import json
import math
from django import forms
from django.core.exceptions import ValidationError

class SigningForm(forms.Form):
    method=forms.ChoiceField(choices=[('drawn','Draw with mouse or finger'),('typed','Type your full name'),('physical','Upload a physically signed copy')])
    name=forms.CharField(max_length=120,label='Your full name')
    signature=forms.CharField(required=False,widget=forms.HiddenInput)
    signed_copy=forms.FileField(required=False,label='Signed copy (PDF, PNG or JPEG, up to 5 MB)')
    password=forms.CharField(widget=forms.PasswordInput,label='Confirm your account password')
    consent=forms.BooleanField(label='I have read the complete agreement and intentionally sign or submit my signed copy.')
    token=forms.CharField(widget=forms.HiddenInput)
    def clean_signature(self):
        raw=self.cleaned_data.get('signature') or '[]'
        if len(raw)>100000:raise ValidationError('The signature is too large. Clear it and try again.')
        try:
            strokes=json.loads(raw)
            if not isinstance(strokes,list) or len(strokes)>100:raise ValueError
            count=0
            for stroke in strokes:
                if not isinstance(stroke,list):raise ValueError
                count+=len(stroke)
                for point in stroke:
                    if len(point)!=2 or any(type(n) not in (int,float) or not math.isfinite(n) or not 0<=n<=1 for n in point):raise ValueError
            if count>5000:raise ValueError
        except (ValueError,TypeError):raise ValidationError('Draw the signature again.')
        return strokes
    def clean(self):
        data=super().clean()
        if data.get('method')=='drawn':
            points=[p for stroke in data.get('signature',[]) for p in stroke]
            if len(points)<5 or max([p[0] for p in points],default=0)-min([p[0] for p in points],default=0)<.03:
                self.add_error('signature','Draw a visible signature, or choose the typed signature option.')
        if data.get('method')=='physical' and not data.get('signed_copy'):
            self.add_error('signed_copy','Upload your physically signed agreement.')
        return data
