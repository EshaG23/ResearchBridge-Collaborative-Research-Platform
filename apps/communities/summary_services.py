import hashlib
from pathlib import Path
from zipfile import ZipFile,BadZipFile
from xml.etree import ElementTree
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import F
from apps.core.permissions import require_permission
from apps.projects.models import Project
from apps.documents.security import validate_private_pdf
from .models import Community,CommunityEvent,ProjectSummary,SummarySection,Sprint,SummaryResource
from .permissions import can_edit

SUMMARY_FIELDS=['description','problem','objectives','existing_solutions','research_gap','progress_notes']
SECTION_FIELDS=['title','content','order']
SPRINT_FIELDS=['title','goal','order','start_date','end_date','status','notes']

def lock(user,pk):
    project_id=Community.objects.values_list('project_id',flat=True).get(pk=pk)
    Project.objects.filter(pk=project_id).update(revision=F('revision'))
    community=Community.objects.select_related('project').get(pk=pk)
    require_permission(can_edit(user,community.project))
    return community

def replay(community,user,data,action):
    existing=CommunityEvent.objects.filter(request_key=data['key']).first()
    if existing:
        if existing.community_id!=community.pk or existing.actor_id!=user.pk or existing.action!=action:
            raise ValidationError('This confirmation has already been used for another change.')
        return existing
    if data['revision']!=community.revision:raise ValidationError('The workspace changed in another window. Reload before saving.')

def snapshot(record,fields):
    return {key:(str(getattr(record,key)) if getattr(record,key) is not None else '') for key in fields}

def record_edit(community,user,data,action,before,after,record_id):
    CommunityEvent.objects.create(community=community,actor=user,action=action,request_key=data['key'],details={'record_id':str(record_id),'before':before,'after':after})
    community.revision+=1;community.save(update_fields=['revision'])

@transaction.atomic
def save_text(user,pk,data,kind,record_pk=None):
    community=lock(user,pk)
    if kind not in ('summary','section','sprint'):raise ValidationError('Unknown workspace edit.')
    action=kind+'_saved'
    old=replay(community,user,data,action)
    if old:
        if record_pk is not None and str(record_pk)!=old.details['record_id']:
            raise ValidationError('This confirmation belongs to another record.')
        return old.details['record_id']
    if kind=='summary':
        record=ProjectSummary.objects.filter(community=community).first() or ProjectSummary(community=community,description=community.project.confidential.details)
        fields=SUMMARY_FIELDS
    else:
        model,fields=(SummarySection,SECTION_FIELDS) if kind=='section' else (Sprint,SPRINT_FIELDS)
        record=model.objects.filter(community=community,pk=record_pk).first() if record_pk else model(community=community)
        require_permission(record is not None)
    before=snapshot(record,fields) if not record._state.adding else {}
    for field in fields:setattr(record,field,data[field])
    if kind=='sprint' and record.status=='active' and Sprint.objects.filter(community=community,status='active').exclude(pk=record.pk).exists():
        raise ValidationError('Another sprint is active. Complete it or return it to Planned before starting this sprint.')
    record.full_clean();record.save()
    record_edit(community,user,data,action,before,snapshot(record,fields),record.pk)
    return record.pk

def validate_resource(upload):
    if upload.size>5*1024*1024:raise ValidationError('Upload a file no larger than 5 MB.')
    suffix=Path(upload.name).suffix.lower()
    if suffix=='.pdf':validate_private_pdf(upload);return 'application/pdf'
    if suffix!='.pptx':raise ValidationError('Use PDF or PPTX. Legacy PPT and macro-enabled presentations are not supported.')
    try:
        with ZipFile(upload) as package:
            entries=package.infolist();names={e.filename for e in entries}
            if len(entries)>2000 or sum(e.file_size for e in entries)>50*1024*1024 or any(e.flag_bits&1 for e in entries):raise ValueError
            if not {'[Content_Types].xml','ppt/presentation.xml'}.issubset(names):raise ValueError
            if any('vbaproject' in name.lower() or name.startswith('ppt/embeddings/') for name in names):raise ValueError
            for name in names:
                if name.endswith(('.xml','.rels')):
                    info=package.getinfo(name)
                    if info.file_size>2*1024*1024:raise ValueError
                    xml=package.read(name)
                    if b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():raise ValueError
                    ElementTree.fromstring(xml)
    except (BadZipFile,ValueError,ElementTree.ParseError,RuntimeError,KeyError,OSError):
        raise ValidationError('Upload a readable PPTX without macros or embedded programs.')
    finally:upload.seek(0)
    return 'application/vnd.openxmlformats-officedocument.presentationml.presentation'

def save_resource(user,pk,data):
    stored=None
    try:
        with transaction.atomic():
            community=lock(user,pk);old=replay(community,user,data,'resource_added')
            if old:return old.details['record_id']
            previous=data.get('replaces')
            if previous and (previous.community_id!=community.pk or SummaryResource.objects.filter(replaces=previous).exists()):raise ValidationError('Choose the latest version of a resource in this community.')
            record=SummaryResource(replaces=previous,version=previous.version+1 if previous else 1,revision_note=data.get('revision_note',''),uploader_name=user.profile.name,community=community,title=data['title'],category=data['category'],url=data.get('url',''),added_by=user)
            upload=data.get('file')
            if upload:
                record.mime_type=validate_resource(upload);raw=upload.read();record.size=len(raw);record.sha256=hashlib.sha256(raw).hexdigest()
                record.filename=Path(upload.name.replace('\\','/')).name[:255]
                record.file.save('resource'+Path(record.filename).suffix.lower(),ContentFile(raw),save=False);stored=record.file
            record.full_clean();record.save()
            record_edit(community,user,data,'resource_added',{}, {'title':record.title,'category':record.category,'url':record.url,'filename':record.filename,'sha256':record.sha256},record.pk)
            return record.pk
    except Exception:
        if stored:stored.storage.delete(stored.name)
        raise
