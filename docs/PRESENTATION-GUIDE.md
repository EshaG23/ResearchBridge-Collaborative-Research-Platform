# ResearchBridge — Complete Project & Presentation Guide

Prepared for Esha • 15 September 2026 • Local demo implementation

## 1. Project explanation and presentation introduction

ResearchBridge is a university research collaboration portal. It connects students with research opportunities and teacher mentors, then carries selected teams through confidentiality agreements, private collaboration, reviewed tasks, preserved documents and research outcomes. Recruitment and controlled admission happen before team collaboration, distinguishing it from a general task manager.

Opening script: “ResearchBridge brings the university research journey into one system. Students and teachers can propose ideas, find collaborators, record selection and confidentiality agreements, collaborate privately, and preserve research progress. Our frontend uses HTML, CSS and JavaScript. Python and Django implement the backend. SQLite stores structured records, and private folders store uploaded files.”

The original product has ten conceptual parts; development was split into twenty coding modules. A Django app is a code package and does not necessarily equal one coding module. This guide explains the current implementation. Historical requirements mention signup and one domain; later decisions replaced signup with roster-based login and accepted both rbunagpur.in and rknec.in. Public hosting and verified real-email delivery remain external setup steps.

## 2. Exact folders, launch, reset and accounts

Project root on this laptop:

```text
C:\Users\Disha\Documents\Codex\2026-09-11\hi\outputs\researchbridge
```

Disha is the Windows folder name; Esha is the presenter. Do not change the path just because the presenter name differs.

### Normal startup: keep saved data

Open Command Prompt and run each line separately:

```cmd
cd /d "C:\Users\Disha\Documents\Codex\2026-09-11\hi\outputs\researchbridge"
start-demo.cmd
```

Keep CMD open. Open http://127.0.0.1:8000/accounts/demo-session/ in a browser. Ctrl+C stops the server. Restarting preserves work. The script applies outstanding migrations then starts the local Django development server. It does not automatically run when Windows starts. This is not a production hosting server.

### Universal reusable demo reset

Stop every running copy of the project server, including any custom-port copy. Run each line separately:

```cmd
cd /d "C:\Users\Disha\Documents\Codex\2026-09-11\hi\outputs\researchbridge"
reset-demo.cmd
```

After “Fresh demo ready”, run:

```cmd
start-demo.cmd
```

Use this script instead of the old multiline caret command. It validates directory boundaries, refuses to run if port 8000 has a listener, archives private/demo as private/demo-backup-TIMESTAMP, applies all migrations, recreates taxonomy and imports five students/five teachers. Profiles become incomplete and passwords return to initial defaults. Live projects, applications, agreements, chat, tasks, polls, notifications and uploaded files start empty. Old data remains in the backup rather than being permanently deleted. Source code and real-mode data outside private/demo stay intact. The reset does not start the server itself.

reset-demo.cmd locates the interpreter; scripts/reset_demo.py performs the archive and setup sequence. Each failure stops the sequence. The server check covers port 8000; you must stop other ports yourself. If a step fails, keep the error and the backup rather than repeatedly resetting. This command is reusable for this project installation; dependencies and roster files must exist.

### Demo accounts

All initial passwords: ResearchDemo!2026. Forgot-password demo OTP: 123456. Ordinary login uses the password, not the OTP.

| Role | Email | Department |
|---|---|---|
| Student | student1@rbunagpur.in | CSE |
| Student | student2@rbunagpur.in | AIML |
| Student | student3@rbunagpur.in | AIDS |
| Student | student4@rknec.in | EE |
| Student | student5@rknec.in | MECH |
| Teacher | teacher1@rbunagpur.in | CSE |
| Teacher | teacher2@rbunagpur.in | AIML |
| Teacher | teacher3@rbunagpur.in | AIDS |
| Teacher | teacher4@rknec.in | EE |
| Teacher | teacher5@rknec.in | MECH |

Names, roles and departments come from fictional demo rosters. Remaining profile fields require completion. Teachers are approved demo identities, not verified real university inboxes. JSON rosters are import data, not the runtime database. Password changes update SQLite and do not rewrite the initial password in JSON. Re-import preserves existing passwords; reset recreates accounts.

### Accounts side by side

Click “Open another account” on login or the demo banner. Each new /demo/<identifier>/ namespace has separate session, CSRF and message cookies. Tabs share the same database, so updates remain visible across roles. A duplicate of the same session URL intentionally shares that account; use the button for a different account. An identifier is not a password and does not log someone in from another browser. Logging out affects that session only. This helper is restricted to local demo mode.

## 3. Technology stack

| Technology | Responsibility |
|---|---|
| Python | Backend business rules, validation, matching, persistence and PDF generation |
| Django 5.2.17 | URLs, views, forms, templates, sessions, authentication, ORM, migrations and tests |
| HTML / Django templates | Page structure, server-rendered content, forms and reusable components |
| CSS | Layout, colours, typography, responsive cards, sidebar and chat presentation |
| JavaScript | Chat polling, browser interaction, signatures, voice recording and OTP countdown |
| SQLite | Persistent relational database in a db.sqlite3 file; no separate database server |
| Django ORM | Maps Python models and relationships to SQL tables and queries |
| ReportLab 4.4.9 | Generates offer-letter and agreement PDF documents |
| pypdf 6.18.0 | Reads/validates PDF structure in document workflows |
| Pillow 12.3.0 | Image validation and image/document processing support |
| asgiref 3.12.1 | Django sync/async integration dependency |
| sqlparse 0.6.0 | SQL parsing/formatting dependency |
| tzdata 2026.3 | Time-zone information |
| charset-normalizer 3.5.1 | Installed text/document dependency |
| Git | Source-code change history, separate from project activity and document versions |

requirements.txt pins dependencies. The usual Python interpreter on this laptop is C:\Users\Disha\Documents\Codex\2026-09-11\hi\work\.venv\Scripts\python.exe. Launchers prefer a project-local .venv when available and otherwise use this workspace environment. setup-demo.cmd prepares a local environment on a machine with Python installed. The environment contains libraries, not research records.

No React, Node backend, MongoDB, Firebase, Redis, Celery, external chat provider or paid AI API is required. Node was used for development syntax checks, not application hosting. Mentor matching is deterministic scoring, not trained AI. Chat uses HTTP polling, not a WebSocket service. SMTP is configurable but actual mailbox delivery has not been verified.

## 4. Architecture: from click to saved data

Django's model-template-view structure is supplemented by service files. Models define persistent data. Views receive requests and coordinate access checks, forms and responses. Templates produce HTML. Services hold business rules and transactions, keeping templates from deciding permissions or directly changing the database.

Example: task submission. A browser POST goes to a route in apps/tasks/urls.py. Middleware resolves the session, validates CSRF and checks profile completion. A view loads the community/task and validates the input form. services.py checks membership, assignee, state and revision; saves submission/evidence; records a history event and notification. SQLite receives structured rows, while upload storage receives bytes. The browser gets success only after the save succeeds.

GET is for reading; changes normally use POST. UUIDs identify records but do not authorize access. config/urls.py includes app URL files; specific task/chat/IP routes precede the generic community route. Five community cards use explicit named routes. To-do opens tasks:board; sprint planning has a separate link.

Middleware order: security → demo namespace → Django sessions → common handling → CSRF → authentication → messages → profile gate → clickjacking protection. Demo middleware maps cookies and URL prefixes per request. Profile middleware allows account/profile pages while blocking normal work until onboarding is complete.

Templates inherit base.html and layouts/member.html, reusing field/icon/message/pagination components. Django escapes normal rendered text. JavaScript enhances interaction, but server-side forms and permissions remain authoritative when requests bypass the UI.

## 5. Database location, tables and persistence

Live demo database:

```text
C:\Users\Disha\Documents\Codex\2026-09-11\hi\outputs\researchbridge\private\demo\db.sqlite3
```

config/settings/base.py defines SQLite and baseline storage. local.py chooses private/demo in demo mode. Base/real-mode defaults to private/db.sqlite3 unless configured otherwise; that is not the active demo DB. Production accepts RESEARCHBRIDGE_DATA_DIR.

SQLite stores users/password hashes, profiles, idea text, applications, task states, chat text, poll votes, notifications, signature evidence and file metadata. Uploaded file bytes are usually not inside the FileField database column: that field stores a relative path to a file on disk.

Typical table names are accounts_user, profiles_profile, projects_project, recruitment_application, agreements_agreementevidence, collaboration_chatmessage and tasks_task. django_session stores sessions; django_migrations records applied migrations. Many-to-many fields create joining tables for skills/departments and other collections. The model appendix documents the actual fields.

Primary keys identify rows. Foreign keys connect an applicant to an application and an application to its project. One-to-one relationships enforce one community per project or one letter per application. Unique constraints prevent duplicate logical relationships/actions. PROTECT preserves referenced evidence during ordinary ORM deletion. A reset instead starts a new database and archives the entire old one.

Migrations describe schema changes; they are not the saved user records. Run migrate before importing rosters. “No such table” usually means the migration phase failed. Django shell or an SQLite viewer can inspect a database copy. Some models have admin registrations, but not every entity is registered and a teacher is not automatically an admin. Use the app for demo changes so its events and validations run.

## 6. Every uploaded-data location

Upload root:

```text
C:\Users\Disha\Documents\Codex\2026-09-11\hi\outputs\researchbridge\private\demo\uploads
```

Patterns below are relative to that root. Identifiers vary; a folder appears when its first file is saved.

| Content | Relative folder/file pattern | Responsible model |
|---|---|---|
| Profile résumé | resumes/<user-id>/<random-id>.pdf | profiles.ResumeVersion |
| Application-uploaded résumé | applications/<applicant-id>/<random-id>.pdf | recruitment.Application; may instead reference an existing ResumeVersion |
| Private project PDF versions | projects/<project-id>/<random-id>.pdf | documents.ProjectDocument / DocumentVersion |
| Issued offer letter | letters/<application-id>/<letter-id>.pdf | recruitment.OfferLetter |
| Agreement evidence | agreements/<agreement-id>/<evidence-id>/evidence.pdf | agreements.AgreementEvidence |
| Physically signed agreement | agreements/<agreement-id>/<evidence-id>/signed-copy.pdf | AgreementEvidence.signed_copy |
| Chat attachments | chat/<community-id>/<attachment-id>/<stored-name> | collaboration.ChatAttachment linked to ChatMessage |
| Summary resources | community-resources/<community-id>/<resource-id>/<stored-name> | communities.SummaryResource |
| Task evidence | task-files/<year>/<month>/<stored-name> | tasks.TaskFile |
| IP progress attachment | ip-updates/<year>/<month>/<stored-name> | ip_progress.IPUpdate |

Chat text is in database rows, not a text file per conversation. Poll questions/options/votes are rows too. Media pages list the existing attachment records; they do not duplicate each file. Voice notes are audio attachments. Links refer to external locations rather than automatically downloading entire websites.

Drawn signature strokes are normalized coordinates saved in AgreementEvidence.signature JSON and rendered in the evidence PDF. Typed signatures record the name and signing method. Physical signatures store an uploaded signed PDF. Snapshot JSON stores student/project/terms context. Consent, timestamps, checksums and mentor reviews preserve the submitted evidence. The account password is checked during signing.

SHA-256 is a checksum, not encryption or a certificate-authority digital signature. Django-signed preview tokens protect workflow payloads from alteration. They do not certify the PDF through PKI/DSC or Aadhaar eSign. Describe this as electronic agreement evidence with mentor verification. Do not claim guaranteed legal enforceability or tamper-proof storage.

The original offer PDF remains archived; a printable version may use a newer design with the stored original details. Agreement corrections create new evidence rather than overwriting older signatures. Files are served through protected download views, not a public /media/ mapping. static/ holds CSS and JavaScript, not research uploads. Backups must include both database and uploads, with writers stopped.

## 7. Twenty implementation modules and their responsible files

All paths below start inside the project root. App code paths begin apps/. HTML templates are under templates/; browser assets are under static/.

### Module 1 — Foundation

manage.py is the command entry point. config/settings/base.py centralizes installed apps, middleware, SQLite, authentication, timezone, static/private paths and email configuration. local.py supplies local demo storage and a persistent development secret. production.py requires explicit production configuration. config/urls.py assembles app routes; wsgi.py and asgi.py are deployment entry points. requirements.txt records pinned packages. The result is a persistent, runnable Django foundation rather than a frontend-only mockup.

### Module 2 — Shared UI

base.html supplies shared assets. layouts/member.html supplies sidebar/topbar/account menu; layouts/workspace.html supplies the other workspace layout. components/*.html provide reusable icons, fields, empty states, messages and pagination. CSS is layered across base.css, refinement.css, studio.css and projects.css. ui.js handles navigation/interactions. core/preview.html is a development preview, not a working module. Later feature pages inherit these shared styles and layouts.

### Module 3 — University roster login and password reset

accounts/models.py defines User, OTPChallenge and AuthThrottle. validators.py normalizes college email; forms.py validates login/reset fields; services.py enforces registration, passwords, OTP binding and rate limits; views.py implements login/logout/reset pages; urls.py registers them. middleware.py isolates demo account tabs. accounts/management/commands/import_roster.py imports students/faculty JSON. templates/accounts and static/js/accounts.js implement the forms and countdown.

Flow: imported account → email/password login → profile gate. No public signup. Reset flow: email → challenge → OTP verification → new password/confirmation. Codes expire after three minutes, resend cooldown is sixty seconds, and a challenge permits five incorrect attempts. Rate-limit windows are fifteen minutes. Login limits are separately applied to email/IP. Real codes are securely random; demo uses 123456. Challenges are bound to the attempt, email and current password; replaced/used codes are consumed. Django stores password hashes, not plaintext. Real SMTP delivery remains unverified.

### Module 4 — Profiles and taxonomy

profiles/models.py defines Profile, Department, Skill, ResearchInterest and immutable ResumeVersion. forms.py validates role-specific profile fields and résumé input. views.py saves and serves profile records; middleware.py enforces onboarding. taxonomy.py defines departments. Students choose years 1–4. Departments: CSE, AIML, AIDS, BCA, MCA, EE, ECS, MECH, CIVIL, ROBOTICS. Teachers have approval state and research information. Résumé replacement creates a version so historical application references remain stable. templates/profiles/edit.html renders the profile form.

### Module 5 — Permissions and private files

core/permissions.py checks active college membership, completed profiles, approved teachers, idea management and confidential access. documents/models.py separates a logical ProjectDocument from its immutable DocumentVersion records. documents/forms.py validates uploads; services.py saves; views.py checks authorisation; security.py builds protected responses. A student's own résumé is accessed by ownership; applicant review uses the application-scoped snapshot. UUIDs are identifiers, not access keys. Staff status does not automatically grant private project access through these ordinary views.

### Module 6 — In-app notifications

notifications/models.py stores recipient, event key, title/body, project/application context and read timestamp. services.py creates idempotent records and resolves destinations using current permissions. views.py supplies list/read/poll endpoints. context_processors.py populates shared unread counts. templates/notifications/index.html renders the inbox; static/js/notifications.js refreshes the bell. Logout does not delete notifications. Stable event keys prevent duplicates on retries. A historical notification does not bypass revoked access.

### Module 7 — Idea creation and project records

projects/models.py separates Project recruitment fields from ConfidentialIdea. forms.py accepts recruitment/private input; services.py saves; views.py implements creation/editing, My Projects, Created Ideas and public/private detail views. templates/projects contains forms, cards and discovery/detail pages. Both eligible students and approved teachers create ideas. Student ideas enter mentor selection; teacher-created ideas use the teacher mentor path. Shared recruitment visibility means inside the authenticated college portal, not anonymous internet access to research.

### Module 8 — Mentor recommendations and requests

mentorship/models.py defines MentorSearch and MentorRequest. services.py ranks active approved teachers with completed profiles and matching demo/real mode. Score = 50 for research-interest match + 20 for department match + up to 30 for proportion of required skills matched. Ties use normalized teacher name then identifier. Visible reasons explain each score. The chosen teacher comes first, then ranked alternatives. Only the pending candidate is notified; rejection advances the queue, acceptance attaches the mentor and opens recruitment. Exhaustion is recorded/notified. Automatic no-response escalation is future scope. views.py and templates/mentorship provide suggestions, inbox and review. This is rule-based matching, not machine learning.

### Module 9 — Dashboard and project discovery

projects/discovery.py implements shared search/filter/sort queries. core/views.py assembles the dashboard. templates/projects/discover.html, discovery_results.html and card.html show actual recruiting opportunities. Filters cover department, domain and skill; sorting/search refine results. Confidential descriptions do not become public search material. Dashboard also includes persistent chat unread counts and explicitly approved achievements. Empty results remain truthful empty states.

### Module 10 — Applications and snapshots

recruitment/models.py Application stores applicant/project, status, motivation, academic score, profile snapshot and uploaded/reference résumé. forms.py validates input; services.py prepares drafts and final submission; views.py implements apply/detail/index and private résumé downloads. Students review before confirming submission. A later profile edit does not rewrite the submitted snapshot. Duplicate applications/invalid recruitment actions are rejected. Manual academic input works; optional AI résumé autofill is not implemented. templates/recruitment/apply.html, detail.html and index.html render this flow.

### Module 11 — Review, shortlisting and meetings

recruitment/review_forms.py, review_services.py and review_views.py handle management filters, shortlisting, selection, not-selected decisions and review reopening. ReviewDecision preserves actor/time/state changes. MeetingInvitation holds schedule, venue, optional HTTPS meeting link, message and cancellation history. manage.html, review_panel.html and meeting.html render the tools. Detailed résumé/contact review belongs to the approved project mentor; student proposers receive restricted overview access. Selection checks positions. Meeting records are not a built-in video call system.

### Module 12 — Offer letters

recruitment/letter_services.py creates signed previews and issues immutable letter records; letter_pdf.py renders the PDF; letter_views.py serves preview, issue, view and download. OfferLetter stores issued snapshot details. templates/recruitment/letter_issue.html, letter.html and letter_content.html present the letter. Mentor must Prepare → Preview → Issue: selection alone does not issue it. Notification reaches the student. There is no separate accept/decline flow. next_steps.html places offer/agreement actions prominently on the application page.

### Module 13 — Agreement signing and verification

agreements/templates.py stores agreement text/version. forms.py validates input; services.py manages snapshots, signing confirmation, evidence persistence and review; pdf.py creates PDFs; permissions.py checks eligibility/readiness; views.py exposes signing, checklist, evidence and downloads. static/js/agreements.js captures signature strokes. A selected student without an issued offer sees pending.html. After issuance they can sign electronically or upload a physically signed PDF. Password confirmation and consent precede submission. Mentor verification/correction is recorded separately. Evidence and review versions remain preserved. Signing does not itself create membership.

### Module 14 — Private community and leader

communities/models.py defines Community, Membership and CommunityEvent. services.py checks the intended roster, creates the community, admits students and records leader actions. permissions.py checks current membership and latest verified evidence. Approved mentor creates the community and appoints the leader. A student proposer joining the team must be explicitly included in the intended roster. Letters alone do not grant private membership. templates/communities/create.html shows readiness; detail.html is the five-card landing page.

### Module 15 — Research summary, documents and sprints

communities/summary_forms.py, summary_services.py and summary_views.py manage summary fields, custom sections, resources and sprint planning. ProjectSummary, SummarySection, SummaryResource and Sprint store these records. Mentors and eligible leaders edit; admitted members view. summary.html, edit.html, sprints.html and sprint_card.html render the UI. A sprint organizes a stage/time period; a task assigns specific work. SummaryResource preserves file/version metadata or an external reference link. The To-do card now points to the task board; sprint planning is accessible separately.

### Module 16 — Chat, media, polls and announcements

collaboration/models.py defines ChatMessage, ChatAttachment, Poll, PollOption, PollVote, Announcement, AnnouncementRevision and ChatReadState. services.py checks membership, request keys, reply context and vote/announcement permissions. uploads.py validates supported file structure and size. views.py serves chat/feed/send/read/media/poll/announcement endpoints and media ranges. static/js/chat.js implements periodic fetching, message submission, replies, recording and poll interactions. templates/collaboration renders messages, polls, media and announcements.

All authorised participants can send messages and vote. The active feed normally polls every three seconds. Older messages load on demand. A poll has one choice per member; select then Save vote, and change it while open. Creator/managers can close/reopen. Revisions prevent stale background results overwriting newer ones. The earlier form.action button-name collision was fixed by reading the action attribute explicitly.

Supported attachments include photos, PDF/Office documents, text/CSV/JSON/ZIP, common audio and video. Relevant chat/task batches allow up to five files, 25 MB each and 60 MB total. It is not unrestricted executable upload. Browser microphone permission enables voice recording; playback support depends on browser codecs. Structural validation is not antivirus scanning. The system does not provide WhatsApp's complete features, calls, end-to-end encryption or WebSocket push. Mentors/leaders manage announcements and revisions; other members read them.

### Module 17 — Tasks, evidence and reviews

tasks/models.py defines Task, TaskFile, Submission, Review and TaskComment. forms.py validates assignment/actions; services.py handles work progress, blockers, evidence, submit, approve, request changes, reopen and comments; views.py supplies board/detail/forms/downloads. templates/tasks/board.html and checklist_row.html show tasks and completed views; detail.html provides evidence/discussion. States include assigned, progress, submitted, changes and approved. Assignees submit work; mentors/leaders review. Submission is not approval. Revision counters catch stale edits. New submissions/file versions retain earlier evidence rather than replacing it silently.

### Module 18 — History, versions and contributions

communities/history_views.py combines lifecycle, workspace, task and file records into a timeline. history.html opens as a separate page with compact changed-field details, actor/time and filters for member/sprint/type/date. library.html groups document versions; contributions.html displays uploads/submissions/reviews/approved work. These counts reflect saved activity, not automatic authorship or ownership decisions. Older versions remain accessible to authorised users. ChatReadState plus static/js/chat-unread.js supplies persistent dashboard unread-message counts.

### Module 19 — Completion and IP outcomes

ip_progress/models.py defines Completion, IPUpdate and Achievement. forms.py validates action notes, confirmation and publication fields. services.py handles requests, mentor completion, reopening, private IP updates and explicit achievement publication/withdrawal. views.py serves the private page and shared approved achievement query. Completion closes recruitment while preserving community work. Reopening research does not automatically reopen recruitment. Whole-project completion is distinct from individual task approval.

Mentors post reported IP progress, requested information, task references and attachments. The system does not file patents or determine ownership. Shared achievements use separately entered/approved fields; private IP text/files are never automatically published. Default display window is 365 days. The mentor can withdraw an achievement. templates/ip_progress/overview.html, form.html and achievements.html render these flows.

### Module 20 — Verification, operations and release preparation

core/backup.py checks SQLite integrity, computes file checksums, writes backup manifests and restores to new directories. backup_workspace/restore_workspace management commands expose it; test_release.py verifies behaviour. /health/ tests DB connectivity. setup-demo.cmd prepares dependencies; start-demo.cmd starts the local server; new reset-demo.cmd safely archives and rebuilds the local demo. .env.example describes environment settings but is not automatically loaded. Production settings/static collection/deployment checks have been prepared; real hosting, HTTPS/domain setup and verified SMTP are still external tasks. Passing tests demonstrates checked behaviours, not a guarantee of zero defects.

## 8. Roles, permissions and important states

| Action | Required relationship or role |
|---|---|
| Login | Active imported roster account in the configured mode |
| Create idea | Completed student profile or approved/completed teacher |
| Manage idea | Creator or approved project mentor |
| View shared notice | Eligible authenticated college user, subject to publication state |
| View confidential details | Authorised creator/mentor or eligible admitted community participant |
| Review applicants / issue letters | Approved project mentor |
| Sign agreement | Eligible selected student after issuance, or explicitly enrolled proposer pathway |
| Verify agreement / create community | Approved project mentor |
| Appoint leader | Project mentor |
| Chat / reply / vote | Eligible community participant |
| Edit summary/sprints/tasks/announcements | Mentor or eligible appointed leader, with action-specific checks |
| Submit task work | Assigned member under the task state rules |
| Confirm completion / publish IP / approve achievement | Project mentor; manager can request completion |

Permissions combine role, relationship and current state. A teacher is not automatically reviewer for every project. Selected, offer issued, agreement submitted, verified and admitted are distinct states. Hiding buttons helps usability; server checks enforce access. Many denied private requests return 404 to avoid revealing whether the record exists.

## 9. Consistency and security

Transactions group related database changes. Request UUIDs/event keys make important actions idempotent: repeating the same request does not create a new logical record. Unique constraints protect relationships such as one vote per poll/member. Revision counters reject stale form submissions rather than silently overwriting newer changes. Selected services issue a write before fetching to serialize competing SQLite actions. SQLite is appropriate to this small demo, not unlimited college-wide concurrency.

Django hashes passwords and manages sessions. Session cookies are HttpOnly; CSRF protects changes; production settings require secure deployment configuration. Demo runs on local HTTP. OTP challenges expire and are bound to the browser attempt/email/password. Signing requires password confirmation and consent. Private downloads check current permissions and file paths. Upload validators constrain file types/sizes and archive structure. These checks are not antivirus scanning, encryption at rest or a certified signing service.

Model save guards and preserved versions reduce accidental evidence overwrites through ordinary code. They do not defeat a person with unrestricted DB/filesystem access. Keep private/ and credentials out of Git. Back up database and files together while writers are stopped. A public /static/ folder must never expose private/uploads.

## 10. Recommended presentation flow

For the shortest complete demo, use a teacher-created project and explain student mentor matching separately. Complete the accounts' profiles before attempting recruitment. Use matching skills/interests to make the recommendation example meaningful.

1. Explain roster login and show student/teacher accounts in separate demo tabs.
2. Show completed profiles, department, skills/interests, year/availability and résumé.
3. Create an idea with shared recruitment fields and separate private details. For the student-idea branch, request a mentor and show acceptance.
4. Another student discovers it, prepares an application, reviews the snapshot and confirms submission.
5. Mentor reviews the preserved résumé, shortlists and finalizes selection. Show an optional meeting invitation if time allows.
6. Mentor prepares, previews and issues the offer letter. Do not skip issuance.
7. Student signs the agreement, confirms password/consent and submits the electronic preview or physical PDF. Mentor verifies it.
8. Mentor creates the community after the agreement checklist passes, explicitly includes a joining student proposer if relevant, and appoints a leader.
9. Open all five cards. Show sprint planning via its separate link.
10. Create/assign a task, save progress, upload evidence and submit. Reviewer approves or requests changes. Show Completed only after approval.
11. Send a message between accounts. Create a poll, vote and change vote. Show the media library and an authorised file download.
12. Show project history, document versions and recorded contributions.
13. Confirm project completion, post private IP progress, explicitly approve a separate achievement and show the dashboard.
14. Explain that logout/restart preserves data; reset is a deliberate separate operation.

Remember: selected is not offer-issued; signed is not verified; verified is not community-created; submitted work is not approved work; private IP progress is not a public achievement.

## 11. Troubleshooting for tomorrow

| Symptom | What to check |
|---|---|
| Browser cannot connect | Run start-demo.cmd; keep CMD open; use port 8000 |
| Address already in use | Another server is running; stop it before starting another |
| Error mentions app label && | Old pasted multiline command failed; use reset-demo.cmd instead |
| No such table | Migration did not finish; read the first error before importing |
| Selected student cannot sign | Mentor must issue the offer letter; agreement pending page explains this |
| Community creation blocked | All intended students need latest verified agreement evidence |
| Task not counted completed | Submitted work still needs reviewer approval |
| Mentor absent from suggestions | Check approved/completed teacher profile and matching demo mode |
| Chat account changed | Use Open another account rather than changing a shared tab's login |
| Poll choice not saved | Voting must be open; select then Save vote; refresh stale assets if necessary |
| Missing files after copying | Need matching SQLite database AND uploads, not source alone |
| OTP email not received | Local mode intentionally simulates OTP; real mailbox setup is pending |
| Reset stops at server check | Stop servers first, including custom ports |

## 12. Viva answers

**Why Django?** It provides authentication, forms, routing, templates, ORM, migrations and tests, while business workflows remain readable Python services.

**Why SQLite?** It is persistent, relational and simple to demonstrate without a separate server. A future PostgreSQL migration is possible through Django with migration and concurrency testing. The present demo does not claim unlimited scalability.

**Is Excel or MongoDB used?** No. Fictional university accounts start in JSON rosters and are imported into SQLite. Live records are not stored in Excel. MongoDB is not part of this implementation.

**Where is the signature?** Structured signature/name/consent/snapshot data is in AgreementEvidence; PDF evidence and any physical signed copy are in private/demo/uploads/agreements. Mentor reviews are separate rows.

**Is matching AI?** No. It is a weighted, deterministic recommendation based on shared interest, department and skills, with visible reasons.

**Is chat real-time?** It uses periodic asynchronous HTTP polling, normally around three seconds for the active chat. It feels live, but it is not a WebSocket/push architecture.

**Does logout delete work?** No. Logout ends the session. SQLite records and uploaded files remain for the next login.

**Why split public and confidential fields?** A recruitment notice must attract suitable applicants without revealing the complete research idea. Private access is checked separately.

**How do votes and retries avoid duplicates?** Unique constraints and update logic maintain one vote per member; request keys and transactions protect repeated workflow actions.

**How is history created?** Successful actions create event/review records and immutable versions. The history page reads them and supports filters; it is not a manually maintained logbook.

**Is signing certified, or are patents filed automatically?** No. Electronic/physical agreement evidence and mentor verification are implemented. IP Progress tracks reported institutional progress. Certified signing and legal filing integrations are outside this demo.

**What remains external or future scope?** Public deployment/HTTPS/domain/storage configuration and verified real SMTP delivery. Optional résumé autofill, no-response mentor escalation and successor-batch handover are not implemented. Do not present those as finished features.

**How is code organized?** Each app groups models/forms/services/views/URLs for a business area. Feature templates/static files provide the UI. Configuration, migrations, tests and operations are separate.

## 13. How to read the code during explanation

Follow config/urls.py → feature urls.py → view → form and permission helper → service → model → template → relevant JavaScript. This follows a click to its save and feedback. For selection read recruitment/review_*; for signing read agreements; for chat read collaboration; for task review read tasks.

All appendix paths are relative to the project root in section 2. The file index covers project-owned source, configuration, templates, assets, migrations, tests and documentation. It excludes virtual-environment dependencies, Git internals, Python caches, generated static copies and private user content. Those folders are described by function rather than exposing passwords, development secrets or personal files.

## 14. Tests and operational boundaries

The last complete regression run before the agreement-navigation addition passed 159 tests, including separate demo sessions. The agreement fix subsequently passed its 12-test targeted suite, and direct community navigation passed 6 community tests. These are historical run results, not a fresh claim that every possible interaction is error-free. The reusable reset was additionally exercised on an isolated temporary project copy during preparation of this guide; current demonstration records were not used for that test.

The checksum backup commands are different from the reset archive. backup_workspace writes a manifest and checks file hashes/SQLite integrity. reset-demo.cmd preserves the entire stopped demo folder by renaming it before creating the new one. It does not claim to create a checksum manifest. Both keep the previous data, but only the backup utility implements manifest verification.

Normal backup/restore commands, with servers stopped and your virtual environment Python selected:

```cmd
python manage.py backup_workspace private/backups/my-new-backup --writers-stopped
python manage.py restore_workspace private/backups/my-new-backup private/restored-workspace
```

Use new destination names. Restore refuses to overwrite existing directories. Keep source/migrations separately in Git. Production secrets belong in private host configuration. .env.example is a reference file, not automatically loaded; do not claim that editing it alone configures runtime environment variables.


## Appendix A — Actual database model and field reference

Generated from the current Django model definitions. No personal database contents are included. A column may hold a reference/path rather than the full linked object/file. Blank/null fields are optional as defined by the model; forms can impose additional workflow rules. Many-to-many fields use joining tables.

### accounts models

#### User — accounts_user

Source: apps/accounts/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| password | CharField | password |
| last_login | DateTimeField | last login; optional at model level |
| is_superuser | BooleanField | superuser status |
| email | CharField | email; unique |
| roster_role | CharField | roster role; optional at model level; choices: student = Student, teacher = Teacher |
| is_active | BooleanField | is active |
| is_staff | BooleanField | is staff |
| date_joined | DateTimeField | date joined |
| email_verified_at | DateTimeField | email verified at; optional at model level |
| is_demo | BooleanField | is demo |
| groups | ManyToManyField | groups → auth.Group; optional at model level |
| user_permissions | ManyToManyField | user permissions → auth.Permission; optional at model level |

Named constraints: accounts_email_case_insensitive_unique.

#### OTPChallenge — accounts_otpchallenge

Source: apps/accounts/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| email | CharField | email |
| binding | CharField | binding |
| code_digest | CharField | code digest |
| mode | CharField | mode |
| created_at | DateTimeField | created at |
| expires_at | DateTimeField | expires at |
| attempts | PositiveSmallIntegerField | attempts |
| consumed | BooleanField | consumed |

#### AuthThrottle — accounts_auththrottle

Source: apps/accounts/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| key | CharField | key; primary key |
| started_at | DateTimeField | started at |
| count | PositiveIntegerField | count |

### profiles models

#### Department — profiles_department

Source: apps/profiles/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| name | CharField | name; unique |
| is_demo | BooleanField | is demo |

#### Skill — profiles_skill

Source: apps/profiles/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| name | CharField | name; unique |

#### ResearchInterest — profiles_researchinterest

Source: apps/profiles/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| name | CharField | name; unique |

#### Profile — profiles_profile

Source: apps/profiles/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| user | OneToOneField | user → accounts.User; unique |
| role | CharField | role; choices: student = Student, teacher = Teacher |
| name | CharField | name; optional at model level |
| department | ForeignKey | department → profiles.Department; optional at model level |
| phone | CharField | phone; optional at model level |
| availability | PositiveSmallIntegerField | availability; optional at model level |
| year | PositiveSmallIntegerField | year; optional at model level |
| previous_research | TextField | previous research; optional at model level |
| scholar_url | CharField | scholar url; optional at model level |
| teacher_approved | BooleanField | teacher approved |
| completed_at | DateTimeField | completed at; optional at model level |
| updated_at | DateTimeField | updated at; optional at model level |
| skills | ManyToManyField | skills → profiles.Skill; optional at model level |
| interests | ManyToManyField | interests → profiles.ResearchInterest; optional at model level |

#### ResumeVersion — profiles_resumeversion

Source: apps/profiles/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| profile | ForeignKey | profile → profiles.Profile |
| file | FileField | file; private storage via resume_path |
| original_name | CharField | original name |
| created_at | DateTimeField | created at; optional at model level |

### projects models

#### Project — projects_project

Source: apps/projects/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| creator | ForeignKey | creator → accounts.User |
| mentor | ForeignKey | mentor → accounts.User; optional at model level |
| creation_key | UUIDField | creation key |
| title | CharField | title |
| domain | ForeignKey | domain → profiles.ResearchInterest |
| short_description | CharField | short description |
| open_positions | PositiveSmallIntegerField | open positions |
| available_roles | CharField | available roles; optional at model level |
| status | CharField | status; choices: draft = Draft, pending_mentor = Awaiting mentor, recruiting = Recruiting, closed = Recruitment closed |
| revision | PositiveIntegerField | revision |
| created_at | DateTimeField | created at; optional at model level |
| updated_at | DateTimeField | updated at; optional at model level |
| departments | ManyToManyField | departments → profiles.Department |
| skills | ManyToManyField | skills → profiles.Skill |

Named constraints: unique_idea_submission, valid_project_positions, published_project_has_mentor.

#### ConfidentialIdea — projects_confidentialidea

Source: apps/projects/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| project | OneToOneField | project → projects.Project; primary key |
| details | TextField | details; optional at model level |
| updated_at | DateTimeField | updated at; optional at model level |

### mentorship models

#### MentorSearch — mentorship_mentorsearch

Source: apps/mentorship/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| project | OneToOneField | project → projects.Project; unique |
| state | CharField | state; choices: pending = Pending response, accepted = Mentor attached, exhausted = No remaining candidate |
| created_at | DateTimeField | created at; optional at model level |
| updated_at | DateTimeField | updated at; optional at model level |

#### MentorRequest — mentorship_mentorrequest

Source: apps/mentorship/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| search | ForeignKey | search → mentorship.MentorSearch |
| teacher | ForeignKey | teacher → accounts.User |
| position | PositiveIntegerField | position |
| score | PositiveSmallIntegerField | score |
| reasons | JSONField | reasons |
| state | CharField | state; choices: queued = Queued, pending = Pending response, accepted = Accepted, rejected = Rejected, skipped = Skipped |
| sent_at | DateTimeField | sent at; optional at model level |
| decided_at | DateTimeField | decided at; optional at model level |

Named constraints: unique_mentor_candidate, unique_mentor_position, one_active_mentor_request.

### recruitment models

#### OfferLetter — recruitment_offerletter

Source: apps/recruitment/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| application | OneToOneField | application → recruitment.Application; unique |
| issued_by | ForeignKey | issued by → accounts.User |
| issued_at | DateTimeField | issued at |
| snapshot | JSONField | snapshot |
| pdf | FileField | pdf; private storage via letter_path |
| sha256 | CharField | sha256 |

#### Application — recruitment_application

Source: apps/recruitment/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| project | ForeignKey | project → projects.Project |
| applicant | ForeignKey | applicant → accounts.User |
| status | CharField | status; choices: draft = Draft, submitted = Submitted, shortlisted = Shortlisted, selected = Selected, not_selected = Not selected |
| profile_resume | ForeignKey | profile resume → profiles.ResumeVersion; optional at model level |
| uploaded_resume | FileField | uploaded resume; optional at model level; private storage via application_path |
| resume_name | CharField | resume name |
| snapshot | JSONField | snapshot |
| motivation | TextField | motivation |
| academic_score | CharField | academic score; optional at model level |
| revision | PositiveIntegerField | revision |
| created_at | DateTimeField | created at; optional at model level |
| submitted_at | DateTimeField | submitted at; optional at model level |

Named constraints: one_application_per_student, application_one_resume_source.

#### ReviewDecision — recruitment_reviewdecision

Source: apps/recruitment/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| application | ForeignKey | application → recruitment.Application |
| actor | ForeignKey | actor → accounts.User |
| action | CharField | action |
| previous_status | CharField | previous status; choices: draft = Draft, submitted = Submitted, shortlisted = Shortlisted, selected = Selected, not_selected = Not selected |
| new_status | CharField | new status; choices: draft = Draft, submitted = Submitted, shortlisted = Shortlisted, selected = Selected, not_selected = Not selected |
| request_key | UUIDField | request key |
| created_at | DateTimeField | created at; optional at model level |

Named constraints: unique_application_review_key.

#### MeetingInvitation — recruitment_meetinginvitation

Source: apps/recruitment/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| application | ForeignKey | application → recruitment.Application |
| created_by | ForeignKey | created by → accounts.User |
| request_key | UUIDField | request key |
| message | TextField | message |
| scheduled_at | DateTimeField | scheduled at |
| venue | CharField | venue |
| online_url | CharField | online url; optional at model level |
| created_at | DateTimeField | created at; optional at model level |
| cancelled_at | DateTimeField | cancelled at; optional at model level |
| cancelled_by | ForeignKey | cancelled by → accounts.User; optional at model level |

Named constraints: unique_meeting_invitation_key.

### agreements models

#### Agreement — agreements_agreement

Source: apps/agreements/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| project | ForeignKey | project → projects.Project |
| student | ForeignKey | student → accounts.User |
| enrolled_by | ForeignKey | enrolled by → accounts.User |
| enrollment_reason | CharField | enrollment reason |
| created_at | DateTimeField | created at; optional at model level |

Named constraints: one_agreement_per_student_project.

#### AgreementEvidence — agreements_agreementevidence

Source: apps/agreements/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| agreement | ForeignKey | agreement → agreements.Agreement |
| request_key | UUIDField | request key; unique |
| snapshot | JSONField | snapshot |
| method | CharField | method; choices: typed = Typed signature, drawn = Drawn signature, physical = Physical signed copy |
| name | CharField | name |
| signature | JSONField | signature |
| consent | TextField | consent |
| created_at | DateTimeField | created at |
| pdf | FileField | pdf; private storage via evidence_path |
| signed_copy | FileField | signed copy; optional at model level; private storage via evidence_path |
| sha256 | CharField | sha256 |
| copy_sha256 | CharField | copy sha256; optional at model level |

#### AgreementReview — agreements_agreementreview

Source: apps/agreements/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| evidence | ForeignKey | evidence → agreements.AgreementEvidence |
| actor | ForeignKey | actor → accounts.User |
| action | CharField | action; choices: verified = Verified, correction = Correction requested |
| reason | CharField | reason |
| request_key | UUIDField | request key; unique |
| created_at | DateTimeField | created at; optional at model level |

### communities models

#### Community — communities_community

Source: apps/communities/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| project | OneToOneField | project → projects.Project; unique |
| created_by | ForeignKey | created by → accounts.User |
| created_at | DateTimeField | created at; optional at model level |
| leader | ForeignKey | leader → accounts.User; optional at model level |
| revision | PositiveIntegerField | revision |

#### Membership — communities_membership

Source: apps/communities/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | ForeignKey | community → communities.Community |
| user | ForeignKey | user → accounts.User |
| role | CharField | role; choices: mentor = Mentor, student = Student |
| admitted_evidence | ForeignKey | admitted evidence → agreements.AgreementEvidence; optional at model level |
| joined_at | DateTimeField | joined at; optional at model level |

Named constraints: unique_community_member.

#### CommunityEvent — communities_communityevent

Source: apps/communities/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| actor_name | CharField | actor name; optional at model level |
| community | ForeignKey | community → communities.Community |
| actor | ForeignKey | actor → accounts.User |
| action | CharField | action |
| details | JSONField | details |
| request_key | UUIDField | request key; unique |
| created_at | DateTimeField | created at; optional at model level |

#### ProjectSummary — communities_projectsummary

Source: apps/communities/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | OneToOneField | community → communities.Community; unique |
| description | TextField | description; optional at model level |
| problem | TextField | problem; optional at model level |
| objectives | TextField | objectives; optional at model level |
| existing_solutions | TextField | existing solutions; optional at model level |
| research_gap | TextField | research gap; optional at model level |
| progress_notes | TextField | progress notes; optional at model level |

#### SummarySection — communities_summarysection

Source: apps/communities/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | ForeignKey | community → communities.Community |
| title | CharField | title |
| content | TextField | content |
| order | PositiveIntegerField | order |

#### Sprint — communities_sprint

Source: apps/communities/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| community | ForeignKey | community → communities.Community |
| title | CharField | title |
| goal | TextField | goal |
| order | PositiveIntegerField | order |
| start_date | DateField | start date; optional at model level |
| end_date | DateField | end date; optional at model level |
| status | CharField | status; choices: planned = Planned, active = Active, completed = Completed |
| notes | TextField | notes; optional at model level |

Named constraints: one_active_sprint, sprint_dates_ordered.

#### SummaryResource — communities_summaryresource

Source: apps/communities/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| replaces | OneToOneField | replaces → communities.SummaryResource; unique; optional at model level |
| version | PositiveIntegerField | version |
| revision_note | CharField | revision note; optional at model level |
| uploader_name | CharField | uploader name; optional at model level |
| id | UUIDField | id; primary key |
| community | ForeignKey | community → communities.Community |
| title | CharField | title |
| category | CharField | category; choices: presentation = Presentation, paper = Literature paper, reference = Reference |
| url | CharField | url; optional at model level |
| file | FileField | file; optional at model level; private storage via resource_path |
| filename | CharField | filename; optional at model level |
| mime_type | CharField | mime type; optional at model level |
| sha256 | CharField | sha256; optional at model level |
| size | PositiveIntegerField | size |
| added_by | ForeignKey | added by → accounts.User |
| created_at | DateTimeField | created at; optional at model level |

Named constraints: resource_one_source.

### tasks models

#### Task — tasks_task

Source: apps/tasks/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| community | ForeignKey | community → communities.Community |
| sprint | ForeignKey | sprint → communities.Sprint; optional at model level |
| title | CharField | title |
| description | TextField | description |
| milestone | CharField | milestone; optional at model level |
| assignee | ForeignKey | assignee → accounts.User |
| created_by | ForeignKey | created by → accounts.User |
| due_date | DateField | due date; optional at model level |
| status | CharField | status; choices: assigned = Assigned, progress = In progress, submitted = Awaiting review, changes = Changes requested, approved = Approved |
| progress_notes | TextField | progress notes; optional at model level |
| blocker | TextField | blocker; optional at model level |
| revision | PositiveIntegerField | revision |
| created_at | DateTimeField | created at; optional at model level |
| updated_at | DateTimeField | updated at; optional at model level |

#### TaskFile — tasks_taskfile

Source: apps/tasks/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| replaces | OneToOneField | replaces → tasks.TaskFile; unique; optional at model level |
| version | PositiveIntegerField | version |
| revision_note | CharField | revision note; optional at model level |
| uploader_name | CharField | uploader name; optional at model level |
| id | UUIDField | id; primary key |
| task | ForeignKey | task → tasks.Task |
| uploader | ForeignKey | uploader → accounts.User |
| file | FileField | file; private storage via task-files/%Y/%m/ |
| filename | CharField | filename |
| mime | CharField | mime |
| sha256 | CharField | sha256 |
| size | PositiveIntegerField | size |
| created_at | DateTimeField | created at; optional at model level |

#### Submission — tasks_submission

Source: apps/tasks/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| task | ForeignKey | task → tasks.Task |
| submitter | ForeignKey | submitter → accounts.User |
| number | PositiveIntegerField | number |
| summary | TextField | summary |
| created_at | DateTimeField | created at; optional at model level |
| files | ManyToManyField | files → tasks.TaskFile; optional at model level |

Named constraints: task_submission_number.

#### Review — tasks_review

Source: apps/tasks/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| submission | OneToOneField | submission → tasks.Submission; unique |
| reviewer | ForeignKey | reviewer → accounts.User |
| decision | CharField | decision; choices: approved = Approve, changes = Request changes |
| feedback | TextField | feedback |
| created_at | DateTimeField | created at; optional at model level |

#### TaskComment — tasks_taskcomment

Source: apps/tasks/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| task | ForeignKey | task → tasks.Task |
| author | ForeignKey | author → accounts.User |
| file | ForeignKey | file → tasks.TaskFile; optional at model level |
| body | TextField | body |
| created_at | DateTimeField | created at; optional at model level |

### documents models

#### ProjectDocument — documents_projectdocument

Source: apps/documents/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| project | ForeignKey | project → projects.Project |
| title | CharField | title |
| created_at | DateTimeField | created at; optional at model level |

#### DocumentVersion — documents_documentversion

Source: apps/documents/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| uploader_name | CharField | uploader name; optional at model level |
| id | UUIDField | id; primary key |
| document | ForeignKey | document → documents.ProjectDocument |
| version | PositiveIntegerField | version |
| uploader | ForeignKey | uploader → accounts.User |
| file | FileField | file; private storage via document_path |
| original_name | CharField | original name |
| size | PositiveIntegerField | size |
| sha256 | CharField | sha256 |
| created_at | DateTimeField | created at; optional at model level |

Named constraints: unique_document_version.

### collaboration models

#### ChatMessage — collaboration_chatmessage

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | ForeignKey | community → communities.Community |
| sender | ForeignKey | sender → accounts.User |
| sender_name | CharField | sender name |
| text | TextField | text; optional at model level |
| reply_to | ForeignKey | reply to → collaboration.ChatMessage; optional at model level |
| request_key | UUIDField | request key |
| created_at | DateTimeField | created at; optional at model level |

Named constraints: unique_chat_send.

#### ChatAttachment — collaboration_chatattachment

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| message | ForeignKey | message → collaboration.ChatMessage |
| file | FileField | file; private storage via attachment_path |
| filename | CharField | filename |
| kind | CharField | kind |
| mime | CharField | mime |
| size | PositiveIntegerField | size |
| sha256 | CharField | sha256 |

#### Poll — collaboration_poll

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| revision | PositiveIntegerField | revision |
| message | OneToOneField | message → collaboration.ChatMessage; unique |
| question | CharField | question |
| closed | BooleanField | closed |

#### PollOption — collaboration_polloption

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| poll | ForeignKey | poll → collaboration.Poll |
| text | CharField | text |
| order | PositiveSmallIntegerField | order |

#### PollVote — collaboration_pollvote

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| poll | ForeignKey | poll → collaboration.Poll |
| voter | ForeignKey | voter → accounts.User |
| option | ForeignKey | option → collaboration.PollOption |
| updated_at | DateTimeField | updated at; optional at model level |

Named constraints: one_vote_per_poll_member.

#### Announcement — collaboration_announcement

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | ForeignKey | community → communities.Community |
| author | ForeignKey | author → accounts.User |
| title | CharField | title |
| message | TextField | message |
| revision | PositiveIntegerField | revision |
| created_at | DateTimeField | created at; optional at model level |
| updated_at | DateTimeField | updated at; optional at model level |

#### AnnouncementRevision — collaboration_announcementrevision

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| announcement | ForeignKey | announcement → collaboration.Announcement |
| actor | ForeignKey | actor → accounts.User |
| title | CharField | title |
| message | TextField | message |
| request_key | UUIDField | request key; unique |
| created_at | DateTimeField | created at; optional at model level |

#### ChatReadState — collaboration_chatreadstate

Source: apps/collaboration/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | ForeignKey | community → communities.Community |
| user | ForeignKey | user → accounts.User |
| last_message_id | PositiveBigIntegerField | last message id |

Named constraints: unique_chat_read_state.

### notifications models

#### Notification — notifications_notification

Source: apps/notifications/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| recipient | ForeignKey | recipient → accounts.User |
| event_key | CharField | event key |
| title | CharField | title |
| message | CharField | message; optional at model level |
| project | ForeignKey | project → projects.Project; optional at model level |
| application | ForeignKey | application → recruitment.Application; optional at model level |
| created_at | DateTimeField | created at; optional at model level |
| read_at | DateTimeField | read at; optional at model level |

Named constraints: unique_notification_event.

### ip_progress models

#### Completion — ip_progress_completion

Source: apps/ip_progress/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | OneToOneField | community → communities.Community; unique |
| state | CharField | state; choices: active = Active research, requested = Completion requested, completed = Completed |
| note | TextField | note; optional at model level |
| confirmed_by | ForeignKey | confirmed by → accounts.User; optional at model level |
| completed_at | DateTimeField | completed at; optional at model level |
| revision | PositiveIntegerField | revision |

#### IPUpdate — ip_progress_ipupdate

Source: apps/ip_progress/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | UUIDField | id; primary key |
| community | ForeignKey | community → communities.Community |
| author | ForeignKey | author → accounts.User |
| author_name | CharField | author name |
| title | CharField | title |
| status_label | CharField | status label |
| message | TextField | message |
| required_information | TextField | required information; optional at model level |
| reference | CharField | reference; optional at model level |
| task | ForeignKey | task → tasks.Task; optional at model level |
| file | FileField | file; optional at model level; private storage via ip-updates/%Y/%m/ |
| filename | CharField | filename; optional at model level |
| mime | CharField | mime; optional at model level |
| sha256 | CharField | sha256; optional at model level |
| created_at | DateTimeField | created at; optional at model level |

#### Achievement — ip_progress_achievement

Source: apps/ip_progress/models.py

| Field | Storage/type | Meaning / relationship |
|---|---|---|
| id | BigAutoField | ID; primary key; optional at model level |
| community | ForeignKey | community → communities.Community |
| approved_by | ForeignKey | approved by → accounts.User |
| title | CharField | title |
| status_label | CharField | status label |
| public_summary | TextField | public summary |
| milestone_date | DateField | milestone date |
| visible | BooleanField | visible |
| created_at | DateTimeField | created at; optional at model level |

## Appendix B — Actual URL / view map

These are unprefixed application routes. Independent demo sessions add /demo/<identifier> before application URLs. Path placeholders represent record identifiers, not literal text to enter. Access checks remain in the views/services.

| URL pattern | Named route | Responsible callable |
|---|---|---|
| /health/ | health | apps.core.views.health |
| / | (unnamed) | django.views.generic.base.view |
| /accounts/demo-session/ | accounts:demo-session | apps.accounts.views.new_demo_session |
| /accounts/login/ | accounts:login | apps.accounts.views.sign_in |
| /accounts/forgot-password/ | accounts:forgot | apps.accounts.views.forgot |
| /accounts/verify/ | accounts:verify | apps.accounts.views.verify |
| /accounts/resend/ | accounts:resend | apps.accounts.views.resend |
| /accounts/reset-password/ | accounts:reset | apps.accounts.views.reset_password |
| /accounts/logout/ | accounts:logout | apps.accounts.views.sign_out |
| /dashboard/ | dashboard | apps.core.views.dashboard |
| /profile/ | profiles:edit | apps.profiles.views.edit |
| /profile/resumes/<int:pk>/ | profiles:resume | apps.profiles.views.resume_download |
| /mentorship/ | mentorship:inbox | apps.mentorship.views.inbox |
| /mentorship/ideas/<uuid:pk>/ | mentorship:suggestions | apps.mentorship.views.suggestions |
| /mentorship/requests/<int:pk>/ | mentorship:review | apps.mentorship.views.review |
| /communities/<uuid:pk>/ip/ | ip_progress:overview | apps.ip_progress.views.overview |
| /communities/<uuid:pk>/ip/files/<uuid:record_id>/ | ip_progress:download | apps.ip_progress.views.download |
| /communities/<uuid:pk>/ip/achievement/<int:record_id>/withdraw/ | ip_progress:withdraw | apps.ip_progress.views.action |
| /communities/<uuid:pk>/ip/<str:action>/ | ip_progress:action | apps.ip_progress.views.action |
| /communities/<uuid:pk>/tasks/ | tasks:board | apps.tasks.views.board |
| /communities/<uuid:pk>/tasks/new/ | tasks:new | apps.tasks.views.edit |
| /communities/<uuid:pk>/tasks/files/<uuid:file_id>/ | tasks:download | apps.tasks.views.download |
| /communities/<uuid:pk>/tasks/<uuid:task_id>/ | tasks:detail | apps.tasks.views.detail |
| /communities/<uuid:pk>/tasks/<uuid:task_id>/edit/ | tasks:edit | apps.tasks.views.edit |
| /communities/<uuid:pk>/tasks/<uuid:task_id>/<str:action>/ | tasks:action | apps.tasks.views.action |
| /communities/chat-unread/ | collaboration:unread | apps.collaboration.views.unread |
| /communities/<uuid:pk>/chat/read/ | collaboration:read | apps.collaboration.views.mark_read |
| /communities/<uuid:pk>/chat/feed/ | collaboration:feed | apps.collaboration.views.feed |
| /communities/<uuid:pk>/chat/send/ | collaboration:send | apps.collaboration.views.post |
| /communities/<uuid:pk>/chat/polls/<int:poll_id>/ | collaboration:poll | apps.collaboration.views.poll_action |
| /communities/<uuid:pk>/chat/media/ | collaboration:media | apps.collaboration.views.media |
| /communities/<uuid:pk>/chat/files/<uuid:attachment_id>/ | collaboration:attachment | apps.collaboration.views.attachment |
| /communities/<uuid:pk>/announcements/new/ | collaboration:announcement-new | apps.collaboration.views.announcement_edit |
| /communities/<uuid:pk>/announcements/<int:record_id>/edit/ | collaboration:announcement-edit | apps.collaboration.views.announcement_edit |
| /communities/<uuid:pk>/announcements/ | collaboration:announcements | apps.collaboration.views.announcements |
| /communities/<uuid:pk>/chat/ | collaboration:chat | apps.collaboration.views.chat |
| /communities/<uuid:pk>/history/ | communities:history | apps.communities.history_views.history |
| /communities/<uuid:pk>/library/ | communities:library | apps.communities.history_views.library |
| /communities/<uuid:pk>/contributions/ | communities:contributions | apps.communities.history_views.contributions |
| /communities/<uuid:pk>/summary/ | communities:summary | apps.communities.summary_views.summary |
| /communities/<uuid:pk>/todo/ | communities:sprints | apps.communities.summary_views.sprints |
| /communities/<uuid:pk>/edit/<str:kind>/ | communities:edit | apps.communities.summary_views.edit |
| /communities/<uuid:pk>/sections/<int:record_pk>/edit/ | communities:edit-section | apps.communities.summary_views.edit |
| /communities/<uuid:pk>/sprints/<uuid:record_pk>/edit/ | communities:edit-sprint | apps.communities.summary_views.edit |
| /communities/<uuid:pk>/resources/add/ | communities:resource | apps.communities.summary_views.resource |
| /communities/<uuid:pk>/resources/<uuid:resource_pk>/download/ | communities:resource-download | apps.communities.summary_views.download |
| /communities/projects/<uuid:pk>/create/ | communities:create | apps.communities.views.create |
| /communities/<uuid:pk>/ | communities:detail | apps.communities.views.detail |
| /communities/<uuid:pk>/leader/ | communities:leader | apps.communities.views.leader |
| /communities/<uuid:pk>/<str:section>/ | communities:section | apps.communities.views.section |
| /agreements/projects/<uuid:pk>/ | agreements:project | apps.agreements.views.project |
| /agreements/projects/<uuid:pk>/sign/ | agreements:sign | apps.agreements.views.sign |
| /agreements/projects/<uuid:pk>/blank/ | agreements:blank | apps.agreements.views.blank |
| /agreements/projects/<uuid:pk>/enroll-proposer/ | agreements:enroll | apps.agreements.views.enroll |
| /agreements/<uuid:pk>/ | agreements:evidence | apps.agreements.views.evidence |
| /agreements/<uuid:pk>/download/ | agreements:download | apps.agreements.views.download |
| /agreements/<uuid:pk>/verify/ | agreements:verify | apps.agreements.views.verify |
| /applications/<uuid:pk>/offer/issue/ | recruitment:issue-letter | apps.recruitment.letter_views.issue |
| /applications/letters/<uuid:pk>/ | recruitment:letter | apps.recruitment.letter_views.detail |
| /applications/letters/<uuid:pk>/download/ | recruitment:letter-download | apps.recruitment.letter_views.download |
| /applications/<uuid:pk>/decision/ | recruitment:decision | apps.recruitment.review_views.decision |
| /applications/<uuid:pk>/meeting/ | recruitment:meeting | apps.recruitment.review_views.meeting |
| /applications/meetings/<uuid:pk>/cancel/ | recruitment:cancel-meeting | apps.recruitment.review_views.cancel |
| /applications/ | recruitment:index | apps.recruitment.views.index |
| /applications/projects/<uuid:project_pk>/ | recruitment:project | apps.recruitment.views.index |
| /applications/projects/<uuid:project_pk>/apply/ | recruitment:apply | apps.recruitment.views.apply |
| /applications/<uuid:pk>/ | recruitment:detail | apps.recruitment.views.detail |
| /applications/<uuid:pk>/resume/ | recruitment:resume | apps.recruitment.views.resume |
| /projects/ | projects:index | apps.projects.views.index |
| /projects/discover/ | projects:discover | apps.projects.views.discover |
| /projects/create/ | projects:create | apps.projects.views.edit |
| /projects/<uuid:pk>/ | projects:detail | apps.projects.views.detail |
| /projects/<uuid:pk>/edit/ | projects:edit | apps.projects.views.edit |
| /projects/<uuid:pk>/private/ | projects:private | apps.projects.views.private |
| /documents/<uuid:project_pk>/upload/ | documents:upload | apps.documents.views.upload |
| /documents/<uuid:project_pk>/<uuid:document_pk>/versions/new/ | documents:version | apps.documents.views.upload |
| /documents/<uuid:project_pk>/versions/<uuid:pk>/ | documents:download | apps.documents.views.download |
| /notifications/ | notifications:index | apps.notifications.views.index |
| /notifications/poll/ | notifications:poll | apps.notifications.views.poll |
| /notifications/read-all/ | notifications:read-all | apps.notifications.views.read_all |
| /notifications/<int:pk>/read/ | notifications:read | apps.notifications.views.read |
| /dev/ui/ | ui-preview | apps.core.views.ui_preview |
| /dev/ui/<str:section>/ | ui-preview-section | apps.core.views.ui_preview |

The Django admin route is /admin/ and requires appropriate administrative authentication. Static asset URLs are handled separately in development.

## Appendix C — Complete project-owned file index

Each entry identifies responsibility and, for Python source, its actual top-level classes/functions. Package markers and migrations are included so filenames are not mistaken for missing functionality. Test files verify behaviour; they do not serve pages.

### .env.example

| File | Responsibility / main symbols |
|---|---|
| .env.example | Environment-variable reference; not automatically loaded. |

### .gitignore

| File | Responsibility / main symbols |
|---|---|
| .gitignore | Excludes private data, secrets, generated files and local dependencies from Git. |

### README.md

| File | Responsibility / main symbols |
|---|---|
| README.md | Project overview, setup and historical module summaries. |

### apps

| File | Responsibility / main symbols |
|---|---|
| apps/__init__.py | Python package marker; no runtime feature logic. |

### apps/accounts

| File | Responsibility / main symbols |
|---|---|
| apps/accounts/__init__.py | Python package marker; no runtime feature logic. |
| apps/accounts/admin.py | Registers selected models for Django administrative maintenance. Main symbols: UserAdmin. |
| apps/accounts/apps.py | Registers this Django app and its configuration. Main symbols: AccountsConfig. |
| apps/accounts/forms.py | Validates submitted form data and supplies input widgets for roster authentication and password reset. Main symbols: EmailForm, CodeForm, LoginForm. |
| apps/accounts/management/__init__.py | Python package marker; no runtime feature logic. |
| apps/accounts/management/commands/__init__.py | Python package marker; no runtime feature logic. |
| apps/accounts/management/commands/import_roster.py | Imports roster JSON into hashed-password user/profile records; preserves existing passwords. Main symbols: Command. |
| apps/accounts/middleware.py | Isolates demo account sessions through per-request URL/cookie namespaces. Main symbols: DemoSessionMiddleware. |
| apps/accounts/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/accounts/migrations/0002_auththrottle_otpchallenge.py | Database migration: 0002 auththrottle otpchallenge. Applied by manage.py migrate; records schema/data evolution. |
| apps/accounts/migrations/0003_user_roster_role.py | Database migration: 0003 user roster role. Applied by manage.py migrate; records schema/data evolution. |
| apps/accounts/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/accounts/models.py | Defines relational records, fields, relationships and constraints for roster authentication and password reset. Main symbols: UserManager, User, OTPChallenge, AuthThrottle. |
| apps/accounts/services.py | Implements business operations and persistence rules for roster authentication and password reset. Main symbols: AuthenticationError, digest, demo_mode, registered_user, rate_limit, password_login, request_code, verify_code. |
| apps/accounts/test_authentication.py | Regression tests for roster authentication and password reset; isolates test data from the live demo. Main symbols: AuthenticationWorkflowTests. |
| apps/accounts/test_demo_sessions.py | Regression tests for roster authentication and password reset; isolates test data from the live demo. Main symbols: DemoSessionTests. |
| apps/accounts/tests.py | Regression tests for roster authentication and password reset; isolates test data from the live demo. Main symbols: AccountFoundationTests. |
| apps/accounts/urls.py | Maps feature URL patterns to request handlers for roster authentication and password reset. |
| apps/accounts/validators.py | Validates and normalizes the accepted university email domains. Main symbols: normalise_college_email, validate_college_email. |
| apps/accounts/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for roster authentication and password reset. Main symbols: sign_in, forgot, current_challenge, verify, resend, reset_user, reset_password, sign_out, new_demo_session. |

### apps/agreements

| File | Responsibility / main symbols |
|---|---|
| apps/agreements/__init__.py | Python package marker; no runtime feature logic. |
| apps/agreements/apps.py | Registers this Django app and its configuration. Main symbols: AgreementsConfig. |
| apps/agreements/forms.py | Validates submitted form data and supplies input widgets for agreement signing evidence and verification. Main symbols: SigningForm. |
| apps/agreements/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/agreements/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/agreements/models.py | Defines relational records, fields, relationships and constraints for agreement signing evidence and verification. Main symbols: ImmutableRecord, Agreement, evidence_path, AgreementEvidence, AgreementReview. |
| apps/agreements/pdf.py | Renders confidentiality agreement text and signing evidence into PDF. Main symbols: Signature, agreement_pdf. |
| apps/agreements/permissions.py | Centralizes eligibility and access decisions for agreement signing evidence and verification. Main symbols: selected_application, eligible_student, can_view_agreement, roster, agreement_gate. |
| apps/agreements/services.py | Implements business operations and persistence rules for agreement signing evidence and verification. Main symbols: context, decode, preview, physical_pdf, submit, review, enroll_proposer. |
| apps/agreements/templates.py | Defines versioned agreement wording and consent text; not an HTML page. Main symbols: current_template, digest. |
| apps/agreements/tests.py | Regression tests for agreement signing evidence and verification; isolates test data from the live demo. Main symbols: AgreementTests. |
| apps/agreements/urls.py | Maps feature URL patterns to request handlers for agreement signing evidence and verification. |
| apps/agreements/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for agreement signing evidence and verification. Main symbols: project, sign, blank, evidence, download, verify, enroll. |

### apps/collaboration

| File | Responsibility / main symbols |
|---|---|
| apps/collaboration/__init__.py | Python package marker; no runtime feature logic. |
| apps/collaboration/apps.py | Registers this Django app and its configuration. Main symbols: CollaborationConfig. |
| apps/collaboration/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/collaboration/migrations/0002_chatreadstate.py | Database migration: 0002 chatreadstate. Applied by manage.py migrate; records schema/data evolution. |
| apps/collaboration/migrations/0003_poll_revision.py | Database migration: 0003 poll revision. Applied by manage.py migrate; records schema/data evolution. |
| apps/collaboration/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/collaboration/models.py | Defines relational records, fields, relationships and constraints for chat, media, polls and announcements. Main symbols: ChatMessage, attachment_path, ChatAttachment, Poll, PollOption, PollVote, Announcement, AnnouncementRevision, ChatReadState. |
| apps/collaboration/services.py | Implements business operations and persistence rules for chat, media, polls and announcements. Main symbols: lock, send, vote, close_poll, announce. |
| apps/collaboration/tests.py | Regression tests for chat, media, polls and announcements; isolates test data from the live demo. Main symbols: ChatTests. |
| apps/collaboration/uploads.py | Checks chat/task attachment type, content structure and size. Main symbols: inspect_upload. |
| apps/collaboration/urls.py | Maps feature URL patterns to request handlers for chat, media, polls and announcements. |
| apps/collaboration/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for chat, media, polls and announcements. Main symbols: AnnouncementForm, number, query, poll_context, message_html, chat, feed, post, poll_action, media, attachment, announcements, announcement_edit, unread_context, unread, mark_read. |

### apps/communities

| File | Responsibility / main symbols |
|---|---|
| apps/communities/__init__.py | Python package marker; no runtime feature logic. |
| apps/communities/apps.py | Registers this Django app and its configuration. Main symbols: CommunitiesConfig. |
| apps/communities/history_views.py | Builds activity timeline, version library and recorded contribution views. Main symbols: Filters, file_rows, activity, history, library, contributions. |
| apps/communities/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/communities/migrations/0002_projectsummary_summarysection_sprint_summaryresource.py | Database migration: 0002 projectsummary summarysection sprint summaryresource. Applied by manage.py migrate; records schema/data evolution. |
| apps/communities/migrations/0003_communityevent_actor_name_summaryresource_replaces_and_more.py | Database migration: 0003 communityevent actor name summaryresource replaces and more. Applied by manage.py migrate; records schema/data evolution. |
| apps/communities/migrations/0004_backfill_contributor_names.py | Database migration: 0004 backfill contributor names. Applied by manage.py migrate; records schema/data evolution. |
| apps/communities/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/communities/models.py | Defines relational records, fields, relationships and constraints for private communities, summaries, sprints and history. Main symbols: Community, Membership, CommunityEvent, ProjectSummary, SummarySection, Sprint, resource_path, SummaryResource. |
| apps/communities/permissions.py | Centralizes eligibility and access decisions for private communities, summaries, sprints and history. Main symbols: can_enter, can_edit. |
| apps/communities/services.py | Implements business operations and persistence rules for private communities, summaries, sprints and history. Main symbols: checklist, confirmation, create_or_sync, appoint_leader. |
| apps/communities/summary_forms.py | Defines summary, resource and sprint input validation. Main symbols: EditFields, SummaryForm, SectionForm, SprintForm, ResourceForm. |
| apps/communities/summary_services.py | Saves summary sections, resources and sprint operations with history. Main symbols: lock, replay, snapshot, record_edit, save_text, validate_resource, save_resource. |
| apps/communities/summary_views.py | Serves summary, sprint editing and protected resource download pages. Main symbols: workspace_context, summary, sprints, edit, resource, download. |
| apps/communities/test_history.py | Regression tests for private communities, summaries, sprints and history; isolates test data from the live demo. Main symbols: HistoryTests. |
| apps/communities/test_summary.py | Regression tests for private communities, summaries, sprints and history; isolates test data from the live demo. Main symbols: SummarySprintTests. |
| apps/communities/tests.py | Regression tests for private communities, summaries, sprints and history; isolates test data from the live demo. Main symbols: CommunityTests. |
| apps/communities/urls.py | Maps feature URL patterns to request handlers for private communities, summaries, sprints and history. |
| apps/communities/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for private communities, summaries, sprints and history. Main symbols: create, accessible, detail, section, leader. |

### apps/core

| File | Responsibility / main symbols |
|---|---|
| apps/core/__init__.py | Python package marker; no runtime feature logic. |
| apps/core/apps.py | Registers this Django app and its configuration. Main symbols: CoreConfig. |
| apps/core/backup.py | Copies/verifies SQLite and uploads with checksum manifests and restores safely. Main symbols: digest, verify, backup, restore. |
| apps/core/management/__init__.py | Python package marker; no runtime feature logic. |
| apps/core/management/commands/__init__.py | Python package marker; no runtime feature logic. |
| apps/core/management/commands/backup_workspace.py | CLI for a stopped workspace backup with checksums. Main symbols: Command. |
| apps/core/management/commands/restore_workspace.py | CLI for verifying/restoring a backup into a new directory. Main symbols: Command. |
| apps/core/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/core/permissions.py | Centralizes eligibility and access decisions for shared dashboard, access and operations. Main symbols: college_member, approved_teacher, can_create_idea, can_manage_project, can_view_confidential, can_view_project, can_view_resume, require_permission. |
| apps/core/test_release.py | Regression tests for shared dashboard, access and operations; isolates test data from the live demo. Main symbols: BackupTests. |
| apps/core/tests.py | Regression tests for shared dashboard, access and operations; isolates test data from the live demo. Main symbols: FoundationRoutingTests, PreviewBoundaryTests. |
| apps/core/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for shared dashboard, access and operations. Main symbols: ui_preview, dashboard, health. |

### apps/documents

| File | Responsibility / main symbols |
|---|---|
| apps/documents/__init__.py | Python package marker; no runtime feature logic. |
| apps/documents/apps.py | Registers this Django app and its configuration. Main symbols: DocumentsConfig. |
| apps/documents/forms.py | Validates submitted form data and supplies input widgets for private project documents and versions. Main symbols: DocumentForm. |
| apps/documents/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/documents/migrations/0002_initial.py | Database migration: 0002 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/documents/migrations/0003_documentversion_uploader_name.py | Database migration: 0003 documentversion uploader name. Applied by manage.py migrate; records schema/data evolution. |
| apps/documents/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/documents/models.py | Defines relational records, fields, relationships and constraints for private project documents and versions. Main symbols: document_path, ProjectDocument, DocumentVersion. |
| apps/documents/security.py | Builds permission-protected private file download responses. Main symbols: validate_private_pdf, private_download. |
| apps/documents/services.py | Implements business operations and persistence rules for private project documents and versions. Main symbols: upload_document. |
| apps/documents/urls.py | Maps feature URL patterns to request handlers for private project documents and versions. |
| apps/documents/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for private project documents and versions. Main symbols: upload, download. |

### apps/ip_progress

| File | Responsibility / main symbols |
|---|---|
| apps/ip_progress/__init__.py | Python package marker; no runtime feature logic. |
| apps/ip_progress/apps.py | Registers this Django app and its configuration. Main symbols: IpProgressConfig. |
| apps/ip_progress/forms.py | Validates submitted form data and supplies input widgets for completion, private IP updates and achievements. Main symbols: Confirmation, CompletionForm, IPForm, AchievementForm. |
| apps/ip_progress/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/ip_progress/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/ip_progress/models.py | Defines relational records, fields, relationships and constraints for completion, private IP updates and achievements. Main symbols: Completion, IPUpdate, Achievement. |
| apps/ip_progress/services.py | Implements business operations and persistence rules for completion, private IP updates and achievements. Main symbols: perform. |
| apps/ip_progress/tests.py | Regression tests for completion, private IP updates and achievements; isolates test data from the live demo. Main symbols: OutcomeTests. |
| apps/ip_progress/urls.py | Maps feature URL patterns to request handlers for completion, private IP updates and achievements. |
| apps/ip_progress/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for completion, private IP updates and achievements. Main symbols: approved_achievements, overview, action, download. |

### apps/mentorship

| File | Responsibility / main symbols |
|---|---|
| apps/mentorship/__init__.py | Python package marker; no runtime feature logic. |
| apps/mentorship/apps.py | Registers this Django app and its configuration. Main symbols: MentorshipConfig. |
| apps/mentorship/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/mentorship/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/mentorship/models.py | Defines relational records, fields, relationships and constraints for mentor ranking and sequential requests. Main symbols: MentorSearch, MentorRequest. |
| apps/mentorship/services.py | Implements business operations and persistence rules for mentor ranking and sequential requests. Main symbols: rank_mentors, _lock_project, _advance, start_search, decide. |
| apps/mentorship/tests.py | Regression tests for mentor ranking and sequential requests; isolates test data from the live demo. Main symbols: MentorshipTests. |
| apps/mentorship/urls.py | Maps feature URL patterns to request handlers for mentor ranking and sequential requests. |
| apps/mentorship/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for mentor ranking and sequential requests. Main symbols: ChoiceForm, DecisionForm, suggestions, inbox, review. |

### apps/notifications

| File | Responsibility / main symbols |
|---|---|
| apps/notifications/__init__.py | Python package marker; no runtime feature logic. |
| apps/notifications/apps.py | Registers this Django app and its configuration. Main symbols: NotificationsConfig. |
| apps/notifications/context_processors.py | Adds notification counts to shared template context. Main symbols: notification_count. |
| apps/notifications/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/notifications/migrations/0002_initial.py | Database migration: 0002 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/notifications/migrations/0003_notification_application.py | Database migration: 0003 notification application. Applied by manage.py migrate; records schema/data evolution. |
| apps/notifications/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/notifications/models.py | Defines relational records, fields, relationships and constraints for persistent alerts and authorised links. Main symbols: Notification. |
| apps/notifications/services.py | Implements business operations and persistence rules for persistent alerts and authorised links. Main symbols: notify, authorised_url, notify_departments. |
| apps/notifications/urls.py | Maps feature URL patterns to request handlers for persistent alerts and authorised links. |
| apps/notifications/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for persistent alerts and authorised links. Main symbols: index, poll, read, read_all. |

### apps/profiles

| File | Responsibility / main symbols |
|---|---|
| apps/profiles/__init__.py | Python package marker; no runtime feature logic. |
| apps/profiles/admin.py | Registers selected models for Django administrative maintenance. Main symbols: ProfileAdmin. |
| apps/profiles/apps.py | Registers this Django app and its configuration. Main symbols: ProfilesConfig. |
| apps/profiles/forms.py | Validates submitted form data and supplies input widgets for profiles, controlled taxonomy and resume versions. Main symbols: ProfileForm. |
| apps/profiles/management/__init__.py | Python package marker; no runtime feature logic. |
| apps/profiles/management/commands/__init__.py | Python package marker; no runtime feature logic. |
| apps/profiles/management/commands/seed_demo_taxonomy.py | Recreates controlled demo departments, skills and interests. Main symbols: Command. |
| apps/profiles/middleware.py | Redirects authenticated users to required profile completion. Main symbols: ProfileGateMiddleware. |
| apps/profiles/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/profiles/migrations/0002_department_options.py | Database migration: 0002 department options. Applied by manage.py migrate; records schema/data evolution. |
| apps/profiles/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/profiles/models.py | Defines relational records, fields, relationships and constraints for profiles, controlled taxonomy and resume versions. Main symbols: Department, Skill, ResearchInterest, Profile, resume_path, ResumeVersion. |
| apps/profiles/taxonomy.py | Defines the controlled department names. |
| apps/profiles/tests.py | Regression tests for profiles, controlled taxonomy and resume versions; isolates test data from the live demo. Main symbols: ProfileWorkflowTests. |
| apps/profiles/urls.py | Maps feature URL patterns to request handlers for profiles, controlled taxonomy and resume versions. |
| apps/profiles/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for profiles, controlled taxonomy and resume versions. Main symbols: edit, resume_download. |

### apps/projects

| File | Responsibility / main symbols |
|---|---|
| apps/projects/__init__.py | Python package marker; no runtime feature logic. |
| apps/projects/apps.py | Registers this Django app and its configuration. Main symbols: ProjectsConfig. |
| apps/projects/discovery.py | Builds recruitment search, filtering and sorting queries. Main symbols: DiscoveryForm, discovery_context. |
| apps/projects/forms.py | Validates submitted form data and supplies input widgets for ideas, recruitment notices and confidential details. Main symbols: IdeaForm. |
| apps/projects/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/projects/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/projects/models.py | Defines relational records, fields, relationships and constraints for ideas, recruitment notices and confidential details. Main symbols: Project, ConfidentialIdea. |
| apps/projects/services.py | Implements business operations and persistence rules for ideas, recruitment notices and confidential details. Main symbols: save_idea. |
| apps/projects/test_discovery.py | Regression tests for ideas, recruitment notices and confidential details; isolates test data from the live demo. Main symbols: DiscoveryTests. |
| apps/projects/tests.py | Regression tests for ideas, recruitment notices and confidential details; isolates test data from the live demo. Main symbols: ResearchModulesTests. |
| apps/projects/urls.py | Maps feature URL patterns to request handlers for ideas, recruitment notices and confidential details. |
| apps/projects/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for ideas, recruitment notices and confidential details. Main symbols: index, edit, detail, private, discover. |

### apps/recruitment

| File | Responsibility / main symbols |
|---|---|
| apps/recruitment/__init__.py | Python package marker; no runtime feature logic. |
| apps/recruitment/apps.py | Registers this Django app and its configuration. Main symbols: RecruitmentConfig. |
| apps/recruitment/forms.py | Validates submitted form data and supplies input widgets for applications, review, meetings and offer letters. Main symbols: ApplicationForm. |
| apps/recruitment/letter_pdf.py | Generates styled offer-letter PDFs from preserved letter snapshots. Main symbols: render_letter. |
| apps/recruitment/letter_services.py | Prepares signed letter previews and issues immutable offer records/PDFs. Main symbols: preview_letter, issue_letter. |
| apps/recruitment/letter_views.py | Serves mentor issuance flow and authorised letter viewing/downloads. Main symbols: LetterForm, issue, detail, download. |
| apps/recruitment/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/recruitment/migrations/0002_alter_application_status_meetinginvitation_and_more.py | Database migration: 0002 alter application status meetinginvitation and more. Applied by manage.py migrate; records schema/data evolution. |
| apps/recruitment/migrations/0003_offerletter.py | Database migration: 0003 offerletter. Applied by manage.py migrate; records schema/data evolution. |
| apps/recruitment/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/recruitment/models.py | Defines relational records, fields, relationships and constraints for applications, review, meetings and offer letters. Main symbols: letter_path, OfferLetter, application_path, Application, ReviewDecision, MeetingInvitation. |
| apps/recruitment/permissions.py | Centralizes eligibility and access decisions for applications, review, meetings and offer letters. Main symbols: can_apply, can_view_application, can_review_applications, can_view_applicant_overview. |
| apps/recruitment/review_forms.py | Defines applicant-management filters and review/meeting inputs. Main symbols: ReviewForm, MeetingForm, ApplicantFilterForm. |
| apps/recruitment/review_services.py | Applies applicant decisions and meeting changes with validation/history. Main symbols: lock_application, review_application, invite_to_meeting, cancel_meeting. |
| apps/recruitment/review_views.py | Handles mentor applicant decisions and meeting request pages. Main symbols: decision, meeting, cancel. |
| apps/recruitment/services.py | Implements business operations and persistence rules for applications, review, meetings and offer letters. Main symbols: _clean_old_file, prepare_application, submit_application. |
| apps/recruitment/test_letters.py | Regression tests for applications, review, meetings and offer letters; isolates test data from the live demo. Main symbols: OfferLetterTests. |
| apps/recruitment/test_review.py | Regression tests for applications, review, meetings and offer letters; isolates test data from the live demo. Main symbols: ApplicantReviewTests. |
| apps/recruitment/tests.py | Regression tests for applications, review, meetings and offer letters; isolates test data from the live demo. Main symbols: ApplicationTests. |
| apps/recruitment/urls.py | Maps feature URL patterns to request handlers for applications, review, meetings and offer letters. |
| apps/recruitment/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for applications, review, meetings and offer letters. Main symbols: apply, detail, resume, index. |

### apps/tasks

| File | Responsibility / main symbols |
|---|---|
| apps/tasks/__init__.py | Python package marker; no runtime feature logic. |
| apps/tasks/apps.py | Registers this Django app and its configuration. Main symbols: TasksConfig. |
| apps/tasks/forms.py | Validates submitted form data and supplies input widgets for assigned work, evidence and review. Main symbols: Confirmation, PersonChoice, TaskForm, MultipleInput, MultipleFiles, FileChoice, EvidenceChoice, WorkForm, ReviewForm, ReopenForm, CommentForm. |
| apps/tasks/migrations/0001_initial.py | Database migration: 0001 initial. Applied by manage.py migrate; records schema/data evolution. |
| apps/tasks/migrations/0002_taskfile_replaces_taskfile_revision_note_and_more.py | Database migration: 0002 taskfile replaces taskfile revision note and more. Applied by manage.py migrate; records schema/data evolution. |
| apps/tasks/migrations/__init__.py | Python package marker; no runtime feature logic. |
| apps/tasks/models.py | Defines relational records, fields, relationships and constraints for assigned work, evidence and review. Main symbols: Immutable, Task, TaskFile, Submission, Review, TaskComment. |
| apps/tasks/services.py | Implements business operations and persistence rules for assigned work, evidence and review. Main symbols: check_revision, event, replay, alert, save_task, act. |
| apps/tasks/tests.py | Regression tests for assigned work, evidence and review; isolates test data from the live demo. Main symbols: TaskTests. |
| apps/tasks/urls.py | Maps feature URL patterns to request handlers for assigned work, evidence and review. |
| apps/tasks/views.py | Handles HTTP requests, permission checks and HTML/JSON/file responses for assigned work, evidence and review. Main symbols: totals, board, edit, detail, action, download. |

### config

| File | Responsibility / main symbols |
|---|---|
| config/__init__.py | Python package marker; no runtime feature logic. |
| config/asgi.py | ASGI application entry point; not evidence of WebSocket chat. |

### config/settings

| File | Responsibility / main symbols |
|---|---|
| config/settings/__init__.py | Python package marker; no runtime feature logic. |
| config/settings/base.py | Shared settings: app/middleware registration, SQLite, auth, templates, files, email and timezone. |
| config/settings/local.py | Local debug mode, isolated demo paths and persistent development secret. |
| config/settings/production.py | Production configuration and required-secret/host/data-directory validation. |

### config

| File | Responsibility / main symbols |
|---|---|
| config/urls.py | Top-level route inclusion and route precedence. |
| config/wsgi.py | WSGI application entry point for compatible servers. |

### demo_rosters

| File | Responsibility / main symbols |
|---|---|
| demo_rosters/README.md | Fictional account roster/import reference. JSON passwords are initial demo seed data, not live password storage. |
| demo_rosters/faculty.json | Fictional teacher roster/import reference. JSON passwords are initial demo seed data, not live password storage. |
| demo_rosters/students.json | Fictional student roster/import reference. JSON passwords are initial demo seed data, not live password storage. |

### docs

| File | Responsibility / main symbols |
|---|---|
| docs/architecture.md | Documentation: Architecture and implementation mapping. Historical module notes may describe the earlier milestone. |
| docs/authentication-and-profiles.md | Documentation: Current authentication: university roster login and password reset. Historical module notes may describe the earlier milestone. |
| docs/decisions.md | Documentation: Confirmed scope, assumptions, and pending decisions. Historical module notes may describe the earlier milestone. |
| docs/interface.md | Documentation: Shared interface — Module 2. Historical module notes may describe the earlier milestone. |
| docs/module-10.md | Documentation: Module 10 — applications and résumé snapshots. Historical module notes may describe the earlier milestone. |
| docs/module-11.md | Documentation: Module 11 — applicant review, shortlist and optional meetings. Historical module notes may describe the earlier milestone. |
| docs/module-12.md | Documentation: Module 12 - Offer letters. Historical module notes may describe the earlier milestone. |
| docs/module-13.md | Documentation: Module 13 - Confidentiality agreements. Historical module notes may describe the earlier milestone. |
| docs/module-14.md | Documentation: Module 14 - Private communities and team leaders. Historical module notes may describe the earlier milestone. |
| docs/module-15.md | Documentation: Module 15 - Editable summary and sprints. Historical module notes may describe the earlier milestone. |
| docs/module-16.md | Documentation: Module 16: team chat and announcements. Historical module notes may describe the earlier milestone. |
| docs/module-17.md | Documentation: Module 17: tasks, evidence and approved completion. Historical module notes may describe the earlier milestone. |
| docs/module-18.md | Documentation: Module 18: history, document versions and contributions. Historical module notes may describe the earlier milestone. |
| docs/module-19.md | Documentation: Module 19: completion and research outcomes. Historical module notes may describe the earlier milestone. |
| docs/module-20.md | Documentation: Module 20: local release and verification. Historical module notes may describe the earlier milestone. |
| docs/module-8.md | Documentation: Module 8 — mentor matching and sequential requests. Historical module notes may describe the earlier milestone. |
| docs/module-9.md | Documentation: Module 9 — project discovery. Historical module notes may describe the earlier milestone. |
| docs/modules-5-7.md | Documentation: Modules 5–7: private access, notifications and ideas. Historical module notes may describe the earlier milestone. |
| docs/operations.md | Documentation: Operations and persistence. Historical module notes may describe the earlier milestone. |
| docs/permissions-and-states.md | Documentation: Intended permissions and state transitions. Historical module notes may describe the earlier milestone. |
| docs/requirements-original.md | Documentation: requirements original. Historical module notes may describe the earlier milestone. |
| docs/status.md | Documentation: Current release status (13 September 2026). Historical module notes may describe the earlier milestone. |

### manage.py

| File | Responsibility / main symbols |
|---|---|
| manage.py | Django CLI entry point for migrations, tests, shell and local server. |

### requirements.txt

| File | Responsibility / main symbols |
|---|---|
| requirements.txt | Pinned runtime dependency versions. |

### reset-demo.cmd

| File | Responsibility / main symbols |
|---|---|
| reset-demo.cmd | Launches the reusable stopped-demo archive/recreation script. |

### scripts

| File | Responsibility / main symbols |
|---|---|
| scripts/reset_demo.py | Validates paths, archives demo data and recreates schema/taxonomy/ten accounts. Main symbols: reset. |

### setup-demo.cmd

| File | Responsibility / main symbols |
|---|---|
| setup-demo.cmd | Creates the environment, installs dependencies and migrates. |

### start-demo.cmd

| File | Responsibility / main symbols |
|---|---|
| start-demo.cmd | Applies migrations and starts the existing local demo without resetting data. |

### static/css

| File | Responsibility / main symbols |
|---|---|
| static/css/base.css | Foundational styles, variables and shared elements. |
| static/css/projects.css | Feature-specific project/community/chat/task/outcome styling. |
| static/css/refinement.css | Shared layout and visual refinements layered over base styles. |
| static/css/studio.css | Additional polished interface and responsive styling. |

### static/js

| File | Responsibility / main symbols |
|---|---|
| static/js/accounts.js | Login inputs and password-reset OTP browser interactions. |
| static/js/agreements.js | Captures and manages electronic drawing/signature input. |
| static/js/chat-unread.js | Refreshes dashboard unread-chat summary. |
| static/js/chat.js | Chat feed polling, sending/replies, attachments/voice notes and poll controls. |
| static/js/notifications.js | Polls and updates the shared notification bell. |
| static/js/ui.js | Shared navigation/menu and general interface interactions. |

### templates/accounts

| File | Responsibility / main symbols |
|---|---|
| templates/accounts/forgot.html | HTML template/fragment for forgot in roster authentication and password reset. Inherits accounts/login.html. |
| templates/accounts/login.html | HTML template/fragment for login in roster authentication and password reset. Inherits base.html. |
| templates/accounts/reset.html | HTML template/fragment for reset in roster authentication and password reset. Inherits accounts/login.html. |
| templates/accounts/verify.html | HTML template/fragment for verify in roster authentication and password reset. Inherits accounts/login.html. |

### templates/agreements

| File | Responsibility / main symbols |
|---|---|
| templates/agreements/content.html | HTML template/fragment for content in agreement signing evidence and verification. |
| templates/agreements/evidence.html | HTML template/fragment for evidence in agreement signing evidence and verification. Inherits layouts/member.html. |
| templates/agreements/pending.html | Explains that signing waits for mentor offer-letter issuance. |
| templates/agreements/project.html | HTML template/fragment for project in agreement signing evidence and verification. Inherits layouts/member.html. |
| templates/agreements/sign.html | HTML template/fragment for sign in agreement signing evidence and verification. Inherits layouts/member.html. |

### templates

| File | Responsibility / main symbols |
|---|---|
| templates/base.html | Root HTML document, shared CSS/JS loading and content blocks. |

### templates/collaboration

| File | Responsibility / main symbols |
|---|---|
| templates/collaboration/announcement_form.html | HTML template/fragment for announcement form in chat, media, polls and announcements. Inherits layouts/member.html. |
| templates/collaboration/announcements.html | HTML template/fragment for announcements in chat, media, polls and announcements. Inherits layouts/member.html. |
| templates/collaboration/attachment.html | HTML template/fragment for attachment in chat, media, polls and announcements. |
| templates/collaboration/chat.html | HTML template/fragment for chat in chat, media, polls and announcements. Inherits layouts/member.html. |
| templates/collaboration/media.html | HTML template/fragment for media in chat, media, polls and announcements. Inherits layouts/member.html. |
| templates/collaboration/message.html | HTML template/fragment for message in chat, media, polls and announcements. |
| templates/collaboration/poll.html | HTML template/fragment for poll in chat, media, polls and announcements. |
| templates/collaboration/unread.html | HTML template/fragment for unread in chat, media, polls and announcements. |

### templates/communities

| File | Responsibility / main symbols |
|---|---|
| templates/communities/contributions.html | HTML template/fragment for contributions in private communities, summaries, sprints and history. Inherits layouts/member.html. |
| templates/communities/create.html | HTML template/fragment for create in private communities, summaries, sprints and history. Inherits layouts/member.html. |
| templates/communities/detail.html | HTML template/fragment for detail in private communities, summaries, sprints and history. Inherits layouts/member.html. |
| templates/communities/edit.html | HTML template/fragment for edit in private communities, summaries, sprints and history. Inherits layouts/member.html. |
| templates/communities/history.html | HTML template/fragment for history in private communities, summaries, sprints and history. Inherits layouts/member.html. |
| templates/communities/history_nav.html | HTML template/fragment for history nav in private communities, summaries, sprints and history. |
| templates/communities/library.html | HTML template/fragment for library in private communities, summaries, sprints and history. Inherits layouts/member.html. |
| templates/communities/section.html | Legacy generic section template; the five community cards now use implemented named routes. |
| templates/communities/sprint_card.html | HTML template/fragment for sprint card in private communities, summaries, sprints and history. |
| templates/communities/sprints.html | HTML template/fragment for sprints in private communities, summaries, sprints and history. Inherits layouts/member.html. |
| templates/communities/summary.html | HTML template/fragment for summary in private communities, summaries, sprints and history. Inherits layouts/member.html. |

### templates/components

| File | Responsibility / main symbols |
|---|---|
| templates/components/brand.html | HTML template/fragment for brand in the application. |
| templates/components/empty.html | HTML template/fragment for empty in the application. |
| templates/components/field.html | HTML template/fragment for field in the application. |
| templates/components/icon.html | HTML template/fragment for icon in the application. |
| templates/components/messages.html | HTML template/fragment for messages in the application. |
| templates/components/pagination.html | HTML template/fragment for pagination in the application. |

### templates/core

| File | Responsibility / main symbols |
|---|---|
| templates/core/dashboard.html | HTML template/fragment for dashboard in shared dashboard, access and operations. Inherits layouts/member.html. |
| templates/core/preview.html | HTML template/fragment for preview in shared dashboard, access and operations. Inherits layouts/workspace.html. |

### templates/documents

| File | Responsibility / main symbols |
|---|---|
| templates/documents/upload.html | HTML template/fragment for upload in private project documents and versions. Inherits layouts/member.html. |

### templates/ip_progress

| File | Responsibility / main symbols |
|---|---|
| templates/ip_progress/achievements.html | HTML template/fragment for achievements in completion, private IP updates and achievements. |
| templates/ip_progress/form.html | HTML template/fragment for form in completion, private IP updates and achievements. Inherits layouts/member.html. |
| templates/ip_progress/overview.html | HTML template/fragment for overview in completion, private IP updates and achievements. Inherits layouts/member.html. |

### templates/layouts

| File | Responsibility / main symbols |
|---|---|
| templates/layouts/member.html | Authenticated sidebar/topbar, notifications, account menu and demo account link. |
| templates/layouts/workspace.html | Alternative shared workspace layout shell. |

### templates/mentorship

| File | Responsibility / main symbols |
|---|---|
| templates/mentorship/inbox.html | HTML template/fragment for inbox in mentor ranking and sequential requests. Inherits layouts/member.html. |
| templates/mentorship/review.html | HTML template/fragment for review in mentor ranking and sequential requests. Inherits layouts/member.html. |
| templates/mentorship/suggestions.html | HTML template/fragment for suggestions in mentor ranking and sequential requests. Inherits layouts/member.html. |

### templates/notifications

| File | Responsibility / main symbols |
|---|---|
| templates/notifications/index.html | HTML template/fragment for index in persistent alerts and authorised links. Inherits layouts/member.html. |

### templates/profiles

| File | Responsibility / main symbols |
|---|---|
| templates/profiles/edit.html | HTML template/fragment for edit in profiles, controlled taxonomy and resume versions. Inherits layouts/member.html. |

### templates/projects

| File | Responsibility / main symbols |
|---|---|
| templates/projects/card.html | HTML template/fragment for card in ideas, recruitment notices and confidential details. |
| templates/projects/detail.html | HTML template/fragment for detail in ideas, recruitment notices and confidential details. Inherits layouts/member.html. |
| templates/projects/discover.html | HTML template/fragment for discover in ideas, recruitment notices and confidential details. Inherits layouts/member.html. |
| templates/projects/discovery_results.html | HTML template/fragment for discovery results in ideas, recruitment notices and confidential details. |
| templates/projects/form.html | HTML template/fragment for form in ideas, recruitment notices and confidential details. Inherits layouts/member.html. |
| templates/projects/index.html | HTML template/fragment for index in ideas, recruitment notices and confidential details. Inherits layouts/member.html. |
| templates/projects/private.html | HTML template/fragment for private in ideas, recruitment notices and confidential details. Inherits layouts/member.html. |

### templates/recruitment

| File | Responsibility / main symbols |
|---|---|
| templates/recruitment/apply.html | HTML template/fragment for apply in applications, review, meetings and offer letters. Inherits layouts/member.html. |
| templates/recruitment/detail.html | HTML template/fragment for detail in applications, review, meetings and offer letters. Inherits layouts/member.html. |
| templates/recruitment/index.html | HTML template/fragment for index in applications, review, meetings and offer letters. Inherits layouts/member.html. |
| templates/recruitment/letter.html | HTML template/fragment for letter in applications, review, meetings and offer letters. Inherits layouts/member.html. |
| templates/recruitment/letter_content.html | HTML template/fragment for letter content in applications, review, meetings and offer letters. |
| templates/recruitment/letter_issue.html | HTML template/fragment for letter issue in applications, review, meetings and offer letters. Inherits layouts/member.html. |
| templates/recruitment/manage.html | HTML template/fragment for manage in applications, review, meetings and offer letters. Inherits layouts/member.html. |
| templates/recruitment/meeting.html | HTML template/fragment for meeting in applications, review, meetings and offer letters. Inherits layouts/member.html. |
| templates/recruitment/next_steps.html | Prominent selected-applicant offer-letter and agreement controls. |
| templates/recruitment/review_panel.html | HTML template/fragment for review panel in applications, review, meetings and offer letters. |

### templates/tasks

| File | Responsibility / main symbols |
|---|---|
| templates/tasks/board.html | HTML template/fragment for board in assigned work, evidence and review. Inherits layouts/member.html. |
| templates/tasks/checklist_row.html | HTML template/fragment for checklist row in assigned work, evidence and review. |
| templates/tasks/detail.html | HTML template/fragment for detail in assigned work, evidence and review. Inherits layouts/member.html. |
| templates/tasks/form.html | HTML template/fragment for form in assigned work, evidence and review. Inherits layouts/member.html. |

### Generated, runtime and private directories

| Directory | Purpose |
|---|---|
| private/demo | Current live demo DB, uploads and development secret |
| private/demo-backup-TIMESTAMP | Previous complete demo archived by reset |
| private/release-backups and other backup destinations | Prior verified backup/restore artifacts, when present |
| private outside demo | Baseline/real-mode storage and other private artifacts; not the fresh demo |
| .venv or ../../work/.venv | Python interpreter and third-party packages |
| __pycache__ | Generated Python bytecode cache, not source-of-truth records |
| staticfiles | collectstatic output for serving public app assets |
| .git | Git source history, not the application database |
| ../../work | Development logs, isolated QA scripts and tools |

This guide and its HTML companion are generated explanations, not runtime application modules.
