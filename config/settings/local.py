from .base import *  # noqa: F403
from django.core.management.utils import get_random_secret_key

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
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
