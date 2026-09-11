# Intended permissions and state transitions

This document records the overall target rules. Modules 1–7 now enforce roster authentication, onboarding, current project access, private files and recipient-scoped notifications. See modules-5-7.md for the implemented permission matrix. Applicant, NDA and community permissions remain for their later modules.

| Actor | Intended access |
|---|---|
| Unauthenticated | Login and OTP only |
| Profile incomplete | Onboarding and essential account controls |
| Completed college profile | College-shared recruitment details |
| Applicant | Own application, letter if selected, relevant invitations |
| Selected unsigned student | Own agreement workflow; no private community |
| Active community member | Private project summary, chat, tasks, files, history, announcements, IP updates |
| Team leader | Project-level summary, task, review, and announcement management |
| Project mentor | Applicant selection, NDA oversight, community creation, leader appointment, IP publishing |
| Administrator | Explicit maintenance powers; not automatic project membership |

The student proposer can see applicant overviews; detailed résumé access is unresolved. A teacher claim does not grant teacher powers. A teacher is not automatically mentor of every project. Original proposer, mentor, and team leader remain separate.

Check permissions server-side for pages, writes, downloads, polling, search, notifications, and document versions. Every nested resource must belong to the authorised project. Signed agreements must not be visible to other students. Internal comments are visible inside the private community only.

## Target transitions

- Authentication: roster-provisioned email and password → mandatory profile → dashboard. Forgot Password uses a bound OTP and password reset; it never creates an account. Demo identities remain explicitly separate and unverified.
- Mentorship: chosen teacher receives one active request → acceptance attaches mentor; rejection advances once to the next ranked candidate. Pending/no candidates must be truthful states. Nonresponse escalation and all-rejected recovery remain future scope.
- Recruitment: applied → shortlisted → selected/not selected. Optional meeting invitations are separate records. Selection → letter issued → agreement pending/completed. No offer accept/decline stage.
- Community: all intended student agreements valid → mentor manually creates once → eligible students and mentor added → mentor appoints student leader. No silent roster removal or automatic creation upon signing.
- Tasks: assigned → in progress → submitted → approved/completed, or changes requested → revised submission → review. Ordinary members cannot self-approve; mentor reviews leader work by proposed default.
- Progress: approved tasks / included sprint tasks × 100. Show a meaningful zero-task state. Submission and revision counts are not completed-task counts.
- Completion: proposed mentor confirmation of final work; never automatically inferred from one sprint reaching 100%. History and community persist.
- IP: teacher-authored updates with flexible statuses. Prepared, submitted, and granted remain distinct. Only deliberately approved shareable achievements leave the community.

Exactly five primary community pages: Summary, Internal Chat, To-do, Announcements, IP Progress. History/document links are contextual, not a sixth primary card.
