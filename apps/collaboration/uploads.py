from io import BytesIO
from pathlib import Path
from zipfile import ZipFile,BadZipFile
from PIL import Image
from pypdf import PdfReader
from django.core.exceptions import ValidationError

MAX_FILE=25*1024*1024

def inspect_upload(upload):
    if not upload.size or upload.size>MAX_FILE:raise ValidationError('Each attachment must be non-empty and no larger than 25 MB.')
    name=Path(upload.name.replace('\\','/')).name[:255];ext=Path(name).suffix.lower()
    raw=upload.read();upload.seek(0)
    images={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.gif':'image/gif','.webp':'image/webp'}
    docs={'.pdf':'application/pdf','.doc':'application/msword','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls':'application/vnd.ms-excel','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt':'application/vnd.ms-powerpoint','.pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.txt':'text/plain','.csv':'text/csv','.json':'application/json','.zip':'application/zip'}
    media={'.mp3':('audio','audio/mpeg'),'.wav':('audio','audio/wav'),'.ogg':('audio','audio/ogg'),'.m4a':('audio','audio/mp4'),'.aac':('audio','audio/aac'),'.flac':('audio','audio/flac'),
        '.mp4':('video','video/mp4'),'.mov':('video','video/quicktime'),'.webm':('video','video/webm')}
    try:
        if ext in images:
            img=Image.open(BytesIO(raw))
            if img.width*img.height>40000000 or img.format not in ('JPEG','PNG','GIF','WEBP'):raise ValueError
            detected={'JPEG':'image/jpeg','PNG':'image/png','GIF':'image/gif','WEBP':'image/webp'}[img.format]
            if detected!=images[ext]:raise ValueError
            img.verify();return name,'image',detected,raw
        if ext in docs:
            if ext=='.pdf':
                reader=PdfReader(BytesIO(raw),strict=True)
                if reader.is_encrypted or not 1<=len(reader.pages)<=500:raise ValueError
            elif ext in ('.docx','.xlsx','.pptx','.zip'):
                with ZipFile(BytesIO(raw)) as z:
                    if len(z.infolist())>5000 or sum(i.file_size for i in z.infolist())>150*1024*1024:raise ValueError
                    if ext!='.zip' and '[Content_Types].xml' not in z.namelist():raise ValueError
            elif ext in ('.doc','.xls','.ppt') and not raw.startswith(bytes.fromhex('D0CF11E0A1B11AE1')):raise ValueError
            elif ext in ('.txt','.csv','.json'):raw.decode('utf-8-sig')
            return name,'document',docs[ext],raw
        if ext in media:
            kind,mime=media[ext]
            ok=(ext in ('.mp4','.mov','.m4a') and raw[4:8]==b'ftyp') or (ext=='.webm' and raw.startswith(bytes.fromhex('1A45DFA3'))) or (ext=='.wav' and raw[:4]==b'RIFF' and raw[8:12]==b'WAVE') or (ext=='.ogg' and raw.startswith(b'OggS')) or (ext=='.flac' and raw.startswith(b'fLaC')) or (ext in ('.mp3','.aac') and (raw.startswith(b'ID3') or (len(raw)>1 and raw[0]==255 and raw[1]&224==224)))
            if not ok:raise ValueError
            if ext=='.webm' and upload.content_type=='audio/webm':kind,mime='audio','audio/webm'
            return name,kind,mime,raw
    except Exception:raise ValidationError('An attachment is unreadable or does not match its file type.')
    raise ValidationError('Use a photo, PDF/Office document, text/CSV/JSON/ZIP, MP3/WAV/OGG/M4A/AAC/FLAC audio, or MP4/MOV/WebM video.')
