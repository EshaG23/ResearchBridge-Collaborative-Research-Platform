# Implementation status

## Module 1 — completed

Implemented: isolated Python environment; pinned Django dependencies; separated app packages; local/production settings; custom college-email user model; database migration foundation; ignored persistent-data directory; admin registration; root-to-sign-in routing; minimal honest sign-in placeholder; original requirements and implementation documentation.

No pre-existing source or Git repository was present. No Next.js/Supabase migration was needed. Full design work is Module 2; working OTP is Module 3. App package presence does not mean its business workflow is implemented.

## Checks actually run

- Initial migration generation and application: passed, including custom user, auth, admin, and sessions.
- `manage.py check`: passed with no issues.
- `manage.py test --verbosity 2`: all 10 tests passed (email validation/normalisation, case-insensitive database uniqueness, direct-save eligibility, admin permission requirements/login, entry routing, honest placeholder, and absence of public media routes).
- `manage.py makemigrations --check --dry-run`: passed, no missing migrations.
- `python -m pip check`: passed, no broken requirements.
- Local development server on `127.0.0.1:8000`: root redirects to sign-in; entry HTML and CSS both return HTTP 200.
- Separate-process persistence check on an isolated scratch SQLite database: designated test record and development secret retained after another migration/process. No test account was added to the actual application database.
- Production `check --deploy --fail-level WARNING`: passed with explicit temporary test secret, host, and data directory. This validates configuration checks only, not a real host.
- SHA-256 comparison: requirements copy matches the complete original attachment byte for byte.
- Git ignore inspection: database, private uploads, development secret, and Python cache files excluded.

Modules 2–20 are pending. Real email, hosting, signed agreements, project workflows, browser visual QA, and full database/file backup-and-restore remain unverified. The sign-in page is a placeholder, not an implemented login feature.


## Module 2 — completed

Implemented the college sign-in presentation, reusable HTML components, workspace sidebar/top bar, notification and profile disclosures, mobile navigation, field/message/empty states, card grid, and responsive table styling. Added a clearly labelled development-only preview and component gallery; it never queries research records or authenticates users.

Verification completed:

- All 12 Django tests passed, including production preview rejection and POST rejection.
- Django system checks passed; no migration changes detected.
- Browser navigation verified for discovery, projects, communities, and components.
- Notification and profile panels show truthful preview content; Escape closes the profile disclosure and returns focus to its trigger, observed in the DOM snapshot.
- Mobile navigation expands and opens the selected destination.
- Feedback demonstration shows loading, completion, and reset without claiming an actual save.
- Project-card layout measured at 1280px (three columns), 900px (two), and 390px (one); no horizontal document overflow at those widths.
- Desktop and phone sign-in screenshots visually inspected; phone component layout inspected.
- All five community labels present; no additional primary destination added.
- Captured browser error log contained no errors during final verification.

One browser tab creation took unusually long; a later focus-inspection call timed out, so focus/dismissal was verified from the current DOM snapshot instead. No blanket accessibility audit is claimed.

Modules 3–20 remain pending. Authentication, discovery filters, idea creation, actual notifications, profiles, and community workflows are not connected yet. No database schema/data changes in Module 2. The full agreed scope is unchanged.

## Module 2 visual refinement

Redesigned the entrance as a framed two-panel layout with a research-journey sidebar, stronger heading hierarchy, focused email panel, and replaceable text identity. Refined shared navigation, milestone banner, empty states, community destinations, controls, and card styling through `static/css/refinement.css`.

Discovery now contains three explicitly labelled illustrative topic cards so the intended recruitment design can be reviewed. These are template-only design samples, not published records or achievements. No data, permission rules, or authentication behaviour changed.

Validation: all 12 existing Django tests passed from the project directory. An initial test invocation from the parent directory discovered zero tests and was rerun correctly. Desktop entrance and three-column discovery screenshots inspected; 390px mobile sign-in and discovery checked for horizontal overflow. Fixed heading whitespace at the phone breakpoint and text encoding in preview templates. No real workflows or new module implementation claimed.


## Modules 3 and 4 — local demo complete; external email integration pending

Implemented: eligible-email request form; bound/expiring/single-use OTP; request limits and resend timer; verification; POST logout; separated demo database; mandatory profile gate; editable student/teacher profiles; resumable drafts; shared controlled taxonomy; private immutable résumé uploads/downloads; administrative teacher approval field; basic authenticated workspace. Real OTP/SMTP code exists, but actual inbox delivery is unverified and requires private credentials plus an approved test.

Executed checks: all 30 Django tests passed after final backend corrections. Coverage includes email restriction, no pre-verification account creation, demo allowlist and real-account protection, expiry/replay/wrong-session rejection, five-attempt lockout, resend invalidation and rate limits, CSRF, POST logout, real-code path through in-memory email, failed-send invalidation, mandatory onboarding, draft persistence, protected roles, optional teacher fields, owner-only résumé downloads, PDF/phone/availability/Scholar validation, résumé version preservation, upload failure rollback, and logout followed by actual OTP re-login preserving student data. Migrations applied to the isolated demo database; no missing migrations or dependency conflicts.

Browser: rejected personal email, displayed OTP countdown/resend cooldown, verified designated teacher OTP, showed mandatory onboarding, hid student fields after teacher selection, saved a teacher profile without granting approval, logged out, reverified OTP, and returned to the saved account dashboard. Initial profile screen included an unwanted blank role option; replaced generated choices with exactly Student/Teacher. Profile screenshots reviewed. Demo teacher record intentionally remains in the local demo database; no real data was created.

Modules 5–20 remain pending. Full product scope unchanged. See authentication-and-profiles.md for demo identities, data paths, limits and remaining external setup.


## Profile options update

Year choices are now 1–4. The project owner supplied CSE, AIML, AIDS, BCA, MCA, EE, ECS, MECH, CIVIL, ROBOTICS. A data migration adds these exact labels for fresh and existing databases. Existing profile department references remain intact and appear on that profile until changed; new profiles use the supplied list. Earlier demo-department/year defaults are superseded.


## Complete visual redesign and expanded local demo access

User-authorised correction: replace the former restrained design with a more colourful, detailed interface, and allow any structurally valid rbunagpur.in email to use 123456 locally. Implemented a new login collaboration diagram, colourful numbered profile sections, selectable skill/interest chips, résumé treatment, profile section navigation, and a detailed dashboard using only actual saved profile data. Shared discovery/component/community styling updated. Years 1–4 and supplied department options remain intact.

The fixed-code flow still requires DEBUG/local demo mode, exact college domain, and isolated demo storage. Existing real user records remain protected. No inbox ownership is claimed. Production demo login remains disabled; actual SMTP delivery is still pending.

All 30 regression tests passed after expanding the demo rule, including authentication of a new college address, refusal of existing non-demo accounts, expiry/attempt/rate protections, and profile/file behaviour. Browser verification showed a previously unlisted research.preview@rbunagpur.in address using 123456 and reaching required onboarding. Reviewed desktop dashboard/profile/login and phone profile/login; no horizontal overflow at 390px. Original saved profiles and résumés were not changed. A blank test demo account remains for the new-email check. Signed out after browser verification and left login ready for the user.


## Roster-only login and Forgot Password — current user-approved workflow

Replaced open email OTP authentication with email/password login for registered roster users only. Both roles accept rbunagpur.in and rknec.in. Added two fictional JSON data files, a transactional import command, assigned role storage, automatic faculty-roster approval, password-reset request/OTP/new-password screens, and protection against role edits and legacy unregistered sessions. Existing user/profile/résumé data retained; unlisted demo users are not deleted but cannot log in until explicitly provisioned.

Passwords are hashed in SQLite; changing one does not modify plaintext initial roster files. Re-import does not overwrite changed passwords. The local demo remains physically isolated; actual random-code SMTP delivery awaits external setup. The full ten-part product scope remains intact with this authentication correction.

Validation: 38 tests passed, covering both-domain/password login, unregistered denial/no creation, request/attempt limits, expiry/replay/binding, no login from reset OTP, signed reset grants, confirmation/strength validation, old-code and session invalidation, old-password rejection/new-password success, unknown-email reset failure, SMTP simulation/failure, preserved profile/files, and idempotent roster import. Browser confirmed faculty.one@rknec.in login, assigned approved faculty role, hidden student fields, and registered-email Forgot Password through OTP to the new-password form. Browser verification did not change an account password; password updates were tested in the isolated test database. Five demo roster accounts imported successfully; their initial password is documented in demo_rosters/README.md.


## Modules 5–7 — completed

Module 5: reusable deny-by-default role/project checks; private PDF validation and downloads; immutable résumé versions; private project document upload and preserved numbered versions with uploader, size and SHA-256 metadata. Downloads validate the resource's project, current access and storage-root containment, and return attachment/no-store/nosniff headers. Staff status is not a project access bypass.

Module 6: database notifications with recipient/event-key uniqueness, unread counts, read timestamps, POST/CSRF-protected read controls, pagination, authorised project destinations and 30-second polling. Saved ideas generate real persistent events in the same database transaction. Future workflow modules can use the same notification service.

Module 7: student and approved-faculty idea creation, shared skill/domain/department choices, 240-character recruitment summary, positions and optional roles. Separate confidential records and private pages. Faculty-created ideas attach their creator as mentor and can publish recruitment; student submissions truthfully await a mentor. Drafts, edits, duplicate-create protection, stale-edit detection, Created Ideas/My Projects and paginated dashboard notices work. Original proposer remains separate from mentor.

Validation: all 55 tests passed; after final access-revocation and save-error handling adjustments, all 23 affected project/core tests passed again. Migrations applied and no missing migrations detected. Tests cover private data/file denial, cross-project URLs, immutable versions, storage failure rollback, role escalation, stale edits, atomic idea/notification rollback, retries, CSRF, notification persistence across login/logout, authorised links and cache headers.

Browser: created a labelled fictional student idea, checked its recruitment and confidential pages, opened its notification and observed unread count change from 1 to 0. Desktop private-space screenshot and 390px idea form reviewed, with no horizontal overflow. The demo idea remains in the local demo database. Mentor matching, applications, NDA and community workflows are still later modules; no automatic mentor acceptance or community access has been invented.


## Module 8 — completed

Implemented deterministic mentor ranking with explanations, chosen-first saved priority queues, one pending request, sequential rejection forwarding, acceptance/mentor attachment and recruitment publication. Added student request status, faculty inbox/review, private access boundaries, idempotent transactional decisions and in-app events. Stale reviews require reloading. Ineligible queued teachers are skipped; empty/exhausted/pending states remain truthful.

All 68 regression tests passed, including 13 new mentorship tests. Migrations applied; Django checks and missing-migration checks passed. Browser verified recommendations on an existing student idea and phone-width overflow check. User-created project content was preserved and no mentor request was sent during browser verification. See module-8.md for matching rules and how to test both roles. Modules 9–20 remain pending.


## Module 9 — completed

Implemented authenticated project discovery on Dashboard and a dedicated sidebar page, recruitment-only search, department/domain/skill filters, four sorting choices, stable pagination, clear-filter controls and contextual empty/error states. Cards include mentor/proposer identity and retain three/two/one responsive columns. Unpublished/closed records and confidential contents are excluded.

Validation: all 44 affected project/mentorship/core tests passed, including 8 new discovery tests. No migration changes detected. Browser checked real records and CSE filtering from two results to one; desktop grid measured at three columns. Existing project records preserved. Application workflows begin in Module 10.


## Module 10 — baseline completed

Implemented résumé choice/upload, private reviewable application drafts, confirmation, preserved profile/résumé snapshots, My applications and mentor-only submitted application access. Duplicate submission protection, notifications, stale-review checks and recruitment eligibility are enforced server-side. Optional PDF autofill remains unimplemented; manual academic score entry is available. No scope change to later applicant review or selection workflows.

All 51 relevant tests passed, including 7 new application tests. Migration applied; Django checks and no-missing-migration checks passed. Browser verified the live Apply link and selection form using an existing student session. No application was submitted against user data during verification. See module-10.md.


## Module 11 — completed

Added applicant-management overview, name/status filters and counts; mentor-only private review; shortlisting, not-selected/reopen and final selection with position-capacity enforcement; immutable decision-history records; optional private meeting invitations with IST timestamps, HTTPS links and cancellation history. In-app notifications link directly to authorised application context. Student proposers receive a restricted overview only, with no résumé, contact, meeting or decision access.

All 95 tests passed, including 12 new review/meeting tests. Migrations applied and no missing migration changes detected. Browser inspection used isolated test-database sample pages because the live demo has no applications after its reset. Checked the desktop applicant table, review actions and phone meeting form; live reset data preserved. Offer-letter issuance remains Module 12. See module-11.md.


Module 12 completed: private, immutable offer letters with mentor preview, PDF downloads and in-app notification. See docs/module-12.md. Agreement signing follows in Module 13.


Module 13 completed: drawn/typed/physical agreement signing, immutable evidence PDFs, mentor verification, correction history and intended-team readiness checklist. See docs/module-13.md.
