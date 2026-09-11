from pathlib import Path
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods, require_GET
from .models import Profile, ResumeVersion
from .forms import ProfileForm

@login_required
@never_cache
@require_http_methods(['GET', 'POST'])
def edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user, defaults={"role": request.user.roster_role})
    draft = request.POST.get('action') == 'draft' and not profile.completed_at
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile, draft=draft)
    if request.method == 'POST' and form.is_valid():
        stored = None
        try:
            with transaction.atomic():
                record = form.save(commit=False)
                if not draft and not record.completed_at:
                    record.completed_at = timezone.now()
                record.save()
                form.save_m2m()
                upload = form.cleaned_data.get('resume')
                if upload:
                    stored = ResumeVersion(profile=record, original_name=Path(upload.name).name[:255])
                    stored.file.save(upload.name, upload, save=False)
                    stored.save()
        except Exception:
            if stored and stored.file:
                stored.file.delete(save=False)
            form.add_error(None, 'Your changes could not be saved. Please try again.')
        else:
            messages.success(request, 'Draft saved. Complete the remaining fields to continue.' if draft else 'Your profile has been saved.')
            return redirect('profiles:edit' if draft else 'dashboard')
    return render(request, 'profiles/edit.html', {'form': form, 'profile': profile,
        'page_title': 'Your profile', 'resume_versions': profile.resumes.order_by('-created_at', '-id')})

@login_required
@never_cache
@require_GET
def resume_download(request, pk):
    from apps.core.permissions import can_view_resume, require_permission
    from apps.documents.security import private_download
    resume = get_object_or_404(ResumeVersion.objects.select_related('profile'), pk=pk)
    require_permission(can_view_resume(request.user, resume))
    return private_download(resume.file, resume.original_name)
