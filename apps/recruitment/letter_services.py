import hashlib
import uuid
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from apps.core.permissions import require_permission
from apps.notifications.services import notify
from .models import OfferLetter
from .letter_pdf import render_letter
from .permissions import can_review_applications
from .review_services import lock_application

SALT='recruitment.offer-preview.v1'
NEXT_STEPS=('Complete the mandatory confidentiality agreement before accessing private project content. '
    'Private community access follows valid agreement completion and the mentor creating the project community. '
    'This letter communicates your selection; no separate offer acceptance or decline is required.')
IDENTITY='ResearchBridge project selection record. Institutional letterhead and signatures have not been supplied.'

def preview_letter(user,app,role):
    require_permission(can_review_applications(user,app.project) and app.status=='selected')
    role=role.strip()
    if not role or len(role)>120:
        raise ValidationError('Enter a selected role of up to 120 characters.')
    identifier=uuid.uuid4()
    now=timezone.now()
    snapshot={'version':1,'reference':f'RB-{identifier.hex.upper()}',
        'student':app.snapshot['name'],'email':app.snapshot['email'],
        'project':app.project.title,'role':role,'mentor':user.profile.name,
        'mentor_email':user.email,'date':timezone.localtime(now).strftime('%d %B %Y, %H:%M IST'),
        'next_steps':NEXT_STEPS,'identity':IDENTITY}
    payload={'id':str(identifier),'app':str(app.pk),'actor':user.pk,'revision':app.revision,
        'project_revision':app.project.revision,'issued_at':now.isoformat(),'snapshot':snapshot}
    return snapshot,signing.dumps(payload,salt=SALT,compress=True)


def issue_letter(user,pk,token):
    stored=None
    try:
        with transaction.atomic():
            app=lock_application(pk)
            require_permission(can_review_applications(user,app.project) and app.status=='selected')
            try:
                data=signing.loads(token,salt=SALT,max_age=1800)
            except signing.BadSignature:
                raise ValidationError('The preview expired or is invalid. Create a fresh preview.')
            if data['app']!=str(app.pk) or data['actor']!=user.pk:
                raise ValidationError('This preview belongs to a different application or mentor.')
            existing=OfferLetter.objects.filter(application=app).first()
            if existing:
                return existing
            if data['revision']!=app.revision or data['project_revision']!=app.project.revision:
                raise ValidationError('The application or project changed. Create a fresh preview.')
            content=render_letter(data['snapshot'])
            letter=OfferLetter(id=uuid.UUID(data['id']),application=app,issued_by=user,
                issued_at=data['issued_at'],snapshot=data['snapshot'],sha256=hashlib.sha256(content).hexdigest())
            letter.pdf.save('letter.pdf',ContentFile(content),save=False)
            stored=letter.pdf
            letter.save()
            notify(app.applicant,f'offer-letter:{letter.pk}','Your offer letter is ready',
                'You have been selected. Open your application to view your private offer letter and next steps.',
                app.project,application=app)
            return letter
    except Exception:
        if stored:
            stored.storage.delete(stored.name)
        raise
