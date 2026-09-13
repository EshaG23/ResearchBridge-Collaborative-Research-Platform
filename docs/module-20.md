# Module 20: local release and verification

Implemented connected workflow tests, department-targeted publication notifications, authorised task/outcome notification links, health endpoint, launch/setup scripts, production environment reference and verified database/file backup and restore commands.

The full regression suite passed: 156 tests. This includes selection/agreement/community/task review/completion/IP/achievement flow, permissions and backup corruption checks. Production settings passed Django deployment checks using temporary test configuration, and static collection and dependency checks passed. These checks do not mean the application has been publicly deployed.

SMTP configuration supports real email, but actual delivery needs project mailbox credentials. Public deployment needs a chosen host, domain, HTTPS and persistent storage. Neither live SMTP delivery nor public hosting has been completed or claimed. The laptop demo continues to use its explicitly labelled demo OTP.

## Final chat/history corrections

Poll forms contained a button named action, which shadowed HTMLFormElement.action and sent requests to an invalid URL. The client now reads the action attribute explicitly. Voting uses select then Save vote, with saved-choice indicators, vote changes, manager/creator close and reopen controls, and revision checks against stale polling responses. Unsaved choices are preserved during refresh. Browser verification saved a student vote, changed it and confirmed it survived reload.

Community history opens as a separate page with member/date/type filters and compact change details. It links to the existing document version and contribution views. The page was inspected in the browser.

## Fresh demo

The previous demo was backed up with verified checksums, restored into a separate directory to verify recovery, and archived before a fresh migrated database was created. Five students and five teachers were imported. All profiles require onboarding; project, community, task, chat, notification and upload data were cleared. See ../demo_rosters/README.md for the fictional accounts.
