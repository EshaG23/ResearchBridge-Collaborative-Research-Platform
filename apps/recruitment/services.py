from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from apps.projects.models import Project
from apps.core.permissions import require_permission
from apps.notifications.services import notify
from .permissions import can_apply
from .models import Application

def _clean_old_file(storage,name):
    try:
        storage.delete(name)
    except OSError:
        pass  # An obsolete private draft file must not undo a successful save.

def prepare_application(user,project_pk,data):
    stored=None
    old_file=None
    try:
        with transaction.atomic():
            Project.objects.filter(pk=project_pk).update(revision=F('revision'))
            project=Project.objects.select_related('mentor__profile','creator').get(pk=project_pk)
            require_permission(can_apply(user,project))
            app=Application.objects.filter(project=project,applicant=user).first()
            if app and app.status!='draft':
                return app
            if app:
                old_file=app.uploaded_resume.name
                app.revision+=1
            else:
                app=Application(project=project,applicant=user)
            profile=user.profile
            app.snapshot={'name':profile.name,'email':user.email,'department':str(profile.department),
                'phone':profile.phone,'year':profile.year,'availability':profile.availability,
                'skills':list(profile.skills.values_list('name',flat=True)),
                'interests':list(profile.interests.values_list('name',flat=True))}
            app.motivation=data['motivation']
            app.academic_score=data['academic_score']
            if data['resume_choice']=='profile':
                resume=data['profile_resume']
                require_permission(resume.profile.user_id==user.pk)
                # Missing files should fail before the application is saved.
                with resume.file.open('rb') as stream:
                    stream.read(5)
                app.profile_resume=resume
                app.uploaded_resume=''
                app.resume_name=resume.original_name
            else:
                app.profile_resume=None
                upload=data['uploaded_resume']
                app.resume_name=Path(upload.name).name[:255]
                app.uploaded_resume.save(upload.name,upload,save=False)
                stored=app.uploaded_resume.name
            app.save()
            if old_file and old_file!=app.uploaded_resume.name:
                storage=Application._meta.get_field('uploaded_resume').storage
                transaction.on_commit(lambda: _clean_old_file(storage,old_file))
            return app
    except Exception:
        if stored:
            Application._meta.get_field('uploaded_resume').storage.delete(stored)
        raise

@transaction.atomic
def submit_application(user,pk,revision):
    app=Application.objects.select_related('project').get(pk=pk,applicant=user)
    Project.objects.filter(pk=app.project_id).update(revision=F('revision'))
    app=Application.objects.select_related('project__mentor__profile','project__creator','profile_resume').get(pk=pk,applicant=user)
    if app.status!='draft':
        return app
    require_permission(can_apply(user,app.project))
    if app.revision!=revision:
        raise ValidationError('Your draft changed in another window. Reload and review it before submitting.')
    with app.resume_file.open('rb') as stream:
        stream.read(5)
    app.status='submitted'
    app.submitted_at=timezone.now()
    app.save(update_fields=['status','submitted_at'])
    notify(user,f'application:{app.pk}:submitted','Application submitted',
        'Your application and résumé snapshot have been saved.',app.project)
    notify(app.project.mentor,f'application:{app.pk}:received','New application',
        f'A student applied to {app.project.title}. Open the project to view applications.'[:500],app.project)
    return app
