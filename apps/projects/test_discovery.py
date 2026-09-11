from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import timedelta
from apps.projects import tests as fixtures
from apps.profiles.models import Department, Skill, ResearchInterest
from .models import Project

@override_settings(DEBUG=True,AUTHENTICATION_MODE='demo',PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class DiscoveryTests(TestCase):
    setUp=fixtures.ResearchModulesTests.setUp
    user=fixtures.ResearchModulesTests.user
    data=fixtures.ResearchModulesTests.data
    create=fixtures.ResearchModulesTests.create
    pdf=fixtures.ResearchModulesTests.pdf

    def seed(self):
        self.robotics=Department.objects.get(name='ROBOTICS')
        self.cad=Skill.objects.create(name='CAD')
        self.sustainability=ResearchInterest.objects.create(name='Sustainability')
        self.alpha=self.create(self.teacher,title='Alpha air sensor',open_positions=2)
        self.beta=self.create(self.teacher,title='Beta robot',departments=[self.robotics.pk],
            skills=[self.cad.pk],domain=self.sustainability.pk,open_positions=8,
            short_description='Design a campus robot',available_roles='Mechanical designer')
        self.client.force_login(self.student)

    def ids(self,url='/projects/discover/',**params):
        return [p.pk for p in self.client.get(url,params).context['page']]

    def test_default_all_departments_recruiting_only_and_no_private_data(self):
        self.seed()
        self.create(title='Private pending title')
        self.create(self.teacher,title='Private draft title',action='draft')
        closed=self.create(self.teacher,title='Closed title')
        closed.status='closed';closed.save()
        self.client.force_login(self.student)
        for url in ['/dashboard/','/projects/discover/']:
            response=self.client.get(url)
            self.assertSetEqual({p.pk for p in response.context['page']},{self.alpha.pk,self.beta.pk})
            for secret in ['PRIVATE-SENTINEL','Private pending title','Private draft title','Closed title']:
                self.assertNotContains(response,secret)
            self.assertContains(response,'teacher')

    def test_each_filter_and_combination(self):
        self.seed()
        for params in [{'department':self.robotics.pk},{'domain':self.sustainability.pk},{'skill':self.cad.pk},
            {'department':self.robotics.pk,'domain':self.sustainability.pk,'skill':self.cad.pk}]:
            self.assertEqual(self.ids(**params),[self.beta.pk])
        self.assertEqual(self.ids(department=self.dept.pk,skill=self.cad.pk),[])
        self.assertSetEqual(set(self.ids()),{self.alpha.pk,self.beta.pk})

    def test_search_uses_recruitment_only_and_handles_empty_results(self):
        self.seed()
        for term in ['BETA','campus robot','Mechanical designer','  robot  ']:
            self.assertEqual(self.ids(q=term),[self.beta.pk])
        self.assertEqual(self.ids(q='PRIVATE-SENTINEL'),[])
        response=self.client.get('/projects/discover/',{'q':'nothing matches'})
        self.assertContains(response,'No projects match just yet.')
        self.assertContains(response,'Clear filters and browse all')

    def test_sorting_and_tie_breaks(self):
        self.seed()
        Project.objects.filter(pk=self.alpha.pk).update(created_at=timezone.now()-timedelta(days=1))
        self.assertEqual(self.ids(sort='newest'),[self.beta.pk,self.alpha.pk])
        self.assertEqual(self.ids(sort='oldest'),[self.alpha.pk,self.beta.pk])
        self.assertEqual(self.ids(sort='title'),[self.alpha.pk,self.beta.pk])
        self.assertEqual(self.ids(sort='positions'),[self.beta.pk,self.alpha.pk])
        self.assertEqual(self.ids(),self.ids(sort='newest'))

    def test_invalid_filters_do_not_broaden_search(self):
        self.seed()
        for params in [{'department':'not-a-number'},{'domain':'999999'},{'skill':'999999'},
            {'sort':'confidential__details'},{'q':'x'*161}]:
            response=self.client.get('/projects/discover/',params)
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.context['page'].paginator.count,0)
            self.assertContains(response,'Please correct the highlighted filters')

    def test_pagination_keeps_filters_and_no_duplicates(self):
        self.seed()
        self.alpha.departments.add(self.robotics)
        self.alpha.skills.add(self.cad)
        for n in range(13):
            self.create(self.teacher,title=f'Robot {n:02}',departments=[self.robotics.pk],skills=[self.cad.pk])
        self.client.force_login(self.student)
        params={'department':self.robotics.pk,'skill':self.cad.pk,'sort':'title'}
        first=self.client.get('/projects/discover/',params)
        second=self.client.get('/projects/discover/',params|{'page':2})
        self.assertEqual(first.context['page'].paginator.count,15)
        ids1={p.pk for p in first.context['page']}
        ids2={p.pk for p in second.context['page']}
        self.assertEqual(len(ids1),12)
        self.assertEqual(len(ids2),3)
        self.assertFalse(ids1 & ids2)
        self.assertContains(first,'department='+str(self.robotics.pk))
        self.assertContains(first,'skill='+str(self.cad.pk))
        self.assertContains(first,'sort=title')
        self.assertContains(first,'page=2')
        self.assertEqual(self.client.get('/projects/discover/',params|{'page':'invalid'}).context['page'].number,1)

    def test_login_profile_gate_readonly_and_cache(self):
        self.seed()
        self.client.logout()
        self.assertEqual(self.client.get('/projects/discover/').status_code,302)
        self.client.force_login(self.student)
        self.assertEqual(self.client.post('/projects/discover/').status_code,405)
        self.assertIn('no-store',self.client.get('/projects/discover/')['Cache-Control'])
        self.student.profile.completed_at=None;self.student.profile.save()
        self.assertRedirects(self.client.get('/projects/discover/'),'/profile/')

    def test_empty_catalog_and_demo_isolation(self):
        self.assertContains(self.client.get('/projects/discover/'),'No recruitment notices have been published yet')
        real=self.user('real-faculty','teacher')
        real.is_demo=False;real.save()
        project=self.create(real,title='Real private environment')
        self.client.force_login(self.student)
        self.assertNotIn(project.pk,self.ids())
