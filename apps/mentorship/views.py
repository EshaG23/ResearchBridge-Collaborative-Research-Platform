from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.shortcuts import get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET,require_http_methods
from apps.core.permissions import college_member,approved_teacher,require_permission
from apps.projects.models import Project
from .models import MentorSearch,MentorRequest
from .services import rank_mentors,start_search,decide

class ChoiceForm(forms.Form):
    teacher=forms.IntegerField(min_value=1,widget=forms.HiddenInput)
class DecisionForm(forms.Form):
    action=forms.ChoiceField(choices=[('accept','Accept'),('reject','Decline')])
    revision=forms.IntegerField(min_value=1)

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def suggestions(request,pk):
    project=get_object_or_404(Project.objects.select_related('creator','domain'),pk=pk)
    require_permission(college_member(request.user) and request.user.roster_role=='student' and project.creator_id==request.user.pk)
    error=None
    if request.method=='POST':
        form=ChoiceForm(request.POST)
        if form.is_valid():
            try:
                start_search(request.user,pk,form.cleaned_data['teacher'])
            except ValidationError as exc:
                error=' '.join(exc.messages)
            except DatabaseError:
                error='Your request could not be saved. Please try again.'
            else:
                messages.success(request,'Your mentor request is saved.')
                return redirect('mentorship:suggestions',pk=pk)
        else:
            error='Select an eligible teacher from the list.'
    search=MentorSearch.objects.filter(project=project).first()
    candidates=rank_mentors(project) if not search and not project.mentor_id else []
    return render(request,'mentorship/suggestions.html',{'page_title':'Find a mentor','project':project,
        'search':search,'candidates':candidates,'error':error,
        'requests':search.requests.select_related('teacher__profile') if search else [],
        'can_request':project.status=='pending_mentor' and not project.mentor_id})

@login_required
@never_cache
@require_GET
def inbox(request):
    require_permission(approved_teacher(request.user),conceal=False)
    rows=MentorRequest.objects.filter(teacher=request.user,sent_at__isnull=False).select_related('search__project__creator__profile')
    return render(request,'mentorship/inbox.html',{'page_title':'Mentor requests',
        'page':Paginator(rows.order_by('-sent_at'),20).get_page(request.GET.get('page'))})

@login_required
@never_cache
@require_http_methods(['GET','POST'])
def review(request,pk):
    candidate=get_object_or_404(MentorRequest.objects.select_related('search__project__creator__profile',
        'search__project__domain'),pk=pk,teacher=request.user,sent_at__isnull=False)
    require_permission(approved_teacher(request.user))
    project=candidate.search.project
    error=None
    if request.method=='POST':
        form=DecisionForm(request.POST)
        if form.is_valid():
            try:
                decide(request.user,pk,form.cleaned_data['action'],form.cleaned_data['revision'])
            except ValidationError as exc:
                error=' '.join(exc.messages)
            except DatabaseError:
                error='Your decision could not be saved. Please try again.'
            else:
                messages.success(request,'Your decision has been saved.')
                return redirect('mentorship:inbox')
        else:
            error='Choose a valid decision.'
    # Former recipients keep decision history, but lose unpublished project details.
    visible=candidate.state=='pending' or project.status in ('recruiting','closed')
    return render(request,'mentorship/review.html',{'page_title':'Review mentor request','candidate':candidate,
        'project':project,'show_details':visible,'error':error})
