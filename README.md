# ResearchBridge

College research collaboration for registered `rbunagpur.in` and `rknec.in` users. This is a student project, not a claim of official university endorsement.

Modules 1–4 provide the foundation, shared UI, roster-based password authentication, and persisted role-specific profiles. The ten-part product specification remains the source of truth; coding modules do not replace its numbering. Real SMTP delivery still needs private setup and testing. Modules 5–7 add shared access policies, private PDF documents and versions, persistent in-app notifications, and student/faculty idea creation. See [modules 5–7 guide](docs/modules-5-7.md). Module 8 adds mentor matching, sequential requests and faculty decisions; see [the mentor guide](docs/module-8.md). Module 9 adds [project discovery and filters](docs/module-9.md) on Dashboard and Discover projects. Module 10 adds [applications with private résumé snapshots](docs/module-10.md). Module 11 adds [applicant review, shortlisting and optional meetings](docs/module-11.md). Offer letters and community workflows remain for later modules.

## Demo accounts

See [demo roster instructions and credentials](demo_rosters/README.md). After initial migrations/taxonomy setup, import both roster files using those commands. The current local demo is already imported.

## Run locally

Python 3.13 is installed on the current machine. From this project directory, the existing environment can be used without activation:

```powershell

..\..\work\.venv\Scripts\python.exe manage.py migrate
..\..\work\.venv\Scripts\python.exe manage.py seed_demo_taxonomy

..\..\work\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

```

Open http://127.0.0.1:8000/. The root opens sign-in. Use student1@rbunagpur.in with initial password ResearchDemo!2026, then complete the mandatory profile. OTP 123456 is now only for local Forgot Password. Review the local interface at http://127.0.0.1:8000/dev/ui/ and shared components at http://127.0.0.1:8000/dev/ui/components/. These previews are disabled in production and contain no real research data.

For a fresh checkout:

```powershell

python -m venv .venv

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo_taxonomy

.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

```

Use the same Python executable for checks:

```powershell

..\..\work\.venv\Scripts\python.exe manage.py check

..\..\work\.venv\Scripts\python.exe manage.py test

..\..\work\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run

```

Optional local administration: run `manage.py createsuperuser` using that Python executable. Enter an eligible college email and a private administrator password interactively. This is a maintenance account, not proof of inbox ownership or teacher status. No credentials are seeded. Student/teacher roles come from imported rosters. Login uses passwords; OTP is only for password reset.

## Documentation

- [Complete original requirements](docs/requirements-original.md)

- [Architecture and module mapping](docs/architecture.md)

- [Permissions and workflow states](docs/permissions-and-states.md)

- [Assumptions and unresolved decisions](docs/decisions.md)

- [Authentication and profiles](docs/authentication-and-profiles.md)
- [Shared interface](docs/interface.md)

- [Implementation and test status](docs/status.md)

- [Deployment and backup guidance](docs/operations.md)

Do not delete `private/` to reset or restart the app. It contains persistent local data and the development signing secret. Do not commit it or upload it with source code.



Module 12 completed: private, immutable offer letters with mentor preview, PDF downloads and in-app notification. See docs/module-12.md. Agreement signing follows in Module 13.


Module 13 completed: drawn/typed/physical agreement signing, immutable evidence PDFs, mentor verification, correction history and intended-team readiness checklist. See docs/module-13.md.


Module 14 completed: mentor-created private community, all-student agreement gate, explicit admission, leader appointment, protected five-section landing page and history. See docs/module-14.md.


Module 15 completed: editable research summary, custom sections, private PDF/PPTX/reference library, sprint planning/status board and recorded edit history. See docs/module-15.md.


Module 16 completed: private persistent team chat, replies, media library, protected audio/video/photo/document attachments, voice-note recording, polls and mentor/leader announcements. All 134 tests passed. See docs/module-16.md.


Module 17 completed: task assignment, progress and blockers, private evidence files, numbered submissions, mentor/leader review, changes requested, reopening, task/file discussion and approved task totals. All 145 regression tests passed. See docs/module-17.md.


Module 18 completed: private filtered history, explicit document version chains, preserved comments/reviews and contribution views. Also added the requested Module 17 checklist/Completed view and persistent dashboard chat unread counts. All 149 regression tests passed. See docs/module-18.md.


## Latest release

Module 19 adds completion, private IP progress and mentor-approved shared achievements. Module 20 adds connected verification, backup/restore tools and local launch scripts. Public hosting and real SMTP delivery still require external configuration; see docs/module-20.md.

In CMD, run `start-demo.cmd` from this folder, then open http://127.0.0.1:8000/accounts/login/. See demo_rosters/README.md for the 5 student and 5 teacher accounts. All initial passwords are `ResearchDemo!2026`; profiles must be completed after login.
