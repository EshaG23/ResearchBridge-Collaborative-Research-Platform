import hashlib,json,sqlite3,shutil
from pathlib import Path
from contextlib import closing

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def verify(source):
    source=Path(source).resolve();manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('format')!=1 or 'db.sqlite3' not in manifest.get('files',{}):raise ValueError('Invalid backup manifest.')
    for relative,expected in manifest['files'].items():
        if Path(relative).is_absolute() or '..' in Path(relative).parts:raise ValueError('Unsafe manifest path.')
        p=(source/relative).resolve()
        if not p.is_relative_to(source) or not p.is_file() or digest(p)!=expected:raise ValueError('Missing, modified or unsafe backup file: '+relative)
    with closing(sqlite3.connect((source/'db.sqlite3').as_uri()+'?mode=ro',uri=True)) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Database integrity check failed.')
    return manifest

def backup(data,destination):
    data=Path(data).resolve();destination=Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(data):raise ValueError('Choose a new backup folder outside the data directory.')
    if not (data/'db.sqlite3').is_file():raise ValueError('Database not found.')
    destination.mkdir(parents=True)
    with closing(sqlite3.connect(data/'db.sqlite3')) as source,closing(sqlite3.connect(destination/'db.sqlite3')) as target:source.backup(target)
    for p in data.rglob('*'):
        relative=p.relative_to(data)
        if 'backups' in relative.parts or p.name.startswith('db.sqlite3') or not p.is_file():continue
        if p.is_symlink() or not p.resolve().is_relative_to(data):raise ValueError('Linked data files are not supported.')
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    files={p.relative_to(destination).as_posix():digest(p) for p in destination.rglob('*') if p.is_file()}
    (destination/'manifest.json').write_text(json.dumps({'format':1,'files':files},indent=2),encoding='utf-8');verify(destination)
    return len(files)

def restore(source,destination):
    source=Path(source).resolve();destination=Path(destination).resolve();manifest=verify(source)
    if destination.exists():raise ValueError('Restore requires a new folder; existing data is never overwritten.')
    destination.mkdir(parents=True)
    for relative,expected in manifest['files'].items():
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/relative,target)
        if digest(target)!=expected:raise ValueError('Restored file checksum failed.')
    return len(manifest['files'])
