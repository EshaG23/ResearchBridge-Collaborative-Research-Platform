"""Archive the local demo and recreate its ten roster accounts. Never touches real data."""
from datetime import datetime
from pathlib import Path
import os
import socket
import subprocess
import sys


def reset(project, check_port=True):
    project = Path(project).resolve()
    private = project / 'private'
    private.mkdir(exist_ok=True)
    if private.is_symlink() or private.resolve().parent != project:
        raise RuntimeError('Unsafe private directory. Reset cancelled.')
    source = private / 'demo'
    if source.is_symlink() or source.resolve().parent != private:
        raise RuntimeError('Unsafe demo directory. Reset cancelled.')
    if check_port:
        with socket.socket() as connection:
            connection.settimeout(1)
            if connection.connect_ex(('127.0.0.1', 8000)) == 0:
                raise RuntimeError('Stop the server with Ctrl+C first. Also stop any servers on other ports.')
    archive = private / ('demo-backup-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    if archive.parent != private or archive.exists():
        raise RuntimeError('Unsafe backup destination. Reset cancelled.')
    if source.exists():
        source.rename(archive)
        print('Previous demo preserved at: ' + str(archive), flush=True)
    env = dict(os.environ, RESEARCHBRIDGE_AUTH_MODE='demo', DJANGO_SETTINGS_MODULE='config.settings.local')
    commands = [
        ['migrate', '--noinput'],
        ['seed_demo_taxonomy'],
        ['import_roster', 'demo_rosters/students.json', '--demo'],
        ['import_roster', 'demo_rosters/faculty.json', '--demo'],
    ]
    for command in commands:
        subprocess.run([sys.executable, str(project / 'manage.py'), *command], cwd=project, env=env, check=True)
    print('\nFresh demo ready: 5 students and 5 teachers; profiles require completion.')
    print('Initial password: ResearchDemo!2026 | Demo reset OTP: 123456')
    print('Run start-demo.cmd, then open http://127.0.0.1:8000/accounts/demo-session/')


if __name__ == '__main__':
    try:
        reset(Path(__file__).resolve().parents[1])
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print('Reset stopped: ' + str(error), file=sys.stderr)
        print('Any previous demo backup is preserved. Do not repeat the reset blindly.', file=sys.stderr)
        sys.exit(1)
