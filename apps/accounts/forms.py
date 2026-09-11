from django import forms
from .validators import normalise_college_email

class EmailForm(forms.Form):
    email = forms.EmailField(label='College email address', max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'yourname@rbunagpur.in',
                                      'data-college-email': '', 'aria-describedby': 'id_email_helptext'}),
        help_text='Registered @rbunagpur.in and @rknec.in addresses are accepted.')
    def clean_email(self):
        return normalise_college_email(self.cleaned_data['email'])

class CodeForm(forms.Form):
    code = forms.RegexField(r'^[0-9]{6}$', label='Six-digit code', max_length=6, min_length=6,
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code',
                                     'pattern': '[0-9]{6}', 'placeholder': '000000', 'class': 'otp-input'}),
        error_messages={'invalid': 'Enter the six-digit code.'})


class LoginForm(EmailForm):
    password = forms.CharField(label='Password', strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password'}))
