from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods,require_GET
from apps.core.permissions import require_permission
from apps.documents.security import private_download
from .models import Application,OfferLetter
from .permissions import can_review_applications,can_view_application
from .letter_services import preview_letter,issue_letter

class LetterForm(forms.Form):
    role=forms.CharField(max_length=120,label='Selected role',help_text='Enter the actual role agreed for this student.')

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def issue(request,pk):
    app=get_object_or_404(Application.objects.select_related('project'),pk=pk)
    require_permission(can_review_applications(request.user,app.project) and app.status=='selected')
    existing=OfferLetter.objects.filter(application=app).first()
    if existing:
        return redirect('recruitment:letter',pk=existing.pk)
    form=LetterForm(request.POST if request.method=='POST' else None)
    context={'application':app,'form':form,'page_title':'Issue offer letter'}
    if request.method=='POST':
        try:
            if request.POST.get('confirm')=='issue':
                letter=issue_letter(request.user,pk,request.POST.get('token',''))
                messages.success(request,'Offer letter issued. The student has been notified.')
                return redirect('recruitment:letter',pk=letter.pk)
            if form.is_valid():
                context['letter_data'],context['token']=preview_letter(request.user,app,form.cleaned_data['role'])
        except ValidationError as exc:
            form.add_error(None,exc)
        except (DatabaseError,OSError):
            form.add_error(None,'The letter could not be saved. Please try again.')
    return render(request,'recruitment/letter_issue.html',context)

@login_required
@never_cache
@require_GET
def detail(request,pk):
    letter=get_object_or_404(OfferLetter.objects.select_related('application__project'),pk=pk)
    require_permission(can_view_application(request.user,letter.application))
    return render(request,'recruitment/letter.html',{'letter':letter,'letter_data':letter.snapshot,'page_title':'Your offer letter'})

@login_required
@never_cache
@require_GET
def download(request,pk):
    letter=get_object_or_404(OfferLetter.objects.select_related('application__project'),pk=pk)
    require_permission(can_view_application(request.user,letter.application))
    return private_download(letter.pdf,f'ResearchBridge-offer-{letter.pk}.pdf')
