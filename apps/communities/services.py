import uuid
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from apps.projects.models import Project
from apps.core.permissions import require_permission,college_member
from apps.recruitment.permissions import can_review_applications
from apps.agreements.permissions import agreement_gate
from apps.agreements.templates import digest
from apps.notifications.services import notify
from .models import Community,Membership,CommunityEvent
from .permissions import can_enter

SALT='community-roster.v1'

def checklist(project):
    data=agreement_gate(project)
    for row in data['rows']:
        row['active']=college_member(row['student']) and row['student'].roster_role=='student'
    data['ready']=data['ready'] and all(r['active'] for r in data['rows'])
    data['fingerprint']=digest({'revision':project.revision,'rows':sorted((str(r['student'].pk),str(r['evidence'].pk) if r['evidence'] else '',r['status'],r['active']) for r in data['rows'])})
    return data

def confirmation(user,project):
    data=checklist(project)
    return signing.dumps({'user':user.pk,'project':str(project.pk),'fingerprint':data['fingerprint']},salt=SALT)

@transaction.atomic
def create_or_sync(user,pk,token,sync=False):
    Project.objects.filter(pk=pk).update(revision=F('revision'))
    project=Project.objects.get(pk=pk)
    require_permission(can_review_applications(user,project))
    existing=Community.objects.filter(project=project).first()
    if existing and not sync:return existing
    try:confirmed=signing.loads(token,salt=SALT,max_age=900)
    except signing.BadSignature:raise ValidationError('The checklist expired. Reload before confirming.')
    data=checklist(project)
    if confirmed!={'user':user.pk,'project':str(pk),'fingerprint':data['fingerprint']}:
        raise ValidationError('The intended team or agreement status changed. Review the checklist again.')
    if not data['ready']:raise ValidationError('Every intended student must have a verified agreement and an active, complete student account.')
    community=existing or Community.objects.create(project=project,created_by=user)
    Membership.objects.get_or_create(community=community,user=user,defaults={'role':'mentor'})
    added=[]
    for row in data['rows']:
        member,created=Membership.objects.get_or_create(community=community,user=row['student'],defaults={'role':'student','admitted_evidence':row['evidence']})
        if created:
            added.append(row['student'].pk)
            notify(row['student'],f'community:{community.pk}:member:{row["student"].pk}','Your private project community is ready','Your mentor has opened the community. Visit the project to enter your team workspace.',project)
    if not existing or added:
        CommunityEvent.objects.create(community=community,actor=user,action='members_added' if existing else 'community_created',details={'student_ids':added,'mentor_id':user.pk},request_key=uuid.uuid4())
        if existing:community.revision+=1;community.save(update_fields=['revision'])
    return community

@transaction.atomic
def appoint_leader(user,pk,student_id,revision,key):
    community=Community.objects.select_related('project').get(pk=pk)
    Project.objects.filter(pk=community.project_id).update(revision=F('revision'))
    community.refresh_from_db();community.project.refresh_from_db()
    require_permission(can_review_applications(user,community.project))
    event=CommunityEvent.objects.filter(request_key=key).first()
    if event:
        if event.community_id!=community.pk or event.actor_id!=user.pk or event.details.get('new_leader')!=student_id:raise ValidationError('This confirmation was already used.')
        return community
    if community.revision!=revision:raise ValidationError('The team changed. Reload before appointing a leader.')
    member=Membership.objects.filter(community=community,user_id=student_id,role='student').select_related('user').first()
    if not member or not can_enter(member.user,community.project):raise ValidationError('Choose an active student member with a verified agreement.')
    if community.leader_id==student_id:return community
    old=community.leader_id;community.leader_id=student_id;community.revision+=1;community.save(update_fields=['leader','revision'])
    event=CommunityEvent.objects.create(community=community,actor=user,action='leader_appointed',details={'old_leader':old,'new_leader':student_id,'leader_name':member.user.profile.name},request_key=key)
    notify(member.user,f'community-leader:{event.pk}','You are the project team leader','Your mentor appointed you as team leader for this project.',community.project)
    return community
