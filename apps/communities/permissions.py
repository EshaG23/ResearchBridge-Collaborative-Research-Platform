from apps.core.permissions import college_member
from apps.recruitment.permissions import can_review_applications
from apps.agreements.models import Agreement
from .models import Community,Membership

def can_enter(user,project):
    if not college_member(user):return False
    community=Community.objects.filter(project=project).first()
    if not community:return False
    if can_review_applications(user,project):return True
    if user.roster_role!='student' or not Membership.objects.filter(community=community,user=user,role='student').exists():return False
    agreement=Agreement.objects.filter(project=project,student=user).first()
    latest=agreement.latest if agreement else None
    return bool(latest and latest.status=='verified')

def can_edit(user,project):
    if not can_enter(user,project):return False
    return can_review_applications(user,project) or project.community.leader_id==user.pk
