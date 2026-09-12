import hashlib
import uuid
from io import BytesIO
from datetime import datetime
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from apps.core.permissions import require_permission
from apps.projects.models import Project
from apps.notifications.services import notify
from apps.recruitment.permissions import can_review_applications
from apps.documents.security import validate_private_pdf
from .models import Agreement,AgreementEvidence,AgreementReview
from .permissions import eligible_student,selected_application
from .templates import current_template,digest
from .pdf import agreement_pdf

SALT='agreements.signing.v1'

def context(user,project):
    require_permission(eligible_student(user,project))
    template=current_template();app=selected_application(project,user)
    identity=app.offer_letter.snapshot if app and hasattr(app,'offer_letter') else {'student':user.profile.name,'email':user.email,'project':project.title}
    agreement=Agreement.objects.filter(project=project,student=user).first()
    latest=agreement.latest if agreement else None
    snapshot={'template':template,'template_hash':digest(template),'student':identity['student'],'email':identity['email'],'project':identity['project'],
        'reference':f'NDA-{project.pk.hex.upper()}-{user.pk}'}
    payload={'project':str(project.pk),'user':user.pk,'auth':user.get_session_auth_hash(),'snapshot':snapshot,
        'previous':str(latest.pk) if latest else None,'key':str(uuid.uuid4()),'project_revision':project.revision}
    return snapshot,signing.dumps(payload,salt=SALT,compress=True)

def decode(token,user,project):
    try:data=signing.loads(token,salt=SALT,max_age=900)
    except signing.BadSignature:raise ValidationError('Your signing session expired or changed. Reload the agreement.')
    require_permission(data['user']==user.pk and data['project']==str(project.pk) and data['auth']==user.get_session_auth_hash())
    if data['snapshot']['template_hash']!=digest(current_template()) or data['project_revision']!=project.revision:
        raise ValidationError('The agreement or project changed. Reload and review the latest version.')
    return data

def preview(token,user,project,cleaned):
    data=decode(token,user,project)
    if cleaned['name'].strip().casefold()!=data['snapshot']['student'].strip().casefold():
        raise ValidationError('Enter your full name exactly as shown on this agreement.')
    data['completion']={'name':cleaned['name'].strip(),'method':cleaned['method'],
        'signature':cleaned['signature'] if cleaned['method']=='drawn' else [],'consent':data['snapshot']['template']['consent']}
    return data,signing.dumps(data,salt=SALT,compress=True)

def physical_pdf(upload):
    if upload.size>5*1024*1024:raise ValidationError('Signed copies must be no larger than 5 MB.')
    if upload.name.lower().endswith('.pdf'):
        validate_private_pdf(upload);return upload.read()
    if not upload.name.lower().endswith(('.png','.jpg','.jpeg')):raise ValidationError('Upload a PDF, PNG or JPEG signed copy.')
    try:
        img=Image.open(upload)
        if img.format not in ('PNG','JPEG') or img.width*img.height>20000000:raise ValueError
        img.load();img=img.convert('RGB')
        out=BytesIO();c=canvas.Canvas(out,pagesize=(595.28,841.89));c.drawImage(ImageReader(img),24,24,width=547.28,height=793.89,preserveAspectRatio=True,anchor='c');c.save()
        return out.getvalue()
    except Exception:raise ValidationError('The image cannot be read. Upload a clear PNG or JPEG.')

def submit(user,project_pk,token,upload=None):
    stored=[]
    try:
        with transaction.atomic():
            Project.objects.filter(pk=project_pk).update(revision=F('revision'))
            project=Project.objects.get(pk=project_pk)
            require_permission(eligible_student(user,project))
            data=decode(token,user,project)
            existing=AgreementEvidence.objects.filter(request_key=data['key']).first()
            if existing:return existing
            completion=data.get('completion')
            if not completion:raise ValidationError('Review your signature before submitting.')
            agreement,_=Agreement.objects.get_or_create(project=project,student=user,defaults={'enrolled_by':user,'enrollment_reason':'Selected applicant completing required agreement'})
            latest=agreement.latest
            if (str(latest.pk) if latest else None)!=data['previous']:
                raise ValidationError('A newer agreement submission exists. Reload to see it.')
            if latest and latest.status!='correction':raise ValidationError('This agreement is already submitted. Ask your mentor if a correction is needed.')
            now=timezone.now();pk=uuid.uuid4()
            evidence=AgreementEvidence(id=pk,agreement=agreement,request_key=data['key'],snapshot=data['snapshot'],
                method=completion['method'],name=completion['name'],signature=completion['signature'],consent=completion['consent'],created_at=now)
            if completion['method']=='physical':
                if not upload:raise ValidationError('Upload the signed agreement copy.')
                raw=physical_pdf(upload);evidence.copy_sha256=hashlib.sha256(raw).hexdigest()
                evidence.signed_copy.save('signed-copy.pdf',ContentFile(raw),save=False);stored.append(evidence.signed_copy)
            contents=agreement_pdf(data['snapshot'],completion|{'id':str(pk),'date':timezone.localtime(now).strftime('%d %B %Y, %H:%M:%S IST')})
            evidence.sha256=hashlib.sha256(contents).hexdigest();evidence.pdf.save('evidence.pdf',ContentFile(contents),save=False);stored.append(evidence.pdf);evidence.save()
            app=selected_application(project,user)
            notify(project.mentor,f'agreement:{pk}:submitted','Agreement awaiting verification','A student submitted an agreement. Open the project agreement checklist to review it.',project,application=app)
            return evidence
    except Exception:
        for file in stored:file.storage.delete(file.name)
        raise

@transaction.atomic
def review(user,evidence_pk,action,reason,key,previous):
    evidence=AgreementEvidence.objects.select_related('agreement__project','agreement__student').get(pk=evidence_pk)
    project=evidence.agreement.project
    Project.objects.filter(pk=project.pk).update(revision=F('revision'))
    project.refresh_from_db();require_permission(can_review_applications(user,project))
    if AgreementReview.objects.filter(request_key=key,evidence=evidence,actor=user,action=action).exists():return evidence
    latest=evidence.agreement.latest;last=evidence.review
    if latest.pk!=evidence.pk or (str(last.pk) if last else '')!=previous:raise ValidationError('This record changed. Reload before reviewing.')
    if action not in ('verified','correction') or not reason.strip():raise ValidationError('Choose a review result and enter your verification or correction notes.')
    if action=='verified' and evidence.status!='pending':raise ValidationError('Only pending evidence can be verified. Request a replacement to correct a record.')
    if action=='verified':
        try:
            for file,expected in [(evidence.pdf,evidence.sha256),(evidence.signed_copy,evidence.copy_sha256)]:
                if file:
                    with file.open('rb') as stream:
                        if hashlib.sha256(stream.read()).hexdigest()!=expected:raise OSError
        except OSError:raise ValidationError('The stored evidence is missing or changed. Request a corrected submission.')
    event=AgreementReview.objects.create(evidence=evidence,actor=user,action=action,reason=reason[:1000],request_key=key)
    notify(evidence.agreement.student,f'agreement-review:{event.pk}','Agreement '+('verified' if action=='verified' else 'correction requested'),
        'Open your agreement to view the mentor review.',project,application=selected_application(project,evidence.agreement.student))
    return evidence

@transaction.atomic
def enroll_proposer(user,project):
    Project.objects.filter(pk=project.pk).update(revision=F('revision'));project.refresh_from_db()
    require_permission(can_review_applications(user,project) and project.creator.roster_role=='student')
    agreement,created=Agreement.objects.get_or_create(project=project,student=project.creator,defaults={'enrolled_by':user,'enrollment_reason':'Mentor explicitly included the student proposer in the intended team'})
    if created:notify(project.creator,f'agreement-enrollment:{agreement.pk}','Your team agreement is required','Your mentor included you in the intended student team. Complete the project confidentiality agreement.',project)
    return agreement
