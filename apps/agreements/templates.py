"""Replace via AGREEMENT_TEMPLATE_PATH only after institutional approval."""
import hashlib
import json
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError

CONSENT='I have read this agreement in full, understand its confidentiality obligations, and intentionally submit my signature for this project. I understand that this development template is not college-approved.'
SAMPLE={
    'version':'sample-nda-1','title':'Project confidentiality agreement',
    'identity':'ResearchBridge | Sample development agreement',
    'sample':True,
    'notice':'SAMPLE FOR DEVELOPMENT. This wording and signing process have not been approved by the college. This is an electronic completion record, not a certified digital-signature service.',
    'clauses':[
        ['Purpose and confidential material','For this project, confidential material includes non-public project details, research methods, data, unpublished findings, documents, software and intellectual-property work shared with the student.'],
        ['Use during the project','The student agrees to use confidential material only for authorised project work, protect it with reasonable care, and share it only with people authorised by the project mentor.'],
        ['Leaving the project','The confidentiality obligation continues after leaving or completing the project, including departure due to unforeseen circumstances. On leaving, the student will follow the mentor\'s instructions for returning project material and removing unauthorised copies.'],
        ['Disclosure and incidents','The student will seek mentor approval before public disclosure of confidential project work and promptly report accidental disclosure or loss. Information already public through no breach, independently developed, or lawfully obtained without confidentiality restrictions is excluded.'],
        ['Institutional rules','This sample does not determine intellectual-property ownership or replace college policies. Any required disclosure and applicable institutional requirements must be addressed in the college-approved agreement.'],
    ],'consent':CONSENT}

def current_template():
    path=getattr(settings,'AGREEMENT_TEMPLATE_PATH',None)
    data=json.loads(Path(path).read_text(encoding='utf-8')) if path else SAMPLE
    required={'version','title','identity','sample','notice','clauses','consent'}
    if not required.issubset(data) or not data['clauses']:
        raise ValidationError('The agreement template is incomplete. Contact the project administrator.')
    # Round-trip to detach callers from the versioned template.
    return json.loads(json.dumps(data))

def digest(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
