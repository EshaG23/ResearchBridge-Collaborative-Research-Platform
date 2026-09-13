import uuid
from django import forms
from django.core.validators import URLValidator
from .models import ProjectSummary,SummarySection,Sprint,SummaryResource

class EditFields(forms.Form):
    revision=forms.IntegerField(min_value=1,widget=forms.HiddenInput)
    key=forms.UUIDField(initial=uuid.uuid4,widget=forms.HiddenInput)

class SummaryForm(EditFields,forms.ModelForm):
    class Meta:
        model=ProjectSummary
        fields=['description','problem','objectives','existing_solutions','research_gap','progress_notes']
        labels={'description':'Detailed project description','problem':'Problem statement','progress_notes':'Research progress narrative'}
        widgets={key:forms.Textarea(attrs={'rows':5}) for key in fields}

class SectionForm(EditFields,forms.ModelForm):
    class Meta:
        model=SummarySection
        fields=['title','content','order']
        widgets={'content':forms.Textarea(attrs={'rows':8})}

class SprintForm(EditFields,forms.ModelForm):
    class Meta:
        model=Sprint
        fields=['title','goal','order','start_date','end_date','status','notes']
        widgets={'start_date':forms.DateInput(attrs={'type':'date'}),'end_date':forms.DateInput(attrs={'type':'date'}),
            'goal':forms.Textarea(attrs={'rows':4}),'notes':forms.Textarea(attrs={'rows':5})}
        labels={'notes':'Sprint updates / narrative'}
    def clean(self):
        data=super().clean()
        if data.get('start_date') and data.get('end_date') and data['end_date']<data['start_date']:
            self.add_error('end_date','End date cannot be before start date.')
        return data

class ResourceForm(EditFields):
    replaces=forms.ModelChoiceField(queryset=SummaryResource.objects.none(),required=False,label='New version of existing resource (optional)')
    revision_note=forms.CharField(max_length=1000,required=False)
    def __init__(self,*args,community=None,**kwargs):
        super().__init__(*args,**kwargs)
        if community:self.fields['replaces'].queryset=community.resources.filter(next_version__isnull=True)
        self.fields['replaces'].label_from_instance=lambda r:f'{r.title} - v{r.version}'

    title=forms.CharField(max_length=160)
    category=forms.ChoiceField(choices=SummaryResource._meta.get_field('category').choices)
    url=forms.URLField(max_length=500,required=False,validators=[URLValidator(schemes=['https'])],label='HTTPS reference link')
    file=forms.FileField(required=False,label='PDF or PPTX file (up to 5 MB)')
    def clean(self):
        data=super().clean()
        if bool(data.get('url'))==bool(data.get('file')):raise forms.ValidationError('Provide either a link or a file.')
        return data
