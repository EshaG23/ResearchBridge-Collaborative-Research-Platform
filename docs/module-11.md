# Module 11 — applicant review, shortlist and optional meetings

## Using the workflow

After a student submits an application, the accepted mentor opens My Projects, the project, then View applications. Applicant management shows name, department, year, submitted skills, availability, application date and status, with live counts and name/status filters. The mentor can open the preserved application and exact submitted résumé.

Student proposers can open the same project applicant overview, but only see the listed overview fields. They cannot open private application details, phone/email, résumés, meeting details or decision controls. This is the documented least-privilege default for the formerly unresolved proposer résumé access question. Unrelated faculty and administrators do not acquire reviewer permissions.

On an application, the mentor can shortlist or mark not selected. A shortlisted applicant can be returned to review, marked not selected, or finally selected. Not-selected applications can be reopened. Final selection is deliberately distinct from shortlisting; once selected, the review controls do not silently reverse the decision. Selecting above the project's listed position capacity is blocked. Offer letters are Module 12, so selection here does not issue a letter, sign an NDA or create membership.

Applicants see their current status and review history under My applications after logout/login. Every status change stores actor, before/after state and time. No review operation changes the submitted profile snapshot, introduction or résumé.

## Meetings

The mentor can invite a submitted or shortlisted applicant to an optional meeting. Enter a message, future date/time in IST, venue, and optionally an HTTPS online meeting link. Timestamps are timezone-aware; forms interpret input as Asia/Kolkata and displays explicitly say IST. There is no email/video-call/calendar integration.

The intended applicant receives a generic in-app notice linking directly to their private application context. Message, venue, time and meeting URL appear only to that applicant and the current approved project mentor. Student proposers cannot see these details. The mentor can cancel an invitation; the applicant is notified and the original invitation and cancellation remain in history. To change arrangements, cancel the old invitation and create a new one. Past meetings are labelled Past meeting, not automatically completed.

## Server-side guarantees

Only the currently attached approved mentor may review or send/cancel invitations. Drafts remain hidden from applicant management and cannot be reviewed. The proposer overview queries only permitted snapshot fields. All writes require POST and CSRF. Forged application/meeting IDs are rejected. Notification targets are re-authorised when generated/opened and never accept a user-provided redirect URL.

Project-scoped transactional locks serialise decisions and capacity checks. Review revision numbers reject stale decisions. Unique request keys prevent retried decisions/invitations from creating duplicates. Cancelling an already cancelled invitation does not notify twice. Decision/invitation records and their notification commit or roll back together. Revoked mentor approval removes review and private-file access.

## Verification and boundaries

All 95 Django tests passed, including 12 new review/meeting tests. Coverage includes state transitions and retries, invalid/stale actions, final-selection capacity, snapshot preservation, proposer privacy, draft exclusion, unrelated/revoked faculty denial, IST-to-UTC conversion, HTTPS/future-time validation, private notification links, invitation/cancellation persistence, transaction rollback, filters, CSRF and login/logout persistence. Existing module 10 tests now verify draft exclusion by result count and application ID rather than a word that may also occur in interface text.

Migrations applied; no pending model changes. Isolated test-database sample pages were rendered for browser inspection of applicant management, review controls and the meeting form. Desktop/table and phone layout checked without changing the freshly reset live demo data. The temporary QA server was stopped afterward.

Letter generation and immutable selection letters are the next module. No offer accept/decline step has been introduced.
