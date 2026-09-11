from .base import *  # noqa: F403
from django.core.management.utils import get_random_secret_key

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
AUTHENTICATION_MODE = os.environ.get('RESEARCHBRIDGE_AUTH_MODE', 'demo')
if AUTHENTICATION_MODE == 'demo':
    DATA_DIR = BASE_DIR / 'private' / 'demo'
    DATABASES['default']['NAME'] = DATA_DIR / 'db.sqlite3'
    MEDIA_ROOT = DATA_DIR / 'uploads'
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
if not SECRET_KEY:
    secret_file = DATA_DIR / ".development-secret"
    try:
        with secret_file.open("x", encoding="utf-8") as stream:
            stream.write(get_random_secret_key())
    except FileExistsError:
        pass
    SECRET_KEY = secret_file.read_text(encoding="utf-8").strip()
