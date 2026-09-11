# Modules 3 and 4: authentication and profiles

## Try the working local demo

Open `/accounts/login/`. Use `demo.student@rbunagpur.in`, `demo.applicant@rbunagpur.in`, or `demo.teacher@rbunagpur.in` with `123456`. No email is sent and no ownership of a real inbox is claimed. Other emails cannot use the fixed code. A demo teacher profile was saved during browser verification using clearly labelled demo details; its teacher approval remains pending. Student/applicant identities are available for fresh onboarding.

Accounts are created only when the challenge is verified. Challenges expire after three minutes, allow five wrong code attempts, and are bound to the requesting browser session. Replacement codes invalidate previous challenges; resend cooldown is 60 seconds. Database counters cap five requests per email and thirty per source IP over fifteen minutes. IP keys and OTP values are stored as keyed digests, not plaintext. A database write serializes verification before consuming a challenge, including on SQLite. No external queue/cache dependency is needed.

Logout is POST-only and ends the session without deleting saved records. A returning complete profile reaches `/dashboard/`; incomplete profiles return to `/profile/`. Private responses are not cacheable. CSRF protection applies to form submissions.

## Profile completion

Required for both roles: name, department, phone (10–15 digits), skills and research interests. Students also need weekly availability (1–80 hours), year (1–4), and a readable unencrypted PDF résumé (up to 5 MB, 1–50 pages). These limits are configurable implementation choices in the form and can be revised. Teacher previous work and Google Scholar links are optional. No teacher résumé or student-year fields are required for teachers.

Use Save draft during onboarding to retain incomplete details. Complete profile validates the full role-specific requirements. After completion, account email and role cannot be changed through profile editing; role correction needs explicit administrative handling. This is a reversible permission default, not a claim of a final college policy.

Selecting Teacher does not grant mentor permissions. An administrator can approve a teacher claim in Django admin > Profiles after the institution's verification procedure. The `is_verified_teacher` property is the permission predicate for upcoming mentor operations. A completed pending teacher profile can reach the account dashboard but has no mentor operations yet.

Demo department fixtures are visibly labelled and separate from real department choices. Run `manage.py seed_demo_taxonomy` explicitly in local demo mode; it is idempotent and creates no users. The project owner has supplied the current department options; see the latest status entry. Skills/interests use shared controlled tables for later matching.

Each résumé upload creates a new immutable file record; previous versions stay downloadable by their owner. Changing a profile résumé cannot overwrite a stored earlier file. Future applications must reference these version records with protected foreign keys. Owner-only download routes currently serve files as attachments; broader reviewer permissions belong to later modules. Upload/database failures show an error and remove a newly stored orphan file. Malware scanning and deployment request-body caps are not claimed by PDF-format validation.

## Data and local setup

Local demo data now resides in `private/demo/db.sqlite3` and `private/demo/uploads/`. The earlier `private/db.sqlite3` was preserved. Local real mode uses the configured `RESEARCHBRIDGE_DATA_DIR`, defaulting to `private/`. Demo mode is deliberately restricted to DEBUG/local development and refused by production settings. Back up the database and matching uploads together while the server is stopped. No demo seed runs on startup.

After pulling these changes, run migrations and the explicit demo taxonomy command using the environment Python executable in README. The current local demo migration and taxonomy setup have already run. Never delete persistent directories during restart.

## Real email status

The real OTP path is implemented using Django SMTP. It was tested using Django's in-memory email backend, including random-code generation, actual code checking, email failure handling, and verification timestamps. Actual external SMTP delivery remains UNVERIFIED and requires a dedicated email account's private credentials and an approved delivery test.

When ready, set `RESEARCHBRIDGE_AUTH_MODE=real`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, and `SMTP_PASSWORD` in the private process/host environment. The default route is smtp.gmail.com:587 with TLS. Do not paste passwords in chat or commit them. Real mode never accepts the fixed demo code as a shortcut; demo user records cannot be authenticated in real mode. The current local demo database is isolated from real-mode data.

The proposed Gmail App Password eligibility and official setup steps must be checked when an account is actually being configured. No paid service or account purchase was introduced. Django SMTP reference: https://docs.djangoproject.com/en/5.2/topics/email/ . PDF parsing reference: https://pypdf.readthedocs.io/en/stable/modules/PdfReader.html .

## Scope boundary

Modules 3–4 do not implement research discovery, project permissions beyond account/file ownership, applications, or mentor management. The real dashboard is an honest account workspace until the project modules arrive; `/dev/ui/` remains a separate design preview.
