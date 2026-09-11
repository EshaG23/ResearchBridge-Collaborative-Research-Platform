import hashlib
from pathlib import Path
from django.db import transaction
from django.db.models import F, Max
from apps.core.permissions import can_manage_project, require_permission
from .models import ProjectDocument, DocumentVersion
from .security import validate_private_pdf

def upload_document(user, project, title, upload, document=None):
    require_permission(can_manage_project(user, project))
    if document is not None:
        require_permission(document.project_id == project.pk)
    validate_private_pdf(upload)
    saved = None
    try:
        with transaction.atomic():
            type(project).objects.filter(pk=project.pk).update(revision=F('revision')+1)
            if document is None:
                document = ProjectDocument.objects.create(project=project,title=title)
            number = (document.versions.aggregate(n=Max('version'))['n'] or 0) + 1
            digest = hashlib.sha256()
            for chunk in upload.chunks():
                digest.update(chunk)
            upload.seek(0)
            saved = DocumentVersion(document=document,version=number,uploader=user,
                original_name=Path(upload.name.replace('\\','/')).name[:255],size=upload.size,sha256=digest.hexdigest())
            saved.file.save(upload.name,upload,save=False)
            saved.save()
    except Exception:
        if saved and saved.file:
            saved.file.delete(save=False)
        raise
    return saved

