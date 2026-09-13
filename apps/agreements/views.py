import uuid
from io import BytesIO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.http import FileResponse
from django.shortcuts import get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods,require_GET,require_POST
from django.views.decorators.debug import sensitive_post_parameters
from apps.accounts.services import rate_limit,AuthenticationError
from apps.core.permissions import require_permission
from apps.projects.models import Project
from apps.recruitment.permissions import can_review_applications
from apps.documents.security import private_download
from .models import Agreement,AgreementEvidence
from .forms import SigningForm
from .permissions import eligible_student,can_view_agreement,agreement_gate,selected_application
from .services import context,preview,submit,review,enroll_proposer
from .pdf import agreement_pdf

@login_required
@never_cache
@require_GET
def project(request,pk):
    project=get_object_or_404(Project,pk=pk)
    mentor=can_review_applications(request.user,project)
    selected=selected_application(project,request.user) if request.user.roster_role=='student' else None
    require_permission(mentor or eligible_student(request.user,project) or selected is not None)
    if selected is not None and not eligible_student(request.user,project):
        return render(request,'agreements/pending.html',{'project':project,'application':selected,'page_title':'Agreement: awaiting offer letter'})
    data={'project':project,'is_mentor':mentor,'page_title':'Confidentiality agreements'}
    if mentor:data.update(agreement_gate(project))
    else:
        agreement=Agreement.objects.filter(project=project,student=request.user).first()
        data.update(agreement=agreement,evidence=agreement.latest if agreement else None)
    return render(request,'agreements/project.html',data)

@login_required
@never_cache
@sensitive_post_parameters('password','signature','token')
@require_http_methods(['GET','POST'])
def sign(request,pk):
    project=get_object_or_404(Project,pk=pk)
    require_permission(eligible_student(request.user,project))
    snapshot,token=context(request.user,project)
    agreement=Agreement.objects.filter(project=project,student=request.user).first()
    latest=agreement.latest if agreement else None
    if latest and latest.status!='correction':return redirect('agreements:evidence',pk=latest.pk)
    form=SigningForm(request.POST or None,request.FILES or None,initial={'name':snapshot['student'],'token':token,'method':'drawn'})
    data={'form':form,'snapshot':snapshot,'project':project,'page_title':'Sign your agreement'}
    if request.method=='POST':
        try:
            if request.POST.get('action')=='confirm':
                evidence=submit(request.user,pk,request.POST.get('token',''))
                messages.success(request,'Signature recorded. Your mentor will verify the agreement.')
                return redirect('agreements:evidence',pk=evidence.pk)
            if form.is_valid():
                rate_limit('agreement-password',request.user.email,request.META.get('REMOTE_ADDR','unknown'),8,50)
                if not request.user.check_password(form.cleaned_data['password']):raise ValidationError('The account password is incorrect.')
                payload,confirmation=preview(form.cleaned_data['token'],request.user,project,form.cleaned_data)
                if form.cleaned_data['method']=='physical':
                    evidence=submit(request.user,pk,confirmation,form.cleaned_data['signed_copy'])
                    messages.success(request,'Signed copy submitted for mentor verification.')
                    return redirect('agreements:evidence',pk=evidence.pk)
                data.update(confirmation=confirmation,completion=payload['completion'],snapshot=payload['snapshot'])
        except (ValidationError,AuthenticationError) as exc:form.add_error(None,str(exc) if isinstance(exc,AuthenticationError) else exc)
        except (DatabaseError,OSError):form.add_error(None,'The agreement could not be saved. Please try again.')
    return render(request,'agreements/sign.html',data)

@login_required
@never_cache
@require_GET
def blank(request,pk):
    project=get_object_or_404(Project,pk=pk)
    require_permission(eligible_student(request.user,project))
    snapshot,_=context(request.user,project)
    response=FileResponse(BytesIO(agreement_pdf(snapshot)),as_attachment=True,filename='ResearchBridge-agreement-to-sign.pdf',content_type='application/pdf')
    response['Cache-Control']='private, no-store';response['X-Content-Type-Options']='nosniff';response['Content-Security-Policy']='sandbox'
    return response

@login_required
@never_cache
@require_GET
def evidence(request,pk):
    record=get_object_or_404(AgreementEvidence.objects.select_related('agreement__project','agreement__student'),pk=pk)
    require_permission(can_view_agreement(request.user,record.agreement))
    latest=record.agreement.latest
    return render(request,'agreements/evidence.html',{'record':record,'snapshot':record.snapshot,'page_title':'Agreement record',
        'is_mentor':can_review_applications(request.user,record.agreement.project),'is_latest':latest.pk==record.pk,
        'history':record.agreement.evidence.order_by('-created_at'),'reviews':record.reviews.select_related('actor__profile'),
        'review_key':uuid.uuid4(),'previous':str(record.review.pk) if record.review else ''})

@login_required
@never_cache
@require_GET
def download(request,pk):
    record=get_object_or_404(AgreementEvidence.objects.select_related('agreement__project'),pk=pk)
    require_permission(can_view_agreement(request.user,record.agreement))
    file=record.signed_copy if request.GET.get('file')=='copy' else record.pdf
    require_permission(bool(file))
    return private_download(file,f'ResearchBridge-agreement-{record.pk}.pdf')

@login_required
@never_cache
@require_POST
def verify(request,pk):
    get_object_or_404(AgreementEvidence,pk=pk)
    try:
        if request.POST.get('inspected')!='yes':raise ValidationError('Confirm that you inspected the agreement and signature evidence.')
        key=uuid.UUID(request.POST.get('request_key',''))
        review(request.user,pk,request.POST.get('action'),request.POST.get('reason',''),key,request.POST.get('previous',''))
        messages.success(request,'Agreement review recorded.')
    except (ValueError,ValidationError) as exc:messages.error(request,str(exc))
    except DatabaseError:messages.error(request,'The review could not be saved. Please try again.')
    return redirect('agreements:evidence',pk=pk)

@login_required
@never_cache
@require_POST
def enroll(request,pk):
    project=get_object_or_404(Project,pk=pk);enroll_proposer(request.user,project)
    messages.success(request,'Student proposer included in the intended team. Their agreement is required.')
    return redirect('agreements:project',pk=pk)
