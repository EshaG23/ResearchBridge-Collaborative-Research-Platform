import uuid
from django import forms
from django.utils import timezone
from django.core.validators import URLValidator

class ReviewForm(forms.Form):
    action=forms.ChoiceField(choices=[('shortlist','Shortlist'),('remove_shortlist','Remove from shortlist'),
        ('not_selected','Not selected'),('reopen','Reopen review'),('select','Finalize selection')])
    revision=forms.IntegerField(min_value=1)
    request_key=forms.UUIDField()

class MeetingForm(forms.Form):
    request_key=forms.UUIDField(initial=uuid.uuid4,widget=forms.HiddenInput)
    revision=forms.IntegerField(min_value=1,widget=forms.HiddenInput)
    message=forms.CharField(max_length=1000,initial='I would like to meet you regarding this project.',
        widget=forms.Textarea(attrs={'rows':3}))
    scheduled_at=forms.DateTimeField(label='Date and time (IST)',input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M',attrs={'type':'datetime-local'}),
        help_text='India Standard Time (Asia/Kolkata).')
    venue=forms.CharField(max_length=250,help_text='For example, Research Lab 2, or Online meeting.')
    online_url=forms.URLField(required=False,label='Online meeting link (optional)',validators=[URLValidator(schemes=['https'])])
    def clean_scheduled_at(self):
        value=self.cleaned_data['scheduled_at']
        if value<=timezone.now():
            raise forms.ValidationError('Choose a future date and time.')
        return value


class ApplicantFilterForm(forms.Form):
    q=forms.CharField(required=False,max_length=120,label='Student name',widget=forms.TextInput(attrs={'placeholder':'Search submitted applicants'}))
    status=forms.ChoiceField(required=False,choices=[('','All submitted applications'),('submitted','Awaiting review'),('shortlisted','Shortlisted'),('selected','Selected'),('not_selected','Not selected')])
