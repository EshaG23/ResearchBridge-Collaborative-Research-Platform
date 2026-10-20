# ResearchBridge

A university research collaboration portal for roster-approved students and teachers using `rbunagpur.in` or `rknec.in` email addresses. This is a student project, not a claim of official university endorsement.

## Features

The implementation covers twenty development modules: university roster login and password reset; role-specific profiles and resumes; protected documents; persistent notifications; idea creation; mentor matching; project discovery; applications and review; offer letters; agreement signing and verification; private communities; research summaries and document versions; chat, attachments and polls; announcements; tasks and reviewed evidence; activity history and contributions; completion and intellectual-property progress; backup and restore utilities.

The frontend uses Django HTML templates, CSS and vanilla JavaScript. The backend uses Python and Django; SQLite stores records, and private folders store uploaded/generated files. See `requirements.txt` for dependency versions.

## Fresh checkout: Windows CMD

Python 3.13 was used for development. Install Python with the Windows `py` launcher, then open CMD inside the cloned `researchbridge` project folder (the folder containing `manage.py`). Run each command separately and continue only if it succeeds:

```cmd
setup-demo.cmd
reset-demo.cmd
start-demo.cmd
```

`setup-demo.cmd` creates a local `.venv`, installs dependencies and applies migrations. `reset-demo.cmd` creates taxonomy and the ten fictional roster accounts. On an existing installation it first archives the current demo data, so use it only when you want a fresh demo. Stop running project servers before resetting. `start-demo.cmd` applies migrations and starts the local server.

Open http://127.0.0.1:8000/accounts/demo-session/ . Keep the terminal open while using the app; Ctrl+C stops the server. For subsequent runs that preserve existing data, use only `start-demo.cmd`.

Use **Open another account** for independent side-by-side demo sessions. See [demo accounts](demo_rosters/README.md) for all five students and five teachers. Initial demo password: `ResearchDemo!2026`. Local forgot-password OTP: `123456`. These are intentionally public fictional demo credentials; do not use them for real accounts.

## Development checks

From a checkout set up with `setup-demo.cmd`:

```cmd
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.venv\Scripts\python.exe manage.py test
```

Use the same Python environment for all management commands. Tests use isolated test databases. The module documents record historical verification, not a guarantee about future modifications.

## Data and credentials

- Demo records: `private/demo/db.sqlite3`.
- Demo uploaded/generated files: `private/demo/uploads/`.
- Local development secret: `private/demo/.development-secret`.
- Reset archives: `private/demo-backup-TIMESTAMP/`.
- `demo_rosters/` contains fictional initial account data, not the live database. Keep real university rosters outside the repository.

The entire `private/` directory is ignored by Git. Do not manually upload it to GitHub or include it in a release ZIP. A source checkout intentionally excludes live profiles, signatures, chat uploads and database contents. Back up the database and uploads together using the documented operations tools.

`.env.example` contains placeholders only. Django does not automatically load `.env` files: set configuration through the process/host environment. Production requires a private secret, explicit hosts, persistent storage and real authentication/email configuration. The local development server and fixed demo OTP are not production hosting. Real SMTP delivery still requires setup and testing.

## Documentation

- [Complete project explanation and file reference](docs/PRESENTATION-GUIDE.md)
- [Offline HTML presentation guide](docs/PRESENTATION-GUIDE.html)
- [Original requirements](docs/requirements-original.md)
- [Architecture](docs/architecture.md)
- [Permissions and workflow states](docs/permissions-and-states.md)
- [Authentication and profiles](docs/authentication-and-profiles.md)
- [Interface](docs/interface.md)
- [Implementation status](docs/status.md)
- [Operations, deployment and backups](docs/operations.md)
- [GitHub publishing checks](docs/github-publishing.md)

Module-specific guides under `docs/` explain implementation details. Original requirements and older module notes are historical; the complete guide describes later decisions such as roster-based login without public signup.
