from apps.core.permissions import college_member
from apps.recruitment.permissions import can_review_applications
from apps.recruitment.models import Application
from .models import Agreement

def selected_application(project,student):
    return Application.objects.filter(project=project,applicant=student,status='selected').first()

def eligible_student(user,project):
    if not college_member(user) or user.roster_role!='student':return False
    app=selected_application(project,user)
    if app and hasattr(app,'offer_letter'):return True
    return project.creator_id==user.pk and Agreement.objects.filter(project=project,student=user).exists()

def can_view_agreement(user,agreement):
    return college_member(user) and (agreement.student_id==user.pk or can_review_applications(user,agreement.project))

def roster(project):
    students={a.applicant_id:a.applicant for a in project.applications.filter(status='selected').select_related('applicant__profile')}
    for agreement in project.agreements.select_related('student__profile'):
        students[agreement.student_id]=agreement.student
    rows=[]
    for student in students.values():
        agreement=Agreement.objects.filter(project=project,student=student).first()
        evidence=agreement.latest if agreement else None
        rows.append({'student':student,'agreement':agreement,'evidence':evidence,'status':evidence.status if evidence else 'missing'})
    return rows

def agreement_gate(project):
    rows=roster(project)
    # Never discard unsigned selected students, including a recorded proposer membership.
    return {'rows':rows,'ready':bool(rows) and all(row['status']=='verified' for row in rows)}
