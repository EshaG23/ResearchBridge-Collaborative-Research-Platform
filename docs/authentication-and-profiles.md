# Current authentication: university roster login and password reset

This supersedes the earlier OTP sign-in and open college-email registration designs.

## Login

Only pre-provisioned users can sign in with email and password. Both students and faculty may use exactly rbunagpur.in or rknec.in. Domains are validated case-insensitively after trimming. Domain eligibility alone never creates an account. No signup endpoint or self-registration is provided. Old OTP verification routes now verify password-reset challenges only and never log users in or create them.

Student/faculty roles come from the imported roster. A faculty roster is an administrative approval source for the demonstration; users cannot change the assigned role. Imported names/departments prefill the profile while retaining previously saved details. Incomplete profiles still complete mandatory onboarding; complete profiles go to the dashboard.

## Roster storage

See demo_rosters/students.json and faculty.json plus their README for the five fictional demo accounts and import commands. The files are initial data sources; SQLite is the live database. Django stores password hashes. Re-import preserves existing usable passwords and profiles. Password changes never rewrite plaintext values in the source roster. Real rosters must remain in protected storage and not source control. No MongoDB dependency was introduced.

`import_roster <file> --demo` is local-demo-only. The real importer requires real mode and omission of --demo. Import is transactional, validates required fields and exact domains, rejects duplicates/conflicting roles, and does not delete accounts missing from a later file.

## Forgot Password

Registered email → request OTP → verify OTP → new password + confirmation → login with new password.

Challenges are hashed, tied to the browser session and current password, expire after three minutes, and allow five wrong attempts. Resend requires 60 seconds and invalidates old challenges. Reset requests are limited to five per email and thirty per IP over fifteen minutes. Password login allows ten attempts per email and sixty per IP over fifteen minutes. Login failures use a generic message. Unknown reset emails receive a generic response and cannot get a valid reset grant.

OTP verification creates a signed, session-held reset authorization valid for ten minutes; it does not authenticate the user. Django password validation and matching confirmation are required. Changing the password invalidates outstanding challenges, previous reset grants, and existing authenticated sessions through Django's session authentication hash. Logout and all reset writes are POST/CSRF-protected. Password values are masked in error reporting.

Local demo reset code is 123456. Demo mode stays under DEBUG with isolated private/demo storage and cannot be enabled in production. Real mode uses secure random six-digit reset codes delivered by SMTP. Actual SMTP delivery remains unverified. Before sending real messages, the project email account needs private SMTP credentials and an approved delivery test. Never paste credentials in chat or commit them. Current SMTP environment fields are documented in config/settings/base.py. Django email reference: https://docs.djangoproject.com/en/5.2/topics/email/ .

## Profiles retained

Required: name, department, phone, shared skills and research interests. Students additionally provide year 1–4, 1–80 hours/week and PDF résumé. Faculty research history and Scholar URL are optional; no student fields/résumé are required for faculty. Departments follow the owner-supplied list. Draft saving, profile editing, private owner-only résumé downloads and immutable résumé versions remain in place.

The database and uploaded files are not deleted by logout, password reset, re-import, or ordinary restart. Future applications must reference preserved résumé versions. Project/recruitment/community features remain separate future modules.
