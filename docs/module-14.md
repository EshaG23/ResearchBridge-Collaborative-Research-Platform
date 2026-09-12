# Module 14 - Private communities and team leaders

Implemented mentor-controlled creation, transactionally gated by every intended student's verified agreement and active completed account. The confirmation binds the reviewed roster, evidence versions, status and project revision for 15 minutes. A missing or changed agreement blocks creation; empty rosters are not ready. Duplicate creation returns the same community without duplicate members/events/notifications.

Creation adds the mentor and all intended eligible students. Student proposers remain distinct and require explicit intended-team enrollment and verification to enter the community. Original idea authors retain their pre-existing authoring permissions outside community membership. A mentor can explicitly admit later verified students through the roster checklist. This is an append-only admission policy: no silent removals, and later selection does not auto-admit anyone.

Every community page checks current account and agreement eligibility. Corrected/unverified student agreements pause entry and leader privileges immediately. Current approved project mentors retain oversight; prior mentors gain no access from a stale membership alone. Protected project documents use the shared permission check. Admitted students see the project in My Projects and get download-only document controls unless they already have project management authority.

Mentors appoint or replace one eligible student leader per project, with optimistic revisions, idempotent confirmation keys, durable history and notification. There is no automatic proposer-to-leader assignment. can_edit is the project-scoped policy hook for later collaboration editing features.

The colourful landing page has exactly five primary destinations: Summary, Internal Chat, To-do, Announcements, IP Progress. Summary exposes existing confidential details and private documents. The other routes are protected foundations with explicit unavailable states: summary editing/sprints (15), chat/announcements (16), tasks (17) and IP features (19) are not claimed as implemented in 14. No fabricated progress or sprint data.

Verification: 118 full-regression tests passed before integration polish, then six focused community tests passed including admitted My Projects visibility and read-only document controls. Coverage includes roster blocking/staleness, duplicate creation, all five protected routes, mentor-only/project-scoped leadership, correction revocation, CSRF and outsider denial. The landing page was visually inspected using synthetic test-database content.

Operations: communities.0001_initial migration. Database and uploads must be backed up together. Future reset order must remove CommunityEvent and Membership before Community, then agreement/application/project records. No user data was reset or demo memberships created in the live database.
