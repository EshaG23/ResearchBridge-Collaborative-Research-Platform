import uuid
from django import forms
from django.contrib.auth import get_user_model
from apps.communities.permissions import can_enter
from .models import Task,TaskFile

class Confirmation(forms.Form):
    key=forms.UUIDField(initial=uuid.uuid4,widget=forms.HiddenInput)
    revision=forms.IntegerField(initial=1,widget=forms.HiddenInput)

class PersonChoice(forms.ModelChoiceField):
    def label_from_instance(self,obj):return f'{obj.profile.name} ({obj.email})'

class TaskForm(Confirmation,forms.ModelForm):
    assignee=PersonChoice(queryset=get_user_model().objects.none())
    class Meta:
        model=Task
        fields=['title','description','sprint','assignee','due_date','milestone']
        widgets={'description':forms.Textarea(attrs={'rows':5}),'due_date':forms.DateInput(attrs={'type':'date'})}
    def __init__(self,*args,community,**kwargs):
        super().__init__(*args,**kwargs)
        ids=list(community.memberships.values_list('user_id',flat=True))+[community.project.mentor_id]
        users=get_user_model().objects.filter(pk__in=ids).select_related('profile')
        self.fields['assignee'].queryset=get_user_model().objects.filter(pk__in=[u.pk for u in users if can_enter(u,community.project)])
        self.fields['sprint'].queryset=community.sprints.all()
        self.fields['sprint'].label_from_instance=lambda s:s.title

class MultipleInput(forms.ClearableFileInput):allow_multiple_selected=True
class MultipleFiles(forms.FileField):
    def __init__(self,*args,**kwargs):super().__init__(*args,widget=MultipleInput(),**kwargs)
    def clean(self,data,initial=None):return [super(MultipleFiles,self).clean(f,initial) for f in (data if isinstance(data,(list,tuple)) else [data]) if f]

class FileChoice(forms.ModelChoiceField):
    def label_from_instance(self,obj):return f'{obj.filename} · v{obj.version} · {obj.created_at:%d %b %H:%M} · {str(obj.pk)[:8]}'
class EvidenceChoice(forms.ModelMultipleChoiceField):
    label_from_instance=FileChoice.label_from_instance

class WorkForm(Confirmation):
    replaces=FileChoice(queryset=TaskFile.objects.none(),required=False,label='Upload a new version of (optional)')
    revision_note=forms.CharField(max_length=1000,required=False,label='Revision note')
    summary=forms.CharField(max_length=10000,widget=forms.Textarea(attrs={'rows':5}),label='Progress / completed work')
    blocker=forms.CharField(max_length=3000,required=False,widget=forms.Textarea(attrs={'rows':2}),label='Blocker (leave empty when resolved)')
    evidence=EvidenceChoice(queryset=TaskFile.objects.none(),required=False,widget=forms.CheckboxSelectMultiple,label='Existing files to include in this submission')
    uploads=MultipleFiles(required=False,label='New evidence files',help_text='Up to 5 files, 25 MB each, 60 MB total. New files are included automatically.')
    def __init__(self,*args,task,**kwargs):
        super().__init__(*args,**kwargs);self.fields['evidence'].queryset=task.files.all();self.fields['replaces'].queryset=task.files.filter(next_version__isnull=True)

class ReviewForm(Confirmation):
    submission=forms.IntegerField(widget=forms.HiddenInput)
    decision=forms.ChoiceField(choices=[('approved','Approve completed work'),('changes','Request changes')])
    feedback=forms.CharField(max_length=10000,widget=forms.Textarea(attrs={'rows':4}))
class ReopenForm(Confirmation):
    feedback=forms.CharField(max_length=10000,widget=forms.Textarea(attrs={'rows':3}),label='Reason for reopening')
class CommentForm(Confirmation):
    body=forms.CharField(max_length=5000,widget=forms.Textarea(attrs={'rows':3}),label='Comment')
    file=FileChoice(queryset=TaskFile.objects.none(),required=False,label='Discuss a specific file version (optional)')
    def __init__(self,*args,task,**kwargs):
        super().__init__(*args,**kwargs);self.fields['file'].queryset=task.files.all()
