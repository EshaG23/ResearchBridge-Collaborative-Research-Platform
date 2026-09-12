from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.shortcuts import get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST,require_http_methods
from apps.core.permissions import require_permission
from .models import Application,MeetingInvitation
from .permissions import can_review_applications
from .review_forms import ReviewForm,MeetingForm
from .review_services import review_application,invite_to_meeting,cancel_meeting

@login_required
@never_cache
@require_POST
def decision(request,pk):
    app=get_object_or_404(Application.objects.select_related('project'),pk=pk)
    require_permission(can_review_applications(request.user,app.project))
    form=ReviewForm(request.POST)
    if form.is_valid():
        try:
            review_application(
                request.user,pk,form.cleaned_data['action'],form.cleaned_data['revision'],form.cleaned_data['request_key'])
        except ValidationError as exc:
            messages.error(request,' '.join(exc.messages))
        except DatabaseError:
            messages.error(request,'Your decision could not be saved. Please try again.')
        else:
            messages.success(request,'Applicant status updated.')
    else:
        messages.error(request,'Invalid decision confirmation. Reload the application and try again.')
    return redirect('recruitment:detail',pk=pk)

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def meeting(request,pk):
    app=get_object_or_404(Application.objects.select_related('project'),pk=pk)
    require_permission(can_review_applications(request.user,app.project) and app.status in ('submitted','shortlisted'))
    form=MeetingForm(request.POST if request.method=='POST' else None,initial={'revision':app.revision})
    if request.method=='POST' and form.is_valid():
        try:
            invite_to_meeting(request.user,pk,form.cleaned_data)
        except ValidationError as exc:
            form.add_error(None,exc)
        except DatabaseError:
            form.add_error(None,'The invitation could not be saved. Please try again.')
        else:
            messages.success(request,'Meeting invitation sent in the app.')
            return redirect('recruitment:detail',pk=pk)
    return render(request,'recruitment/meeting.html',{'page_title':'Invite to a meeting','application':app,'form':form})

@login_required
@never_cache
@require_POST
def cancel(request,pk):
    invite=get_object_or_404(MeetingInvitation.objects.select_related('application__project'),pk=pk)
    require_permission(can_review_applications(request.user,invite.application.project))
    try:
        cancel_meeting(request.user,pk)
    except DatabaseError:
        messages.error(request,'The cancellation could not be saved. Please try again.')
    else:
        messages.success(request,'Meeting cancelled. The applicant has been notified.')
    return redirect('recruitment:detail',pk=invite.application_id)
