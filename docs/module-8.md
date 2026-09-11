# Module 8 — mentor matching and sequential requests

## Using the workflow

Student: open My Projects, select a saved idea, then Find a mentor / request status. Submit drafts first. Choose an eligible teacher to send the first request. The page becomes a saved priority list with sent times and outcomes.

Teacher: sign in with an approved, completed faculty profile. Open Mentor requests in the sidebar, or open a notification and choose Review and respond. Read the recruitment information and accept or decline. Confidential notes/files are inaccessible before acceptance.

Acceptance attaches the teacher as mentor, preserves the student as original proposer, opens recruitment and adds the project to the mentor's My Projects. Rejection records the decision and approaches the next eligible candidate exactly once. The student receives persistent updates. Queued teachers receive neither notifications nor unpublished project access.

Both demo.teacher@rbunagpur.in and faculty.one@rknec.in are provisioned faculty identities. Each must complete its profile before appearing in recommendations; merely appearing in a roster is insufficient. This module does not automatically populate or complete user profiles.

## Matching defaults

Research domain appears in faculty interests: 50 points. Faculty department is among project departments: 20 points. Shared required skills: up to 30 points, proportionate to coverage and rounded to an integer. Ties use case-insensitive faculty name then user ID. These are explainable matching points, not probabilities or machine learning.

Only active, approved faculty with completed matching-role profiles in the same demo/real category are ranked. Zero-overlap candidates remain available for cross-disciplinary choices with an explicit explanation. Faculty cards show professional details, never phone numbers or résumés.

The chosen candidate goes first; remaining candidates retain descending rank. Order, scores and reasons are saved when the request starts. Later profile/project edits do not silently reorder the active queue. Reviewers see the current recruitment information and submit its revision; stale decisions are rejected with a reload instruction.

## State and access rules

One MentorSearch per project: pending, accepted or exhausted. Each candidate has queued, pending, accepted, rejected or skipped state. Only one pending request per search is allowed by a database constraint. Queued candidates who lose eligibility are skipped when their turn arrives. Pending recipients who lose approval cannot view or decide; there is no automatic timeout/escalation.

Only the original student proposer starts a search. Only the current, approved recipient can decide. Pending recipients can view recruitment details and the decision page, not private records, files or edits. Acceptance grants the existing project mentor permissions. Former recipients retain decision history but no private access. Rejected recipients lose unpublished recruitment access.

The search, decisions, project changes and notifications are transactional. A project write lock serialises starts/decisions. Retried starts return the existing search. Repeated identical decisions do not create notifications or advance twice; conflicting later decisions are rejected. Notification deduplication remains enforced by recipient/event keys. No broad faculty or staff access is granted.

## Boundaries and verification

An empty candidate list and an exhausted search are shown truthfully. There is no fabricated acceptance. Nonresponse escalation and recovery/restarting after every candidate rejects remain the original future scope. No email is sent for mentor requests: notifications are in-app.

All 68 Django tests passed after implementation, including 13 new mentorship tests. Coverage includes scoring, eligibility, chosen-first ordering, one active request, non-broadcasting, private access denial, rejection forwarding, retries, exhaustion, approval revocation, stale decisions, CSRF, rollback, proposer preservation, recruitment publication and persistence across login/logout. Migrations applied and no pending model changes remain.

Browser verification opened the saved student idea and matching faculty recommendations. No request or decision was submitted against the user's saved ideas during visual checks; request and decision changes were tested in an isolated test database.
