import re
from django import forms
from django.db.models import Q
from .taxonomy import DEPARTMENT_NAMES
from pypdf import PdfReader
from .models import Profile, ResumeVersion, Department

class ProfileForm(forms.ModelForm):
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')], widget=forms.RadioSelect)
    resume = forms.FileField(required=False, label='PDF résumé', widget=forms.FileInput(attrs={'accept': '.pdf,application/pdf'}),
                             help_text='PDF only, up to 5 MB. Each upload is preserved as a new version.')
    availability = forms.IntegerField(required=False, min_value=1, max_value=80, label='Availability (hours per week)')
    year = forms.TypedChoiceField(required=False, coerce=int, empty_value=None,
        choices=[('', 'Choose your year')] + [(n, f'Year {n}') for n in range(1,5)], label='Current year of study')
    class Meta:
        model = Profile
        fields = ['role','name','department','phone','skills','interests','availability','year','previous_research','scholar_url']
        labels = {'interests': 'Research interests', 'scholar_url': 'Google Scholar link', 'previous_research': 'Previous research work'}
        widgets = {'role': forms.RadioSelect, 'skills': forms.CheckboxSelectMultiple,
                   'interests': forms.CheckboxSelectMultiple, 'previous_research': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, draft=False, **kwargs):
        self.draft = draft
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(Q(name__in=DEPARTMENT_NAMES) | Q(pk=self.instance.department_id))
        self.fields['role'].required = True
        if not self.instance.role:
            self.initial['role'] = 'student'
        if self.instance.completed_at:
            self.fields['role'].disabled = True
        for name, field in self.fields.items():
            if name != 'role':
                field.required = False
            field.widget.attrs['aria-describedby'] = f'id_{name}_helptext id_{name}_error'
        self.fields['name'].widget.attrs['autocomplete'] = 'name'
        self.fields['phone'].widget.attrs.update({'autocomplete':'tel', 'inputmode':'tel'})
        self.fields['skills'].help_text = 'Choose all skills that apply.'
        self.fields['interests'].help_text = 'Choose the research areas you are interested in.'

    def clean_phone(self):
        value = self.cleaned_data.get('phone', '').strip()
        compact = re.sub(r'[ ()-]', '', value)
        if value and not re.fullmatch(r'\+?[0-9]{10,15}', compact):
            raise forms.ValidationError('Enter a phone number with 10–15 digits, optionally starting with +.')
        return compact

    def clean_scholar_url(self):
        from urllib.parse import urlparse
        value = self.cleaned_data.get('scholar_url', '')
        if value and urlparse(value).hostname != 'scholar.google.com':
            raise forms.ValidationError('Use a scholar.google.com profile link.')
        return value

    def clean_resume(self):
        upload = self.cleaned_data.get('resume')
        if not upload:
            return None
        if not upload.name.lower().endswith('.pdf') or upload.size > 5*1024*1024:
            raise forms.ValidationError('Upload a PDF no larger than 5 MB.')
        try:
            if upload.read(5) != b'%PDF-':
                raise ValueError
            upload.seek(0)
            reader = PdfReader(upload, strict=True)
            if reader.is_encrypted or not len(reader.pages) or len(reader.pages) > 50:
                raise ValueError
        except Exception:
            raise forms.ValidationError('Upload a readable, unencrypted PDF with 1–50 pages.') from None
        finally:
            upload.seek(0)
        return upload

    def clean(self):
        data = super().clean()
        required = ['name','department','phone','skills','interests']
        if data.get('role') == 'student':
            required += ['availability','year']
            if not self.instance.pk or not self.instance.latest_resume:
                required += ['resume']
        else:
            data['availability'] = None
            data['year'] = None
            if data.get('resume'):
                self.add_error('resume', 'A teacher profile does not require a résumé. Remove this upload.')
        if not self.draft:
            for name in required:
                if not data.get(name) and name not in self.errors:
                    self.add_error(name, 'This field is required to complete your profile.')
        return data
