"""Load private hosted configuration consistently for WSGI and management commands."""
import json
import os
from pathlib import Path


def configure():
    path = Path.home() / '.researchbridge.json'
    values = json.loads(path.read_text(encoding='utf-8'))
    allowed = {'DJANGO_SECRET_KEY', 'DJANGO_ALLOWED_HOSTS', 'RESEARCHBRIDGE_DATA_DIR',
               'SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'SMTP_FROM',
               'SMTP_USE_SSL', 'SMTP_USE_TLS', 'RESEARCHBRIDGE_PASSWORD_RESET_ENABLED'}
    if not isinstance(values, dict) or set(values) - allowed:
        raise RuntimeError('Invalid hosted configuration keys.')
    for key, value in values.items():
        if not isinstance(value, str):
            raise RuntimeError('Hosted configuration values must be strings.')
        os.environ[key] = value
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
    os.environ['RESEARCHBRIDGE_AUTH_MODE'] = 'real'
