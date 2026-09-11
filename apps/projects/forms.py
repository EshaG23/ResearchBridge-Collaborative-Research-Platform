import uuid
from django import forms
from apps.profiles.models import Department
from apps.profiles.taxonomy import DEPARTMENT_NAMES
from .models import Project

class IdeaForm(forms.ModelForm):
    creation_key = forms.UUIDField(widget=forms.HiddenInput, initial=uuid.uuid4)
    revision = forms.IntegerField(widget=forms.HiddenInput, initial=1, min_value=1)
    confidential_details = forms.CharField(required=False, max_length=20000,
        widget=forms.Textarea(attrs={'rows':8}),
        help_text='Visible only to you and your attached, approved mentor. Keep methods, novel mechanisms and unpublished findings here.')
    class Meta:
        model = Project
        fields = ['title','domain','departments','short_description','skills','open_positions','available_roles']
        labels = {'domain':'Research domain', 'short_description':'Recruitment summary', 'skills':'Required skills',
                  'open_positions':'Open student positions', 'available_roles':'Available roles (optional)'}
        widgets = {'departments':forms.CheckboxSelectMultiple, 'skills':forms.CheckboxSelectMultiple,
                   'short_description':forms.Textarea(attrs={'rows':3, 'maxlength':240})}
        help_texts = {'short_description':'Up to 240 characters. Describe the opportunity without revealing your full idea.',
                      'available_roles':'For example: Python developer, electronics designer, literature researcher.'}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['departments'].queryset = Department.objects.filter(name__in=DEPARTMENT_NAMES)
        if self.instance.pk and not self.instance._state.adding:
            self.initial.update(creation_key=self.instance.creation_key, revision=self.instance.revision,
                                confidential_details=self.instance.confidential.details)

