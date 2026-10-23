# PythonAnywhere deployment without email

This setup uses production settings, password login, private persistent SQLite/uploads and disabled email reset. It does not enable local demo sessions or the fixed OTP. Each student/teacher completes their own profile. Create a PythonAnywhere account and web app first; replace USERNAME below with that account name. No hosting credentials belong in Git.

## 1. Source and environment

In a PythonAnywhere Bash console, clone your repository into `~/researchbridge`. If it is already cloned there, pull the reviewed changes instead of cloning again:

```bash
git clone https://github.com/EshaG23/ResearchBridge-Collaborative-Research-Platform.git ~/researchbridge
cd ~/researchbridge
python3.13 -m venv ~/.virtualenvs/researchbridge
source ~/.virtualenvs/researchbridge/bin/activate
pip install --no-cache-dir -r requirements.txt
mkdir -p ~/researchbridge-data/uploads
```

Choose an available Python version compatible with the pinned requirements (development used 3.13). The web app and virtualenv must use the same version. Stay within the free account disk quota; uploaded audio/video consumes it quickly. Do not use the Windows .cmd launch/reset scripts on this host.

## 2. Private settings

Run this once in the same Bash console. Replace the hostname with the exact one assigned by the Web tab, including its regional domain if applicable. Exclusive creation avoids replacing an existing secret:

```bash
python - <<'PY'
import json, os
from pathlib import Path
from django.core.management.utils import get_random_secret_key
path = Path.home() / '.researchbridge.json'
config = {
    'DJANGO_SECRET_KEY': get_random_secret_key(),
    'DJANGO_ALLOWED_HOSTS': 'USERNAME.pythonanywhere.com',
    'RESEARCHBRIDGE_DATA_DIR': str(Path.home() / 'researchbridge-data'),
    'RESEARCHBRIDGE_PASSWORD_RESET_ENABLED': '0'
}
with path.open('x', encoding='utf-8') as stream:
    json.dump(config, stream, indent=2)
os.chmod(path, 0o600)
PY
```

`deploy/environment.py` loads this private file for both WSGI and management commands, fixes authentication to real mode and uses production settings. No SMTP credentials are needed while reset is disabled. Existing .env files are not automatically loaded.

## 3. Database and accounts

```bash
python deploy/manage_hosted.py migrate --noinput
python deploy/manage_hosted.py seed_taxonomy
python deploy/manage_hosted.py collectstatic --noinput
```

Create separate private student and faculty JSON rosters outside the repository, for example `~/students-private-roster.json`. Use the structure below, with approved email addresses, a real chosen name and a unique strong initial password per account. Do not reuse the public demo password. These placeholders must be replaced before import:

```json
{
  "role": "student",
  "accounts": [
    {"name": "REPLACE_NAME", "email": "APPROVED_ADDRESS@rbunagpur.in", "department": "CSE", "initial_password": "REPLACE_WITH_UNIQUE_PRIVATE_PASSWORD"}
  ]
}
```

For faculty use `"role": "teacher"`. Both supported university domains are accepted. Import without `--demo`:

```bash
chmod 600 ~/students-private-roster.json ~/faculty-private-roster.json
python deploy/manage_hosted.py import_roster ~/students-private-roster.json
python deploy/manage_hosted.py import_roster ~/faculty-private-roster.json
```

Roster import does not complete profiles. Re-import preserves existing passwords and profile data. Retain roster files only in private controlled storage; they contain initial passwords. Do not expose them through static-file mappings.

With email skipped, the operator can reset an account password interactively after verifying the person's identity:

```bash
python deploy/manage_hosted.py changepassword APPROVED_ADDRESS@rbunagpur.in
```

Do not type the new password in shell command arguments. Optional Django administration uses `createsuperuser`; it is not a replacement for importing student/teacher roles.

## 4. Web configuration

In PythonAnywhere's Web tab choose Manual configuration and the matching Python version. Set the virtualenv to `/home/USERNAME/.virtualenvs/researchbridge`. Replace the contents of the WSGI configuration file linked on that tab with `deploy/pythonanywhere_wsgi.py`. This assumes the checkout is `~/researchbridge`.

Map only `/static/` to `/home/USERNAME/researchbridge/staticfiles`. Do not add a public `/media/`, `/uploads/`, home-directory or project-root mapping. Django's permission-checked views serve private downloads.

Use the assigned HTTPS hostname. Production already redirects insecure requests and sets secure cookies. Verify HTTPS reaches Django correctly on the host; do not add a blindly trusted forwarded-protocol header or disable HTTPS to work around redirect loops.

Reload the web app, then run:

```bash
python deploy/manage_hosted.py check --deploy
```

Visit `/health/` and `/accounts/login/` over HTTPS. Confirm static assets load, real-mode accounts log in, incomplete profiles are required, and password help states email reset is unavailable. Verify authorised/private downloads and denied access from unrelated users. Test signatures, chat/polls and task persistence before sharing the link. Use separate browser profiles to demonstrate accounts simultaneously; the local demo-session helper is intentionally unavailable online.

## 5. Updates and backups

Before schema changes, stop writers and follow docs/operations.md to back up both database and uploads. Use `python deploy/manage_hosted.py` instead of `python manage.py` for hosted backup/restore commands so they target the hosted directory. Keep a separate backup copy away from the host. Never run the local reset script on hosted data.

For a reviewed code update: pull changes, install requirements if changed, apply migrations, collectstatic and reload. Do not overwrite the private settings or storage directory. Check the host's free-plan expiry/renewal and disk quota regularly.

Email can be added later by configuring the SMTP values in the private JSON and setting RESEARCHBRIDGE_PASSWORD_RESET_ENABLED to 1, then testing delivery. Production rejects enabled reset without SMTP credentials. Hosting, HTTPS and browser behaviour still require verification on the actual account; local tests do not establish deployment success.
