"""Copy this into the WSGI configuration file linked from PythonAnywhere's Web tab."""
import sys
from pathlib import Path

project = Path.home() / 'researchbridge'
sys.path.insert(0, str(project))
from deploy.environment import configure
configure()
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
