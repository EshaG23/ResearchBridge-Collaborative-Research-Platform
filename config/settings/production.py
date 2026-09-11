from .base import *  # noqa: F403
from django.core.exceptions import ImproperlyConfigured

if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("Set a private DJANGO_SECRET_KEY of at least 50 characters.")
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Set explicit DJANGO_ALLOWED_HOSTS for this deployment.")
if not DATA_DIR.is_dir():
    raise ImproperlyConfigured("Provision RESEARCHBRIDGE_DATA_DIR on persistent storage first.")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
# Configure a trusted proxy header only after verifying the chosen host's behaviour.
