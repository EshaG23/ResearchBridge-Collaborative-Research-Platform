# Modules 5–7: private access, notifications and ideas

## Try the features

1. Log in using a registered demo account and complete its profile if needed.
2. Open Create idea in the sidebar. Enter title, domain, departments, a recruitment summary (up to 240 characters), skills and 1–100 open positions. Available roles and confidential notes are optional.
3. Save draft, or submit. Students see Awaiting mentor; approved faculty can publish immediately and become the mentor. All recruitment fields are required even for drafts.
4. Use Created Ideas for your original proposals; My Projects includes proposals and projects you are authorised to mentor.
5. Open Confidential space to read private notes or upload a PDF. Add version preserves every earlier file. Current idea attachments support readable, unencrypted PDFs up to 5 MB and 50 pages; later task modules add their required file formats.
6. Open Notifications. Idea saves persist here after logout. View idea marks the event read and checks your current access before navigating. Polling refreshes the unread count every 30 seconds and pauses in hidden tabs.

## Enforced permissions

| Resource | Allowed users |
|---|---|
| Published recruitment overview | Active roster users with completed matching-role profiles |
| Draft or awaiting-mentor overview | Proposer and attached approved mentor |
| Confidential idea, project PDFs and versions | Proposer and attached approved mentor |
| Create idea | Completed-profile students and approved faculty |
| Edit idea and upload project PDF | Authorised proposer or attached approved mentor |
| Profile résumé history/download | That résumé's owner only |
| Notification list, poll and read action | Recipient only |

Faculty approval is checked for faculty project management, including faculty-owned ideas. Unrelated faculty and staff do not gain private access. An attached mentor who loses approval is denied private access and excluded from My Projects. Future application résumé access must be scoped to a particular application snapshot, not an unrestricted profile URL. Community access will be added only after its real NDA/membership workflow exists.

## Persistence and retry behaviour

Project, confidential record, taxonomy links and saved-idea notification commit together. A per-creator submission UUID prevents duplicate ideas on retries. An edit revision prevents overwriting a newer edit from another window. Notification recipient/event-key uniqueness prevents duplicate delivery records; read timestamps are preserved on retries.

Project files use random storage names outside static/public routes. Each immutable version stores document/project context, uploader, time, original filename, byte size and SHA-256. Failed metadata saves remove newly written files. No public media route is installed. Back up the database and private uploads together as described in operations.md.

Recruitment records never contain confidential text. Notification messages contain generic event text, not private research content; the service accepts only a project reference for navigation, never a supplied external URL. Recheck destination access when generating polling links and when opening a notification.

## Remaining workflow dependencies

Student mentor matching and acceptance come next. Discovery filtering, applications, letters, NDA, community membership, tasks and IP are separate later modules. There is no applicant/community membership bypass. The database-backed notification infrastructure is ready for those events. Real password-reset SMTP delivery still needs private setup and an actual delivery test.
