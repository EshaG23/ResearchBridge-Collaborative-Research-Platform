from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def normalise_college_email(value):
    email = (value or "").strip().lower()
    validate_email(email)
    if email.rsplit("@", 1)[1] not in {"rbunagpur.in", "rknec.in"}:
        raise ValidationError("Use your rbunagpur.in or rknec.in college email address.")
    return email

def validate_college_email(value):
    normalise_college_email(value)
