from django import forms
from apps.profiles.models import ResumeVersion
from apps.documents.security import validate_private_pdf

class ApplicationForm(forms.Form):
    resume_choice=forms.ChoiceField(choices=[('profile','Use a saved profile résumé'),('upload','Upload a different PDF')],
        widget=forms.RadioSelect,initial='profile',label='Résumé source')
    profile_resume=forms.ModelChoiceField(queryset=ResumeVersion.objects.none(),required=False,label='Saved résumé')
    uploaded_resume=forms.FileField(required=False,label='Different PDF résumé',
        widget=forms.FileInput(attrs={'accept':'.pdf'}),help_text='PDF · Up to 5 MB · Does not replace your profile résumé.')
    motivation=forms.CharField(max_length=3000,widget=forms.Textarea(attrs={'rows':5}),label='Why would you like to join?')
    academic_score=forms.CharField(max_length=40,required=False,label='Academic score and scale (optional)',
        help_text='For example, 8.2/10. Enter this yourself; no score is inferred.')
    def __init__(self,*args,user,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['profile_resume'].queryset=ResumeVersion.objects.filter(profile__user=user).order_by('-created_at')
        self.fields['profile_resume'].label_from_instance=lambda obj: f'{obj.original_name} · {obj.created_at:%d %b %Y, %H:%M}'
        self.initial['profile_resume']=user.profile.latest_resume
    def clean_uploaded_resume(self):
        value=self.cleaned_data.get('uploaded_resume')
        return validate_private_pdf(value) if value else None
    def clean(self):
        data=super().clean()
        if data.get('resume_choice')=='profile':
            if not data.get('profile_resume'):
                self.add_error('profile_resume','Choose one of your saved résumés.')
            if data.get('uploaded_resume'):
                self.add_error('uploaded_resume','Choose the upload option to use this file.')
        elif data.get('resume_choice')=='upload' and not data.get('uploaded_resume'):
            self.add_error('uploaded_resume','Upload the PDF you want to submit.')
        return data
