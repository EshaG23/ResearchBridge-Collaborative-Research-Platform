from apps.core.permissions import college_member,approved_teacher
def can_apply(user,project):
    return (college_member(user) and user.roster_role=='student' and project.creator_id!=user.pk
        and project.status=='recruiting' and project.mentor_id is not None
        and approved_teacher(project.mentor) and project.creator.is_demo==user.is_demo)

def can_view_application(user,application):
    return college_member(user) and (application.applicant_id==user.pk or
        (application.status!='draft' and application.project.mentor_id==user.pk and approved_teacher(user)))
