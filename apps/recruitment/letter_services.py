import hashlib
import uuid
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
import reportlab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone
from apps.core.permissions import require_permission
from apps.notifications.services import notify
from .models import OfferLetter
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

def render_letter(snapshot):
    fontdir=Path(reportlab.__file__).parent/'fonts'
    if 'RBVera' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('RBVera',str(fontdir/'Vera.ttf')))
    body=ParagraphStyle('RBBody',fontName='RBVera',fontSize=10,leading=16,textColor=colors.HexColor('#26384c'),spaceAfter=14)
    title=ParagraphStyle('RBTitle',parent=body,fontSize=26,leading=32,spaceAfter=22)
    small=ParagraphStyle('RBSmall',parent=body,fontSize=8,leading=12,textColor=colors.HexColor('#546579'))
    out=BytesIO()
    doc=SimpleDocTemplate(out,pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=48,
        title='ResearchBridge offer letter',author='ResearchBridge')
    p=lambda text,style=body: Paragraph(escape(str(text)),style)
    story=[p('RESEARCHBRIDGE',small),p('Your next chapter\nstarts with research.',title),
        p('OFFER LETTER / PROJECT SELECTION',small),p('Reference: '+snapshot['reference'],small),p('Issued: '+snapshot['date'],small),Spacer(1,12),
        p('Dear '+snapshot['student']+','),p('You have been selected to join the following research project.')]
    for label,key in [('Student','student'),('University email','email'),('Project','project'),('Selected role','role'),('Mentor','mentor'),('Mentor email','mentor_email')]:
        story.append(p(label+': '+snapshot[key]))
    story.extend([Spacer(1,12),p('What happens next',title),p(snapshot['next_steps']),p('Issued in ResearchBridge by '+snapshot['mentor']+'.'),p(snapshot['identity'],small)])
    def footer(canvas,document):
        canvas.setStrokeColor(colors.HexColor('#64b6a2'));canvas.line(48,35,547,35)
        canvas.setFont('RBVera',8);canvas.drawString(48,22,'ResearchBridge | Private selection record');canvas.drawRightString(547,22,str(document.page))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()

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
