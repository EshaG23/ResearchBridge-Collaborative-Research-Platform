"""Run with the hosting virtualenv: python deploy/manage_hosted.py migrate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from deploy.environment import configure
configure()
from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)
