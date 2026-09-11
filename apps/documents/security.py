from pathlib import Path
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from pypdf import PdfReader

def validate_private_pdf(upload):
    if not upload.name.lower().endswith('.pdf') or upload.size > 5 * 1024 * 1024:
        raise ValidationError('Upload a PDF no larger than 5 MB.')
    try:
        if upload.read(5) != b'%PDF-':
            raise ValueError
        upload.seek(0)
        reader = PdfReader(upload, strict=True)
        if reader.is_encrypted or not 1 <= len(reader.pages) <= 50:
            raise ValueError
    except Exception:
        raise ValidationError('Upload a readable, unencrypted PDF with 1–50 pages.') from None
    finally:
        upload.seek(0)
    return upload

def private_download(field, filename):
    # Resolve against the storage root as defence against corrupt/path-traversal metadata.
    root = Path(field.storage.location).resolve()
    path = Path(field.path).resolve()
    if not path.is_relative_to(root):
        raise Http404
    try:
        response = FileResponse(field.open('rb'), as_attachment=True,
                                filename=Path(filename.replace('\\', '/')).name,
                                content_type='application/pdf')
    except (FileNotFoundError, OSError):
        raise Http404('File unavailable') from None
    response['Cache-Control'] = 'private, no-store, max-age=0'
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "sandbox; default-src 'none'"
    return response

