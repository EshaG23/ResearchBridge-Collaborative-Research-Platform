# Module 17: tasks, evidence and approved completion

Open My Projects > Community > To-do > Open task workbench. The mentor or appointed leader creates tasks with a title, description, assignee, optional sprint, due date and milestone. Tasks without a sprint remain in the project backlog. Search and filters support status, sprint and Assigned to me.

The assignee updates progress, reports or clears a blocker and uploads deliverables. Work can be saved before submission. On submission, select existing evidence files to include; newly uploaded files are included automatically. A written submission without attachments is also supported. File limits match chat: five files per upload, 25 MB each, 60 MB total, validated supported formats. Private downloads recheck membership and current agreement verification.

Workflow: Assigned > In progress > Awaiting review > Approved, or Changes requested > Revised submission > Approved. Blocker text is separate from the review state and must be cleared to submit. Mentor or leader reviews other members' submissions; neither may approve their own work. The leader's work requires mentor review. A review includes mandatory feedback and refers to one exact numbered submission and its evidence files.

Task scope and assignment cannot change while submitted or approved. Request changes before editing submitted work, or reopen approved work with a recorded reason. Reopening immediately removes the task from approved totals. Reassignment preserves old history and submissions and clears the current assignee's progress/blocker fields. Current access is checked inside the same locked transaction as each mutation. Stale revision submissions are rejected; retry keys prevent duplicate updates, reviews and notifications.

Every task counts once. Approved task completion = approved task count / total task count. Project and sprint totals come from saved tasks and change when work is approved, reopened or a task is added. Zero-task sprints show an empty state. Sprint status is distinct from approved task completion; neither automatically marks a research project complete.

Files are immutable uploads with uploader, timestamp, original filename and checksum. Each submission retains its own selected file set, even after later uploads. Members can comment on the task or a specific uploaded file. Assignment changes, progress, submissions, reviews, reopenings and comments record community events. Broader cross-project contribution/history views remain Module 18.

In-app notifications cover assignment, submission for review, approval, changes requested and reopening. Notification links use the existing authorised project context; open its community task workbench for the task. No email is sent for these events.

Validation includes permission and self-review denial, leader review of another member, full revision/approval/reopen workflow, progress recalculation, preserved evidence, stale/retry checks, CSRF, scoped files and submissions, agreement revocation, transaction cleanup, and HTTP forms. Isolated browser verification covered task creation, evidence review, approval and 1-of-3 task progress. Live data was not used as test fixtures.
