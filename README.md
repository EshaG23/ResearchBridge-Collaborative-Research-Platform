# ResearchBridge

College research collaboration for eligible `rbunagpur.in` users. This is a student project, not a claim of official university endorsement.

Module 1 establishes the Django foundation. The ten-part product specification remains the source of truth; coding modules do not replace its numbering. Authentication and research workflows are not implemented yet.

## Run locally

Python 3.13 is installed on the current machine. From this project directory, the existing environment can be used without activation:

```powershell
..\..\work\.venv\Scripts\python.exe manage.py migrate
..\..\work\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/. The root redirects to an honest sign-in placeholder. No fake OTP form or research data is provided.

For a fresh checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Use the same Python executable for checks:

```powershell
..\..\work\.venv\Scripts\python.exe manage.py check
..\..\work\.venv\Scripts\python.exe manage.py test
..\..\work\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Optional local administration: run `manage.py createsuperuser` using that Python executable. Enter an eligible college email and a private administrator password interactively. This is a maintenance account, not proof of inbox ownership or teacher status. No credentials are seeded. Student/teacher sign-in will use OTP in Module 3.

## Documentation

- [Complete original requirements](docs/requirements-original.md)
- [Architecture and module mapping](docs/architecture.md)
- [Permissions and workflow states](docs/permissions-and-states.md)
- [Assumptions and unresolved decisions](docs/decisions.md)
- [Implementation and test status](docs/status.md)
- [Deployment and backup guidance](docs/operations.md)

Do not delete `private/` to reset or restart the app. It contains persistent local data and the development signing secret. Do not commit it or upload it with source code.
