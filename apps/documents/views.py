from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.cache import never_cache
from apps.core.permissions import can_manage_project, can_view_confidential, require_permission
from apps.projects.models import Project
from .models import ProjectDocument, DocumentVersion
from .forms import DocumentForm
from .services import upload_document
from .security import private_download

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def upload(request, project_pk, document_pk=None):
    project = get_object_or_404(Project,pk=project_pk)
    require_permission(can_manage_project(request.user,project))
    document = get_object_or_404(ProjectDocument,pk=document_pk,project=project) if document_pk else None
    form = DocumentForm(request.POST if request.method == 'POST' else None, request.FILES or None,
                        initial={'title':document.title if document else ''})
    if document:
        form.fields['title'].disabled = True
    if request.method == 'POST' and form.is_valid():
        try:
            upload_document(request.user,project,form.cleaned_data['title'],form.cleaned_data['file'],document)
        except Exception:
            form.add_error(None,'The file could not be saved. Please try again.')
        else:
            messages.success(request,'Private document saved. Earlier versions are preserved.')
            return redirect('projects:private',pk=project.pk)
    return render(request,'documents/upload.html',{'page_title':'Upload private document','project':project,'form':form,'document':document})

@login_required
@never_cache
@require_GET
def download(request, project_pk, pk):
    version = get_object_or_404(DocumentVersion.objects.select_related('document__project'),pk=pk,document__project_id=project_pk)
    require_permission(can_view_confidential(request.user,version.document.project))
    return private_download(version.file,version.original_name)

