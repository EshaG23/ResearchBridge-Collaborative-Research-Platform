from django.test import TestCase, override_settings, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from apps.projects.tests import ResearchModulesTests
from apps.projects.models import Project
from apps.notifications.models import Notification
from apps.profiles.models import Skill
from apps.core.permissions import can_view_project, can_view_confidential
from .models import MentorSearch, MentorRequest
from .services import rank_mentors, start_search, decide

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class MentorshipTests(TestCase):
    setUp=ResearchModulesTests.setUp
    user=ResearchModulesTests.user
    data=ResearchModulesTests.data
    create=ResearchModulesTests.create
    pdf=ResearchModulesTests.pdf

    def prepare(self):
        self.project=self.create()
        self.teacher.profile.department=self.dept
        self.teacher.profile.save()
        self.teacher.profile.skills.add(self.skill)
        self.teacher.profile.interests.add(self.domain)
        self.second=self.user('second','teacher')
        return self.project

    def start(self):
        self.prepare()
        return start_search(self.student,self.project.pk,self.teacher.pk)

    def test_scoring_ranking_reasons_and_eligibility(self):
        self.prepare()
        self.user('unapproved','teacher',False)
        inactive=self.user('inactive','teacher')
        inactive.is_active=False;inactive.save()
        incomplete=self.user('incomplete','teacher')
        incomplete.profile.completed_at=None;incomplete.profile.save()
        real=self.user('real','teacher')
        real.is_demo=False;real.save()
        ranked=rank_mentors(self.project)
        self.assertEqual([r['teacher'].pk for r in ranked],[self.teacher.pk,self.second.pk])
        self.assertEqual([r['score'] for r in ranked],[100,0])
        self.assertIn('Shared skills: Python',ranked[0]['reasons'])
        self.assertEqual(rank_mentors(self.project)[0]['teacher'].pk,self.teacher.pk)
        extra=Skill.objects.create(name='CAD')
        self.project.skills.add(extra)
        self.assertEqual(rank_mentors(self.project)[0]['score'],85)

    def test_chosen_teacher_first_remaining_ranked_and_no_broadcast(self):
        self.prepare()
        third=self.user('third','teacher')
        search=start_search(self.student,self.project.pk,self.second.pk)
        rows=list(search.requests.all())
        self.assertEqual(rows[0].teacher,self.second)
        self.assertEqual(rows[1].teacher,self.teacher)
        self.assertEqual(rows[2].teacher,third)
        self.assertEqual([r.state for r in rows],['pending','queued','queued'])
        self.assertEqual(Notification.objects.filter(recipient=self.second,title='Mentor request').count(),1)
        self.assertFalse(Notification.objects.filter(recipient=self.teacher).exists())
        self.assertEqual(start_search(self.student,self.project.pk,self.teacher.pk).pk,search.pk)
        self.assertEqual(MentorSearch.objects.count(),1)
        self.assertEqual(MentorRequest.objects.filter(state='pending').count(),1)

    def test_only_current_recipient_can_view_recruitment_never_private(self):
        search=self.start()
        current=search.requests.get(state='pending')
        for user,expected in [(self.teacher,200),(self.second,404),(self.other,404)]:
            self.client.force_login(user)
            response=self.client.get(reverse('projects:detail',args=[self.project.pk]))
            self.assertEqual(response.status_code,expected)
            self.assertNotContains(response,'PRIVATE-SENTINEL',status_code=expected)
            self.assertEqual(self.client.get(reverse('projects:private',args=[self.project.pk])).status_code,404)
            self.assertEqual(self.client.get(reverse('projects:edit',args=[self.project.pk])).status_code,404)
        self.client.force_login(self.teacher)
        response=self.client.get(reverse('mentorship:review',args=[current.pk]))
        self.assertContains(response,'Accept mentorship')
        self.assertNotContains(response,'PRIVATE-SENTINEL')
        self.assertContains(self.client.get('/notifications/'),'View idea')
        self.client.force_login(self.second)
        self.assertNotContains(self.client.get('/mentorship/'),self.project.title)
        self.assertEqual(self.client.get(reverse('mentorship:review',args=[current.pk])).status_code,404)

    def test_reject_advances_once_and_revokes_draft_access(self):
        search=self.start()
        current=search.requests.get(state='pending')
        self.project.refresh_from_db()
        decide(self.teacher,current.pk,'reject',self.project.revision)
        following=search.requests.get(state='pending')
        self.assertEqual(following.teacher,self.second)
        decide(self.teacher,current.pk,'reject',self.project.revision)
        self.assertEqual(search.requests.filter(state='pending').count(),1)
        self.assertEqual(Notification.objects.filter(recipient=self.second,title='Mentor request').count(),1)
        self.assertFalse(can_view_project(self.teacher,self.project))
        with self.assertRaises(ValidationError):
            decide(self.teacher,current.pk,'accept',self.project.revision)

    def test_accept_attaches_mentor_publishes_and_preserves_proposer(self):
        search=self.start()
        current=search.requests.get(state='pending')
        self.project.refresh_from_db()
        revision=self.project.revision
        decide(self.teacher,current.pk,'accept',revision)
        decide(self.teacher,current.pk,'accept',revision)
        self.project.refresh_from_db();search.refresh_from_db()
        self.assertEqual(self.project.creator,self.student)
        self.assertEqual(self.project.mentor,self.teacher)
        self.assertEqual(self.project.status,'recruiting')
        self.assertEqual(search.state,'accepted')
        self.assertFalse(search.requests.filter(state='pending').exists())
        self.assertEqual(search.requests.get(teacher=self.second).state,'skipped')
        self.assertTrue(can_view_confidential(self.teacher,self.project))
        self.assertFalse(can_view_confidential(self.second,self.project))
        self.assertEqual(Notification.objects.filter(recipient=self.student,title='Mentor accepted').count(),1)
        self.client.force_login(self.teacher)
        self.assertContains(self.client.get('/projects/'),self.project.title)

    def test_exhaustion_and_skip_ineligible_queued_candidates(self):
        search=self.start()
        self.second.profile.teacher_approved=False;self.second.profile.save()
        current=search.requests.get(state='pending')
        self.project.refresh_from_db()
        decide(self.teacher,current.pk,'reject',self.project.revision)
        search.refresh_from_db();self.project.refresh_from_db()
        self.assertEqual(search.state,'exhausted')
        self.assertIsNone(self.project.mentor)
        self.assertEqual(self.project.status,'pending_mentor')
        self.assertEqual(search.requests.get(teacher=self.second).state,'skipped')
        self.assertFalse(search.requests.filter(state='pending').exists())
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('mentorship:suggestions',args=[self.project.pk])),'No remaining candidate')

    def test_all_rejections_end_without_false_acceptance(self):
        search=self.start()
        self.project.refresh_from_db()
        first=search.requests.get(state='pending')
        decide(self.teacher,first.pk,'reject',self.project.revision)
        second=search.requests.get(state='pending')
        decide(self.second,second.pk,'reject',self.project.revision)
        search.refresh_from_db()
        self.assertEqual(search.state,'exhausted')
        self.assertEqual(search.requests.filter(state='rejected').count(),2)

    def test_invalid_start_actions_and_unauthorised_writes(self):
        self.prepare()
        url=reverse('mentorship:suggestions',args=[self.project.pk])
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(url,{'teacher':self.teacher.pk}).status_code,404)
        self.client.force_login(self.student)
        self.assertContains(self.client.post(url,{'teacher':self.other.pk}),'no longer eligible')
        self.project.status='draft';self.project.save()
        self.assertContains(self.client.post(url,{'teacher':self.teacher.pk}),'Save your student idea')
        self.assertFalse(MentorSearch.objects.exists())

    def test_no_candidates_and_teacher_created_idea(self):
        self.project=self.create()
        self.teacher.profile.teacher_approved=False;self.teacher.profile.save()
        self.assertContains(self.client.get(reverse('mentorship:suggestions',args=[self.project.pk])),'No eligible faculty profiles yet')
        self.teacher.profile.teacher_approved=True;self.teacher.profile.save()
        teacher_project=self.create(self.teacher)
        self.assertEqual(self.client.get(reverse('mentorship:suggestions',args=[teacher_project.pk])).status_code,404)

    def test_stale_review_and_approval_revocation(self):
        search=self.start()
        current=search.requests.get(state='pending')
        self.project.refresh_from_db()
        with self.assertRaises(ValidationError):
            decide(self.teacher,current.pk,'accept',self.project.revision-1)
        self.teacher.profile.teacher_approved=False;self.teacher.profile.save()
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.post(reverse('mentorship:review',args=[current.pk]),
            {'action':'accept','revision':self.project.revision}).status_code,404)
        self.project.refresh_from_db()
        self.assertIsNone(self.project.mentor)

    def test_post_csrf_and_only_one_pending_database_constraint(self):
        search=self.start()
        current=search.requests.get(state='pending')
        strict=Client(enforce_csrf_checks=True)
        strict.force_login(self.teacher)
        self.assertEqual(strict.post(reverse('mentorship:review',args=[current.pk]),{'action':'accept','revision':1}).status_code,403)
        with self.assertRaises(IntegrityError),transaction.atomic():
            search.requests.filter(state='queued').update(state='pending')
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('mentorship:review',args=[current.pk])).status_code,200)
        current.refresh_from_db()
        self.assertEqual(current.state,'pending')

    def test_transaction_rollback_preserves_pending_request_and_no_notifications(self):
        from unittest.mock import patch
        from django.db import DatabaseError
        search=self.start()
        current=search.requests.get(state='pending')
        self.project.refresh_from_db()
        count=Notification.objects.count()
        with patch('apps.mentorship.services.notify',side_effect=DatabaseError('failed')):
            with self.assertRaises(DatabaseError):
                decide(self.teacher,current.pk,'accept',self.project.revision)
        self.project.refresh_from_db();current.refresh_from_db();search.refresh_from_db()
        self.assertIsNone(self.project.mentor)
        self.assertEqual(current.state,'pending')
        self.assertEqual(search.state,'pending')
        self.assertEqual(Notification.objects.count(),count)

    def test_browser_post_routes_and_request_history_survive_logout(self):
        self.prepare()
        self.client.post(reverse('mentorship:suggestions',args=[self.project.pk]),{'teacher':self.teacher.pk})
        candidate=MentorRequest.objects.get(state='pending')
        self.client.post('/accounts/logout/')
        self.client.post('/accounts/login/',{'email':self.teacher.email,'password':'Testing!2026'})
        self.assertContains(self.client.get('/mentorship/'),'Review request')
        self.project.refresh_from_db()
        response=self.client.post(reverse('mentorship:review',args=[candidate.pk]),
            {'action':'accept','revision':self.project.revision})
        self.assertRedirects(response,'/mentorship/')
        self.assertContains(self.client.get('/mentorship/'),'Accepted')
