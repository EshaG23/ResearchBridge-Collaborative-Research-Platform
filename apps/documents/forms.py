from django import forms
from .security import validate_private_pdf
class DocumentForm(forms.Form):
    title = forms.CharField(max_length=160)
    file = forms.FileField(label='Private PDF',help_text='PDF only · Up to 5 MB · 1–50 pages',
        widget=forms.FileInput(attrs={'accept':'.pdf'}))
    def clean_file(self):
        return validate_private_pdf(self.cleaned_data['file'])

