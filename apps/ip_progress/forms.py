import uuid
from django import forms
from django.utils import timezone
from .models import IPUpdate,Achievement

class Confirmation(forms.Form):
    key=forms.UUIDField(initial=uuid.uuid4,widget=forms.HiddenInput)
    revision=forms.IntegerField(initial=1,widget=forms.HiddenInput)

class CompletionForm(Confirmation):
    note=forms.CharField(max_length=10000,widget=forms.Textarea(attrs={'rows':5}),label='Final work / reason')
    confirm=forms.BooleanField(label='I confirm this action and the information above.')

class IPForm(Confirmation,forms.ModelForm):
    class Meta:
        model=IPUpdate
        fields=['title','status_label','message','required_information','reference','task','file']
        widgets={'message':forms.Textarea(attrs={'rows':5}),'required_information':forms.Textarea(attrs={'rows':3})}
        labels={'status_label':'Status label (e.g. prepared, submitted, under review or granted)','file':'Supporting attachment (optional, up to 25 MB)'}
    def __init__(self,*args,community,**kwargs):
        super().__init__(*args,**kwargs);self.fields['task'].queryset=community.tasks.all();self.fields['task'].label_from_instance=lambda t:t.title

class AchievementForm(Confirmation,forms.ModelForm):
    confirm=forms.BooleanField(label='I approve only this text for the shared college dashboard and confirm it contains no confidential information.')
    class Meta:
        model=Achievement
        fields=['title','status_label','public_summary','milestone_date']
        widgets={'public_summary':forms.Textarea(attrs={'rows':4}),'milestone_date':forms.DateInput(attrs={'type':'date'})}
    def clean_milestone_date(self):
        date=self.cleaned_data['milestone_date']
        if date>timezone.localdate():raise forms.ValidationError('Use the date of an actual milestone, not a future achievement.')
        return date
