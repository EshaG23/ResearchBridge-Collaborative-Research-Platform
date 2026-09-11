Copy the entire prompt below into your new Codex task. It captures your **final ten-part project**, including your corrections. It is a **context-setting prompt**, so it asks Codex to understand and document the requirements before starting implementation.

I’ve separated confirmed requirements from suggested technical defaults so implementation choices don’t silently change your project. This structure follows the emphasis on clear context and task boundaries in [OpenAI’s prompting guidance](https://learn.chatgpt.com/docs/prompting).

RESEARCHBRIDGE — MASTER PROJECT CONTEXT AND REQUIREMENTS

Read this entire specification carefully before responding.

This is the primary context prompt for my project. Its purpose is to explain the complete application, the exact workflow my team has finalised, the interface we want, and our technical constraints.

Do not start building the whole application immediately after receiving this prompt. First understand the requirements, preserve them in project documentation, and identify the implementation dependencies. I will subsequently ask you to plan or implement specific parts.

Do not reduce this specification to a generic project-management website. The recruitment process, mentor involvement, confidentiality requirements, private project community, task review, contribution history, and IP progress are connected parts of one workflow.

When implementation begins, build complete working features with real database persistence. A beautiful interface with nonfunctional buttons is not sufficient.


**A. PROJECT BACKGROUND AND PURPOSE**

This is our college Idea Lab project, worth 25 marks.

We need a full-fledged working application that we can demonstrate from beginning to end.

The temporary product name is ResearchBridge.

The intended institution is Ramdeobaba University, Nagpur.

The application is restricted to eligible college users with email addresses whose domain is exactly:

rbunagpur.in

The main users are students and teachers.

The application helps them:

- Post research project ideas without publicly revealing the full confidential idea.
- Find a suitable teacher mentor for student-created projects.
- Discover projects recruiting students.
- Apply using a résumé and relevant details.
- Review and shortlist applicants.
- Communicate selection through offer letters.
- Collect mandatory confidentiality agreements.
- Create a private project community.
- Collaborate through summaries, chat, sprints, tasks, announcements, and documents.
- Review completed work.
- Automatically preserve project history and contribution records.
- Mark a project completed.
- Follow teacher-posted updates about the college’s intellectual property process.

There are exactly TEN agreed product parts.

The eighth part contains several connected subsections. Do not count those as additional top-level product parts.

Earlier discussions mentioned twelve parts and a much larger module list. Those have been superseded by the ten-part specification below.

ResearchBridge should look professional and suitable for a university setting, but do not claim official university endorsement or authorisation unless I provide it.


**B. HOW TO INTERPRET THIS SPECIFICATION**

Requirements explicitly described in the ten parts are the agreed product scope.

Technical details described as “suggested default,” “proposed,” or “implementation recommendation” are practical starting points, not additional decisions supposedly made by my team.

When a detail is genuinely unresolved:

- Record it.
- Make a reasonable, reversible technical choice when possible.
- Explain the assumption.
- Ask me only when the answer materially changes the product, access permissions, institutional process, or required external setup.
- Continue independent work when implementation has been authorised.

Do not silently reintroduce features that we placed in future scope.

Do not reinterpret our offer-letter workflow as a conventional recruitment system with an additional accept/decline stage. Our simplified decision is explicitly explained in Parts 6 and 7.

Do not treat a missing NDA as signed merely to complete the demonstration.

Do not interpret “public dashboard” as accessible to everyone on the internet. It means shared within the authenticated college application.


**C. AGREED TECHNICAL DIRECTION**

Our preference is simplicity, a Python backend, easy deployment, and no required payments or payment details.

Frontend:

- HTML rendered through Django templates.
- Custom CSS.
- JavaScript for interactive behaviour.
- Reusable template components and shared styles.
- Responsive layouts for desktop and mobile.

We originally considered React as an option, but the agreed starting recommendation is HTML, CSS, and JavaScript with Django.

Do not switch to React, Next.js, or another frontend framework without a concrete reason and discussion.

Backend:

- Python.
- Django.
- Organise the application into separate Django apps or clearly separated business modules.
- Keep business rules understandable and testable.
- Use Django’s established session, form-validation, and security mechanisms.

Database:

- SQLite for the initial small working demonstration and initial simple deployment.
- Use Django models and migrations.
- Keep the design compatible with a later PostgreSQL migration.
- Do not assume SQLite is suitable for unlimited concurrent college-wide usage.
- Do not require a separate paid database subscription.

Files:

- Store files privately on persistent storage for the initial deployment.
- Keep database metadata for ownership, project, task, document version, upload time, and uploader.
- Back up both the database and files.
- Never rely on temporary deployment storage for important project records.

Email:

- Demo OTP first, using the explicitly restricted demo mode described in Part 1.
- Real email OTP later through an email integration.
- A dedicated Gmail account with SMTP and an App Password is the proposed small-demo option, subject to current account eligibility and actual delivery testing.
- Verify current official setup instructions when implementing.
- Never request a paid email service or payment card as a default requirement.

Deployment:

- PythonAnywhere Free is the proposed initial host.
- Verify its current storage, network, web-app renewal, and other limits before deployment.
- Do not promise unlimited free hosting or permanent service availability.
- If it cannot support the agreed demonstration, explain the exact limitation and investigate another genuinely free option that does not require payment details.
- Keep the project runnable locally regardless of hosting availability.

Other implementation preferences:

- Database-backed notifications.
- Database-backed internal chat.
- Periodic JavaScript fetching of new chat messages and notifications is acceptable initially.
- Python rules for mentor matching.
- Optional PDF résumé extraction with a free Python library.
- Django admin for necessary administrative maintenance.
- Git for source history.
- Django tests and browser-based verification for meaningful workflows.

Do not introduce paid AI APIs, Redis, Celery, Kubernetes, microservices, a vector database, or separate chat services unless a later requirement genuinely needs them.

Our agreed features must work without a paid AI model.


**D. VISUAL DESIGN — VERY IMPORTANT**

The interface must be exceptionally polished, clean, restrained, and professional.

The requested palette is:

- Blue.
- Black or near-black.
- White.
- Supporting neutral greys.

Suggested visual treatment:

- Deep navy or dark blue navigation.
- White primary content surfaces.
- Blue primary action buttons.
- Near-black readable body text.
- Subtle grey borders.
- Light neutral background where useful.
- Consistent typography.
- Moderate corner rounding.
- Small, consistent icons.
- Purposeful spacing.
- Subtle shadows only where they improve separation.

The interface should feel like a carefully designed university research portal.

Avoid:

- Gaudy colours.
- Neon.
- Decorative gradients.
- Glass effects.
- Excessive animation.
- Large decorative illustrations.
- Oversized headings.
- Random colours for every section.
- Emoji-based navigation.
- Repeated cards inside cards without purpose.
- Fake statistics.
- Fake achievements.
- Unnecessary marketing sections.

Professional appearance must apply to all pages, including:

- Login and OTP.
- First-time profile setup.
- Shared dashboard.
- Create Idea.
- Public recruitment details.
- Application form.
- Applicant management.
- Mentor requests.
- Offer letters.
- Agreement records.
- Community overview.
- Summary.
- Internal chat.
- To-do.
- Announcements.
- Project history.
- IP progress.

Use:

- Clear labels.
- Helpful validation messages.
- Visible focus states.
- Keyboard-accessible controls.
- Appropriate colour contrast.
- Responsive tables and forms.
- Empty states with relevant next actions.
- Loading and saving indicators.
- Meaningful success and failure messages.

Desktop project discovery must show three vertical project cards side by side when the screen width permits.

On smaller screens, adapt to two or one column without horizontal overflow.

A sidebar, compact top bar, notification bell, and profile menu are suitable shared navigation defaults.

Use the college’s actual logo or letterhead only when an authorised asset is provided. Until then, use a clearly replaceable text identity or labelled placeholder.

Technical setup messages belong in development or administrative contexts, not scattered throughout ordinary student workflows.


**PART 1 OF 10 — COLLEGE-ONLY ACCESS, EMAIL OTP, LOGIN, LOGOUT, AND PERSISTENCE**

**Purpose**

Only eligible college users should access the application. User accounts and saved work must remain intact after logout.

**Entry behaviour**

When an unauthenticated person opens the application or its deployed link, show the login/sign-up page.

Do not first display a generic marketing landing page.

If an authenticated user has an incomplete profile, direct them to mandatory profile completion.

If an authenticated user already has a completed profile, direct them to the main dashboard.

**College email restriction**

Accept only an email address whose domain is exactly rbunagpur.in.

The comparison should be case-insensitive.

Trim accidental surrounding spaces.

Validate the entire email structure, not just whether the string contains the college domain.

Reject:

- Personal Gmail addresses.
- Yahoo or Outlook addresses.
- Other college domains.
- Addresses such as someone@rbunagpur.in.example.com.
- Invalid or incomplete email addresses.

Do not allow a personal email to proceed to registration.

The interface should clearly explain the problem and disable the relevant continuation action while the email is invalid.

The server must independently enforce the same restriction. Bypassing the interface must not bypass eligibility checks.

**OTP sign-up and login**

The user enters their college email and requests a code.

For real authentication:

- Generate a random six-digit code securely.
- Send it to the entered eligible email.
- Bind it to the intended email and authentication attempt.
- Make it expire after three minutes.
- Display a matching countdown.
- Enforce expiration on the server.
- Make a successfully used code unusable again.
- Limit repeated incorrect attempts.
- Limit repeated requests.
- Show a resend cooldown.
- Ensure requesting a replacement code cannot leave old codes unexpectedly valid.
- Do not put OTPs or credentials into ordinary logs.

Suggested configurable defaults:

- Three-minute validity.
- Sixty-second resend cooldown.
- Five incorrect attempts per challenge.

These are implementation defaults, not a reason to build a complicated authentication interface.

Create or activate the real user account only after successful verification.

A code being sent is not proof that the user owns the email account.

**Temporary demonstration OTP**

For the initial development demonstration, use:

123456

This must be implemented as an explicit demo authentication mode.

Requirements for demo mode:

- Clearly label it as a demonstration.
- Restrict it to designated demo identities.
- Continue validating the college email format.
- Keep demo data separate from real private research data.
- Do not claim demo users have verified ownership of real college inboxes.
- Do not allow the fixed code to authenticate arbitrary real users on a public deployment.
- Disable fixed-code authentication when real OTP mode is enabled.
- Use the demo flow to test the timer and navigation without pretending a real email was sent.

Demo mode should let us build and demonstrate the application while real email setup is pending.

**Free real email mechanism**

When real delivery is required:

- Investigate the proposed dedicated Gmail SMTP route using current official instructions.
- Explain the account setup in simple language.
- Explain two-step verification and App Password availability where applicable.
- Tell me where to enter credentials privately.
- Do not ask me to paste secret credentials in chat.
- Do not ask for ownership of the college domain merely to send email to college recipients.
- Test delivery to an approved test inbox.
- Report delivery as unverified until the test actually succeeds.

Email is used for authentication OTPs.

Recruitment updates, mentor requests, interviews, offers, tasks, and IP updates should use the application’s notification system.

**Logout and permanent saved progress**

The account/profile menu must include Logout.

Logging out ends the login session.

It must not delete:

- Profile details.
- Résumés.
- Created ideas.
- Mentor requests.
- Applications.
- Selection letters.
- Agreement records.
- Community membership.
- Chat messages.
- Tasks.
- Uploaded files.
- Document versions.
- Contribution history.
- Project progress.
- IP updates.

The next successful login should restore access to the user’s saved records.

Browser local storage is not the main database.

If a save fails, show that failure. Never show “saved” for information that exists only temporarily in the browser.

**Acceptance example**

A student signs in, completes a task, uploads a PPT, logs out, and later logs in again.

The task status, PPT, comments, and activity history must still exist.


**PART 2 OF 10 — MANDATORY FIRST-TIME PROFILE**

**Purpose**

Every new user completes a role-specific profile before reaching the shared dashboard.

**First-time flow**

Email verification → Mandatory profile setup → Shared dashboard.

**Returning-user flow**

Login → Shared dashboard, provided the profile is already complete.

If the user leaves midway through onboarding, the next login should return them to unfinished profile setup.

**Role choice**

The profile page begins with two choices:

- Student.
- Teacher.

Show relevant fields according to that choice.

**Student profile fields**

Include:

- Name.
- Department.
- Phone number.
- College email ID.
- Skills.
- Research interests.
- Availability in hours per week.
- PDF résumé upload.
- Current year of study.

The verified college email should appear automatically.

Do not let the user silently replace it with an unverified personal email.

Use structured choices or tags for shared matching attributes wherever practical.

Validate:

- Name presence.
- Department selection.
- Phone format.
- Reasonable availability values.
- Year selection.
- Allowed résumé file type and size.

The student profile fields are required for a completed student profile unless we later explicitly change a field’s requirement.

**Teacher profile fields**

Include:

- Name.
- Department.
- Phone number.
- College email ID.
- Skills.
- Research interests.
- Previous research work — optional.
- Google Scholar link — optional.

Do not show student-year fields to teachers.

Do not require a teacher résumé unless we later add that requirement.

The teacher profile’s department, skills, and research interests should use the same underlying terminology as project requirements where appropriate.

**Teacher eligibility**

Selecting “Teacher” records a role claim; it should not automatically grant powerful teacher permissions to any student who selects it.

The exact college verification process is not yet finalised.

For the initial controlled demonstration, use explicitly provisioned or administrator-approved teacher accounts. Record that as an implementation default.

Do not invent faculty verification from email ownership alone.

**Department data**

Use a controlled department list rather than different free-text spellings everywhere.

When real department names are needed, obtain them from an appropriate university source or from me.

Clearly label temporary fixtures.

**Profile editing**

After onboarding, users should be able to reopen their profile and update permitted details.

Updating a résumé should create a new profile résumé record/version without silently replacing the résumé attached to an earlier application.

Phone numbers, full résumés, and private profile data should not automatically appear on all project discovery cards.

**Acceptance example**

A new student chooses Student, fills in the required details, uploads a PDF résumé, and reaches the dashboard.

After logout and login, the application opens the dashboard directly and retains the completed profile.


**PART 3 OF 10 — ACHIEVEMENT BOARD, IDEA CREATION, AND MENTOR MATCHING**

This part includes the later correction about teacher priority order.

**Achievement board**

At the top of the shared dashboard, show an achievement board or scrolling banner.

It highlights college research projects with relevant completion and IP milestones.

Examples:

- Project completed and IP application submitted.
- Intellectual property protection granted.

Keep “applied” and “granted” visibly distinct.

Do not describe an application as a granted right.

The time range is flexible. We discussed periods such as:

- Last three months.
- Last six months.
- Last year.

Treat the default range as configurable, not as a final hardcoded institutional policy.

The banner should use approved, shareable information only.

Suggested implementation default:

- A teacher or authorised administrator approves an achievement for display.
- A private IP update is not automatically made visible to the whole college.

Do not invent achievements to make the dashboard appear populated.

For demonstration data, label achievements as demo records.

If the banner scrolls, make it readable and provide an accessible pause or reduced-motion behaviour.

**Create Idea entry point**

Show a simple Create Idea button on the dashboard.

Clicking it opens a separate page.

Both students and teachers can create ideas.

**Public recruitment information**

The form includes:

- Project title.
- Research domain.
- Relevant department or departments.
- A short one-to-two-line description.
- Required skills.
- Number of open positions.
- Available roles where relevant.

The short description is intentionally limited because the complete idea should remain private.

Define a reasonable text limit that produces approximately one or two lines in the intended layout. Record that limit as a UI implementation choice.

Do not make the detailed confidential idea part of public recruitment data.

If private project information is stored before the community exists, keep it in separately protected fields or records.

**Student-created idea**

A student enters the idea’s recruitment information.

Before forming the team, the student can seek a teacher mentor.

At the applicant-review stage, the intended workflow requires an attached teacher mentor.

**Shared matching attributes**

Teacher profiles and project forms must share appropriate attributes, such as:

- Department.
- Research domain or interest tags.
- Skills.

Do not match independently typed inconsistent labels without normalisation.

The exact matching weights have not been finalised.

Suggested initial implementation:

- Deterministic Python scoring using shared attributes.
- Prioritise meaningful domain and research-interest overlap.
- Use skills and department compatibility as supporting factors.
- Document the scoring rules.
- Show understandable reasons for recommendations.
- Do not describe the ranking as a scientific probability or claim it uses machine learning if it does not.

**Priority list and request flow**

Show the student a ranked list of suitable teachers.

Each entry should show enough professional information to help the student understand the match:

- Name.
- Department.
- Relevant research interests.
- Relevant skills.
- Optional research background or Scholar link.
- Explanation of shared matching attributes.

The student can select a teacher to approach from the suggestions.

The mentor request then follows the priority-list workflow.

Because the original selection interaction and the later priority-order correction must both be preserved, use this proposed default unless I change it:

- The student initiates a request to the chosen suggested teacher.
- That teacher becomes the current recipient.
- The remaining candidates are kept in their matching priority order.
- Only one active request is sent at a time.
- If the teacher rejects, the next eligible teacher receives the request.

Do not broadcast the same request to every teacher simultaneously.

**Teacher notification**

The requested teacher receives an in-app notification.

It identifies:

- The student.
- The proposed project.
- That a mentor request needs attention.

Clicking the notification opens the relevant idea’s recruitment information.

Before acceptance, the notification and linked request should not reveal confidential project information beyond the permitted recruitment details.

**Teacher decision**

If the teacher accepts:

- Record the acceptance.
- Attach that teacher as the project mentor.
- Show the updated mentor status to the student.
- Give the mentor the project-specific management access required by later parts.

If the teacher rejects:

- Record the rejection.
- Send the request to the next teacher in the priority order.
- Prevent duplicate active mentor requests.

Handling a teacher who never responds, or a situation where all suggested teachers reject, is future scope.

The current implementation must still represent “pending response” or “no remaining candidate” truthfully. It must not fabricate an acceptance or crash.

**Teacher-created idea**

A teacher can post the same recruitment information directly.

The teacher serves as the project’s teacher/mentor.

A separate mentor-matching step is unnecessary.

The published recruitment notice appears on all students’ shared dashboards.

**Preserve the original proposer**

If a student created the idea, keep that student recorded as the original proposer after a teacher joins or a team leader is appointed.

Original proposer, mentor, and team leader are different concepts.


**PART 4 OF 10 — PROJECT DISCOVERY AND APPLICATIONS**

**Dashboard discovery**

Initially show all published projects currently recruiting students.

The student should be able to explore outside their own department.

Do not automatically hide every project outside the student’s department.

Provide sorting and filtering, especially by:

- Skills.
- Department.
- Research domain.

Other useful sorting controls may be added if they remain simple and are documented as implementation choices.

Filtering should help a student narrow the list to relevant projects.

For example, a Computer Science student may choose to focus on projects matching their skills instead of browsing Civil or Mechanical projects.

**Card layout**

Use vertical project cards.

At desktop width, show three cards horizontally in one row.

Each card should show useful recruitment information without exposing the complete private idea.

Suitable information includes:

- Title.
- Short description.
- Domain.
- Department.
- Skills.
- Open positions.
- Proposer or mentor identity where appropriate.

**Project details page**

Clicking a card opens a separate page.

Show all public-within-college recruitment details submitted by the proposer.

Provide an Apply button.

Do not show:

- Confidential research description.
- Private summary documents.
- Community chat.
- Private task files.
- Other applicants’ résumés.
- NDA records.

**Application résumé choices**

The applicant must have two clear options:

1. Use the PDF résumé already stored in their profile.
2. Upload a different PDF résumé for this application.

Show which file will be submitted.

Allow the applicant to review the selected résumé before submission.

Uploading a different application résumé must not silently overwrite the profile résumé.

If an “also update my profile résumé” option is added, it must be explicit and optional.

Preserve the résumé submitted with each application even if the student later edits their profile.

**Two implementation levels**

Required baseline:

- Select an existing résumé or upload a new PDF.
- Submit the application with the relevant profile/application details.
- Make the submitted information available to the authorised teacher.

Preferred enhancement:

- Extract relevant information from the selected PDF.
- Use it to prefill an application form.
- Allow the applicant to correct the extracted values before submitting.

Example:

If the résumé states a CGPA, extract that value and populate the CGPA field.

Other possible extracted information includes name, skills, education, or projects, where extraction is reliable and the application form needs those fields.

CGPA is an example of an application field. It was not specified as a mandatory original profile field.

**Autofill behaviour**

- Do not guess missing details.
- Leave uncertain or absent fields blank.
- Do not silently invent a CGPA.
- Do not assume a grading scale when it is not stated.
- Handle scanned or unreadable PDFs gracefully.
- Keep manual entry available.
- Do not block the application just because extraction fails.
- Do not add a paid AI service for this feature.

The enhanced approach is preferred if it works reliably. The baseline remains an acceptable implementation.

**Application submission**

Save:

- Applicant.
- Project.
- Submitted résumé version.
- Submitted form details.
- Submission time.
- Application status.

Use the submitted data as a historical snapshot.

Prevent duplicate applications caused by repeated button clicks.

Show a clear success message and a way to view the submitted application status.

Suggested supporting controls such as closing recruitment should stop new applications truthfully, without erasing existing submissions.

**Acceptance example**

A student filters by Python and AI, opens one of three matching cards, chooses their existing résumé, reviews the application, and submits it.

The project’s authorised teacher can then see that application and its original submitted résumé.


**PART 5 OF 10 — APPLICANT REVIEW, SHORTLISTING, AND OPTIONAL MEETING**

**Access from the proposer’s dashboard**

A student or teacher who created an idea must be able to locate it from their dashboard.

A My Projects or Created Ideas area is a suitable navigation implementation.

Opening the project allows the creator to see who has applied.

By this stage:

- A teacher-created project already has its teacher.
- A student-created project should have its accepted mentor.

**Decision authority**

The teacher/mentor reviews applicants and shortlists students.

Do not give the student proposer teacher-only selection powers merely because they created the idea.

The proposer can see the applicant overview. Private résumé access should be limited to authorised reviewers; the exact extent of student-proposer résumé access remains a permission detail to document before implementation.

**Applicant review interface**

Provide a professional applicant-management page.

A table or well-organised list is appropriate.

Show relevant information such as:

- Student name.
- Department.
- Year.
- Skills.
- Availability.
- Application date.
- Application status.
- Link to the submitted résumé.
- Submitted application details.
- Review actions available to the current user.

The mentor should be able to open an applicant’s record and review the résumé and details.

**Shortlisting**

The teacher shortlists applicants based on the résumé and submitted details.

An optional meeting may occur before final selection.

Distinguish shortlisted candidates from finally selected students so letters are not issued to everyone who merely reached the shortlist.

Suggested simple states:

- Applied.
- Shortlisted.
- Selected.
- Not selected.

Meeting invitations may be related records rather than a complicated separate state machine.

Do not add elaborate HR workflows unless requested.

**Optional meeting/interview notification**

The teacher can send a simple in-app invitation to a student.

It should contain:

- A message such as “I would like to meet you regarding this project.”
- Date.
- Time.
- Venue.

An optional online meeting link may be supported if useful, but building video calling is not required.

Use clear local time display appropriate to the college, with unambiguous stored timestamps.

The notification should link to the relevant project/application context.

Only the intended applicant and authorised project reviewers should see private meeting details.

A full calendar system, meeting negotiation workflow, or video-call system is not required.

**Preserve the original Part 5 scope**

A later message summarised Part 5 as teacher shortlisting. That did not remove:

- Viewing applicants.
- Reviewing résumés.
- Reviewing submitted details.
- Optional meeting notifications.

All of those remain included.


**PART 6 OF 10 — OFFER LETTERS / SELECTION LETTERS**

**Purpose**

After the teacher finalises selection, the selected students receive an offer letter communicating their selection.

The user called these offer letters. The interface can retain that wording.

**Recipients**

Issue letters to selected students, not every applicant.

A shortlisted student who has not been finally selected should not automatically receive one.

**Contents**

Suggested practical contents:

- Student name.
- Project title.
- Selected role.
- Teacher/mentor name.
- Issue date.
- Selection reference.
- Instruction to complete the mandatory confidentiality agreement.
- Explanation that private community access follows agreement completion and mentor community creation.

Use actual project and student data.

Do not invent official signatures, institutional authorisation, or terms.

Store the issued letter or a reproducible immutable record of its exact contents.

A printable or downloadable PDF is an appropriate implementation.

Deliver the notification inside the application; non-OTP email delivery is not required.

**Important simplified workflow**

There is no separate student-facing Accept Offer or Decline Offer workflow in our final requirements.

The student has applied, and this letter communicates selection.

The next required action is agreement completion.

Do not reintroduce offer acceptance merely because it is common in employment systems.

This simplification does not allow the system to mark an unsigned agreement as signed.

An issued selection letter does not grant private project access.

Suggested status presentation:

- Selected.
- Letter issued.
- Agreement pending.
- Agreement completed.
- Community access active.

These represent different facts and must not be collapsed into one status.


**PART 7 OF 10 — MANDATORY CONFIDENTIALITY AGREEMENT / NDA**

**Purpose**

Every selected student who will join the private community must complete the required confidentiality agreement.

The intended agreement covers confidentiality:

- While working on the project.
- After leaving the project.
- When leaving due to unforeseen circumstances.

The agreement relates to the confidentiality of project details and intellectual property work.

The team intends this to be a formal college agreement retained for institutional records.

**College letterhead and wording**

The agreement should use the college’s authorised letterhead when supplied.

The college-approved agreement text and any required signing process must come from the appropriate college authority.

Until those are supplied:

- Use a clearly labelled sample template for development.
- Keep the letterhead replaceable.
- Do not present generated wording as college-approved.
- Do not claim that a drawn signature, checkbox, or file upload alone guarantees legal validity.

Implement the recording workflow; do not claim to provide a certified legal-signature service.

**Signing options**

The agreed requirement allows:

- Electronic completion/signing, using the process eventually approved for this project.
- Physical signing followed by a recorded copy.

The exact electronic signing mechanism is still to be settled.

For a physical agreement, a proposed implementation is:

- Upload a PDF or image scan.
- Associate it with the correct student and project.
- Let the mentor verify receipt and suitability.
- Record who verified it and when.

Simply uploading a random file must not automatically satisfy the agreement requirement.

**Agreement records**

Store:

- Project.
- Selected student.
- Agreement version or exact document.
- Completion method.
- Relevant completion date/time.
- Uploaded signed file or electronic acceptance evidence.
- Verification status where applicable.
- Verifier and verification time.
- Corrections or replacement history.

Protect these records.

Students should not access other students’ signed agreements.

An authorised mentor or designated college recordkeeper should be able to retrieve records they are permitted to manage.

**Community gate**

The mentor creates the community only after all intended selected student members have completed the required agreement.

The community-creation page must show:

- Intended student members.
- Agreement status for each.
- Any missing or unverified agreement.
- Whether creation is currently allowed.

There is no separate decline button.

If someone has not signed, that student remains without private community access.

Do not silently remove unsigned students from the intended roster to enable creation.

If the intended roster needs changing, that must be an explicit, recorded mentor action. Record the exact roster-management rule as a policy detail to finalise.

Apply the NDA requirement to selected student members, including a student proposer if that person is joining the student team.

Do not automatically impose an additional teacher NDA workflow unless we later require one.

**Acceptance example**

Four students are selected.

Three have completed valid agreements and one has not.

The mentor sees the missing agreement and cannot create the community for that four-person roster yet.

Once the fourth agreement is completed and verified as required, community creation becomes available.


**PART 8 OF 10 — PRIVATE PROJECT COMMUNITY AND COLLABORATION**

This is the most important part of the application.

Preserve all the following subsections together under Part 8.

**8.1 — Mentor-controlled community creation**

The private community is not automatically created immediately after selection or signing.

The teacher/mentor controls its creation.

Inside the mentor’s project details, show:

Create Private Project Community

When the mentor clicks it:

- Confirm their project-specific authority.
- Check the selected student roster.
- Check every required agreement.
- Create the community once.
- Add the mentor.
- Automatically add the eligible selected students.
- Record community creation in project history.

Repeated clicks must not create multiple communities or duplicate memberships.

If prerequisites are missing, show a specific explanation.

Once created, the community becomes the primary place for further project discussions and work.

**Private information becomes available here**

Approved community members can now see the full project details.

Before this stage, applicants had access only to recruitment information and their own recruitment records.

Protect:

- Detailed summary.
- Private project documents.
- Internal chat.
- Tasks.
- Comments.
- Announcements.
- Project history.
- IP progress.

Users must not gain access merely by guessing a URL.

**Team leader appointment**

The teacher appoints a student member as the project’s team leader.

Do not automatically make the original student proposer the team leader unless the teacher chooses them.

The mentor retains oversight.

The team leader helps manage day-to-day work because the teacher cannot personally manage every update.

Represent separately:

- Original proposer.
- Teacher/mentor.
- Student team leader.
- Student member.

A team leader role applies within a particular project, not across the whole platform.

**Community main page**

The community has a dedicated overview page.

Show five primary section cards:

1. Summary.
2. Internal Chat.
3. To-do.
4. Announcements.
5. IP Progress.

Each card opens its own page.

Keep these five primary destinations. History and document views can be linked from relevant sections without adding an unrequested sixth main card.

Show useful real project context, such as title, mentor, team leader, members, and current sprint.

Do not display fabricated progress.

**8.2 — Summary and sprint overview**

The Summary page contains the full project explanation and an overview of progress.

The teacher/mentor and team leader can add and update sections.

Ordinary members can read the summary.

Include:

- Project title and basic information.
- Detailed project description.
- Domain.
- Problem statement.
- Objectives.
- Existing solutions.
- Research gap.
- Related PPTs.
- Literature papers.
- Relevant links.
- Other useful project-specific sections.

The summary must be customisable.

A simple implementation can provide structured default sections and additional titled text sections. A complex drag-and-drop page builder is unnecessary.

For custom sections, support practical controls such as adding, editing, and ordering them.

Preserve meaningful edit history where it relates to Part 9.

**Sprint organisation**

The project can be divided into multiple sprints.

Seven sprints was an example, not a fixed requirement.

Support a variable number.

The teacher or team leader can define:

- Sprint title.
- Order.
- Goal.
- Planned dates where useful.
- Status.

Show:

- Which sprint is current.
- What has already been completed.
- What is being worked on now.
- What is planned for the next sprint.
- An overall progress overview.

Task-derived counts should come from actual task records.

Narrative summaries can be edited by the mentor/team leader.

Do not require people to manually duplicate task completion totals in the summary.

Suggested sprint states:

- Planned.
- Active.
- Completed.

Document the chosen rule for whether multiple sprints can be active. A single current sprint is a suitable initial default.

**8.3 — Internal chat**

Provide working internal group chat for community members.

For example, a teacher, one team leader, and three other students should all be able to communicate.

Five people was an example, not a hardcoded team size.

Chat is an essential feature.

Minimum behaviour:

- View project messages.
- Send a message.
- Show sender.
- Show time.
- Display messages in a consistent order.
- Preserve messages after refresh and logout.
- Fetch newly received messages without requiring a full page reload.
- Show failure if a message cannot be saved.
- Prevent accidental duplicate sends.
- Load older messages without requiring an unlimited response.

Periodic background fetching while the page is open is acceptable for the initial version.

Describe it accurately as polling-based chat if that is how it works.

Do not require an external chat service or paid messaging API.

Only project community members can read or send messages in that community.

Do not confuse the public college dashboard with the private group chat.

**8.4 — To-do, task assignment, review, announcements, and section integration**

**To-do purpose**

The To-do page includes:

- Work already done.
- Current work.
- Planning for upcoming work.
- Individual assignments.
- Sprint tasks.
- Timelines.
- Major milestones.
- Review.
- Blockers/problems.
- Progress updates.
- Contribution tracking.
- Files and task discussions.

Completed work and upcoming plans belong within this page. They are not separate main community cards.

**Reference screenshots**

I will later provide screenshots from a Google Developers Group website as references.

Use relevant field and interaction ideas.

Do not copy the exact website design, branding, or unrelated functionality.

Continue with the agreed professional visual direction.

**Task creation and assignment**

The mentor or team leader creates tasks and assigns them to members.

Suggested task fields:

- Title.
- Description.
- Sprint.
- Assigned member.
- Due date.
- Status.
- Related milestone.
- Attachments.
- Comments.
- Blocker information.
- Review information.

Priority can be added as a simple optional field if useful.

Do not require a complex project-management configuration before a team can create its first task.

**Member work updates**

Members can update tasks assigned to them.

They should be able to:

- Report progress.
- Describe completed work.
- Upload evidence or deliverables.
- Add comments.
- Report a blocker/problem.
- Submit work for review.

Do not let members arbitrarily reassign other people’s tasks or grant themselves reviewer permissions.

**Task file example**

A member is assigned to create a PPT.

They upload the PPT to the task and submit their work.

Other authorised project members can discuss that file through comments.

Here, “public comments” means visible inside the private project community. It does not mean visible to the entire college or internet.

**Review and approved completion**

The team agreed to add review before work counts as approved.

Suggested task workflow:

Assigned → In Progress → Submitted for Review → Approved/Completed

If changes are needed:

Submitted for Review → Changes Requested → Revised Submission → Approved/Completed

Represent blockers either through a clear separate flag or a documented state without losing the main review status.

The mentor or authorised team leader reviews submissions.

An ordinary member cannot approve their own submission.

Suggested default for team-leader tasks:

- The mentor reviews the team leader’s own work.

Record:

- Submitter.
- Submission time.
- Submitted file version.
- Reviewer.
- Review time.
- Feedback.
- Decision.

**Progress calculation**

The agreed starting approach is task-count-based completion.

Example:

- A sprint has ten tasks.
- One task is approved/completed.
- The sprint’s approved task completion is 10%.

Use:

Approved tasks ÷ Total included sprint tasks × 100

Show both the percentage and the count.

Submitting unreviewed work must not increase the approved-completion count.

If a sprint has zero tasks, show a meaningful empty state rather than dividing by zero.

If tasks are added or approved work is reopened, recalculate progress and record relevant changes.

Call this task completion, rather than suggesting it precisely measures research quality or effort.

Do not add weighted tasks, time tracking, or productivity rankings unless requested.

**Milestones and blockers**

Allow the mentor/team leader to define meaningful milestone labels or goals associated with work.

A member should be able to report:

- What is blocked.
- Why.
- What help is needed.

Show unresolved blockers in a useful way.

Blockers should not erase prior work or comments.

**Announcements**

Announcements have their own page.

The teacher/mentor and team leader can post announcements.

Community members can read them.

Store:

- Title.
- Message.
- Author.
- Date/time.
- Relevant update history.

An in-app notification can direct members to a new announcement.

Do not email announcements.

**IP Progress destination**

IP Progress is the fifth primary community section.

Its full behaviour is defined in Part 10.

Ordinary students and the team leader should not automatically receive teacher-only IP status publishing permissions.


**PART 9 OF 10 — PROJECT HISTORY, DOCUMENT VERSION HISTORY, AND CONTRIBUTION TRACKING**

**Purpose**

Automatically preserve the project’s history and connect contributions to actual work.

This is directly linked to the To-do workflow.

Members should not need to manually re-enter the same task completion into a separate contribution form.

**Automatic project history**

Record meaningful saved events, such as:

- Project creation.
- Mentor acceptance.
- Selection.
- Agreement completion or verification.
- Community creation.
- Team leader appointment.
- Sprint creation and start.
- Task creation and assignment.
- Work submission.
- File upload.
- New document version.
- Review decision.
- Approved task completion.
- Blocker reported or resolved.
- Sprint completion.
- Project completion.
- IP status updates.

The essential user requirement is to see who did what and when, including when a sprint started.

Do not log every hover, page view, or unsaved click as a contribution.

Create history from successful business actions.

If a database save fails, do not create a misleading “completed” event.

**History entry contents**

Store enough structured information to show:

- Actor.
- Project.
- Related sprint.
- Related task or document.
- Action.
- Timestamp.
- Relevant previous and new status.
- Link to supporting work.

Show dates and times consistently.

A timeline with filters for member, sprint, date, or activity type is a suitable implementation.

**Contribution tracking**

Derive contributions from:

- Submitted work.
- Uploaded deliverables.
- Document revisions.
- Approved task completions.
- Recorded reviews where useful.

Separate submitted activity from approved work.

For example:

- Student A submitted PPT version 1.
- Mentor requested changes.
- Student A uploaded version 2.
- Mentor approved version 2.

All four events remain visible in the appropriate history.

Do not count each revision as a separate completed task.

Do not automatically assign legal ownership, authorship order, or research quality scores.

Do not erase a contributor’s credit if their display name, role, or membership later changes.

**Document storage and versions**

Documents can be attached to tasks or relevant summary sections.

Support the agreed working file types, such as:

- PDF résumés.
- PDF research papers.
- PPT/PPTX presentations.
- Appropriate document and image files.
- Signed agreement records through their separately protected workflow.

Set configurable type and size limits.

Do not allow arbitrary unlimited uploads.

For each logical document, preserve versions.

A document version should record:

- Logical document identifier.
- Version number.
- Stored file.
- Original filename.
- Uploader.
- Upload timestamp.
- Revision note where applicable.
- Related project/task/section.

Uploading version 2 must not overwrite version 1.

Use unique storage names so identical filenames do not collide.

Mark the latest version clearly.

Allow authorised users to open or download earlier versions.

**Comments and discussions on files**

Members can comment on task files within the community.

Associate comments with the relevant task and, when discussing a specific revision, its document version.

A later upload should not make an older review appear to refer to the new file.

Preserve discussion context.

**History and permissions**

History is private project content.

An outsider should not retrieve it through a timeline endpoint.

Do not expose private file names or comments through public recruitment details.

Protect uploaded files through authorised server access, not merely hidden links.

**Acceptance example**

Sprint 1 begins.

A member uploads a PPT to an assigned task.

The team leader requests changes.

The member uploads a revised PPT.

The team leader approves it.

The application shows:

- Sprint start date.
- Both PPT versions.
- Their uploaders and timestamps.
- Review comments.
- The approved version.
- Updated task completion.
- The member’s recorded contribution.

All of this remains after logout and login.


**PART 10 OF 10 — PROJECT COMPLETION AND IP HANDLING**

**Project completion**

When the project work is finished, support marking the project completed.

Suggested default:

- The mentor confirms completion.
- The team leader can prepare the final work and request that confirmation.

The exact completion authority was not explicitly settled, so record this as a proposed permission default.

Do not automatically mark a project completed solely because one sprint reaches 100%.

The overall project may include multiple sprints and final deliverables.

Store completion date and the person who confirmed it.

Completion does not delete the project community or its history.

**Actual IP process**

The college and teacher handle the actual intellectual property process.

ResearchBridge does not file legal applications automatically.

It does not replace the college’s IP office or the teacher’s responsibilities.

The application’s role is to display progress and communicate required information.

**IP Progress page**

Inside the private community, the teacher posts updates such as:

- IP documentation is being prepared.
- The IP application has been filled/prepared.
- The IP application has been submitted.
- These additional details are required.
- These documents are needed.
- The application is under review.
- An outcome has been received.

These are examples. Do not hardcode every possible legal process into one universal status sequence.

Allow a clear update title/status and explanatory text.

Suggested fields:

- Update title.
- Status label.
- Detailed message.
- Required details or documents.
- Date/time.
- Teacher author.
- Optional supporting attachment.
- Reference number if appropriate and permitted.

The teacher should be able to distinguish “prepared” from “submitted” and “submitted” from “granted.”

Students can follow the updates.

The team leader does not automatically inherit teacher-only IP publishing powers.

**Requests for information**

A teacher can post that specific information or documents are needed.

Members can see the request.

Existing task/file functionality may be linked to fulfil it where appropriate. Do not build a separate complex legal case-management system.

**Connection to achievement banner**

An approved, non-confidential IP milestone can appear on the shared dashboard’s achievement board.

Do not automatically copy all IP update text or attachments into that banner.

Only deliberately approved shareable information should appear outside the community.

**Numbering correction**

IP Progress is Part 10.

Earlier references to Part 12 were corrected by the user.


**E. SHARED NOTIFICATIONS**

Use one consistent in-app notification system across the ten parts.

Notifications should support relevant events, including:

- Mentor request received.
- Mentor request accepted.
- New application received.
- Meeting invitation.
- Selection letter issued.
- Agreement submitted or verified.
- Community created.
- Task assigned.
- Work submitted for review.
- Changes requested.
- Task approved.
- Announcement posted.
- IP progress updated.

Where carried forward from the earlier recruitment requirements, department-targeted new-project notifications should reach eligible registered students in the selected departments.

This does not change dashboard visibility: all students may still browse published recruitment notices.

Notifications must:

- Be stored in the database.
- Remain after logout.
- Be available after the user returns from being offline.
- Have read/unread status.
- Support an unread count.
- Link to an authorised relevant page.
- Avoid duplicate records when an operation is retried.
- Avoid exposing confidential information to unauthorised recipients.

Do not depend on an open browser tab for storing a notification.

Polling is only a way to display newly stored records.

Do not add browser push notifications or non-authentication emails as mandatory dependencies.


**F. PERMISSIONS AND INFORMATION BOUNDARIES**

Use server-side, project-specific permission checks.

Do not rely on hiding buttons.

Important distinctions:

- College user is not the same as project member.
- Applicant is not the same as selected student.
- Selected student is not the same as NDA-complete student.
- NDA-complete student is not automatically a community member before mentor creation.
- Teacher in the college is not automatically mentor of every project.
- Original proposer is not automatically team leader.
- Team leader is not platform administrator.

Expected access:

- Unauthenticated visitor: login/sign-up only.
- Eligible user with incomplete profile: onboarding and necessary account controls.
- Completed-profile college user: shared recruitment information.
- Applicant: own application and recruitment notifications.
- Selected unsigned student: own letter and agreement workflow, without community access.
- Active community member: authorised private project content.
- Team leader: project-level summary, task, review, and announcement management.
- Mentor: project selection, agreement oversight, community creation, leader appointment, and IP updates.
- Administrator: necessary platform maintenance, without presenting admin status as automatic research-team membership.

Any support-level ability to access sensitive records should be explicit and documented, not silently exposed through ordinary application endpoints.

Validate access on:

- Pages.
- Form submissions.
- JavaScript endpoints.
- File downloads.
- Chat requests.
- Search.
- Notifications.
- History.
- Document versions.

Prevent one project member from using an identifier belonging to another project to access its records.


**G. DATA AND STATE DESIGN EXPECTATIONS**

Design a coherent relational data model.

Likely concepts include:

- User.
- Student/teacher profile.
- Department.
- Skill.
- Research interest/domain.
- OTP challenge.
- Project.
- Public recruitment record.
- Private project details.
- Mentor candidate ranking.
- Mentor request.
- Application.
- Submitted résumé version.
- Meeting invitation.
- Selection letter.
- Agreement template/version.
- Student agreement record.
- Community.
- Membership and project role.
- Sprint.
- Milestone.
- Task.
- Task submission.
- Task review.
- Comment.
- Document.
- Document version.
- Chat message.
- Announcement.
- Activity event.
- Notification.
- IP update.
- Approved achievement.

These are modelling concepts, not a demand for exactly one table per bullet.

Choose sensible relationships and avoid duplicate stores for the same fact.

Important rules:

- Account email should be unique under the chosen normalisation policy.
- Repeated submissions must not create duplicate applications.
- Repeated community creation must not create duplicates.
- A mentor rejection must not notify several next candidates because of a retry.
- Issued letters should have preserved contents.
- Agreements should reference the exact relevant version.
- Application résumés should remain unchanged historically.
- Task reviews should point to the submission being reviewed.
- File versions should be immutable stored revisions.
- Activity history should refer to actual saved actions.

Use transactions for related database changes where needed.

For file uploads, handle failures so the database does not claim that a missing file was successfully saved.

Do not delete the SQLite database during ordinary restarts, migrations, or redeployment.

Do not initialise fresh demo data on every server start.


**H. PROPOSED CODE ORGANISATION**

Keep one Django application deployment with business modules.

A reasonable organisation is:

- Core/shared configuration and UI.
- Accounts and OTP.
- Profiles and shared taxonomy.
- Projects and recruitment notices.
- Mentorship.
- Applications and selection.
- Agreements and letters.
- Communities and membership.
- Sprints and tasks.
- Documents and history.
- Chat and announcements.
- Notifications.
- IP progress and achievements.

These internal code modules support the ten product parts. They do not change the agreed product numbering.

Keep:

- Views reasonably thin.
- Business operations in clear functions/services.
- Permission checks reusable.
- Form validation explicit.
- Database migrations committed.
- Tests close to the functionality they verify.
- Shared UI components consistent.

Avoid one enormous views file or a single JavaScript file containing the entire application.

Do not overengineer the architecture for hypothetical future university-scale traffic.


**I. KNOWN UNRESOLVED DETAILS AND SUGGESTED DEFAULTS**

Record these rather than treating them as settled team decisions:

- Exact teacher verification process.
- Final department list.
- Precise matching weights and tie-breaking.
- Configurable achievement time range.
- Who approves achievements for the shared banner.
- Exact selection-letter wording and formatting.
- College-approved NDA text and letterhead.
- Accepted electronic-signing method.
- Physical-agreement verification process.
- Explicit selected-roster changes if needed.
- Student proposer’s access to detailed applicant résumés.
- Final project-completion permission.
- Exact file types and upload size limits.
- Exact optional résumé-autofill fields.
- Whether more than one sprint may be active.

Use the proposed defaults in this document for low-risk reversible behaviour where reasonable.

Do not block unrelated development while waiting for official wording or assets.

Use labelled development templates for those dependencies.


**J. FEATURES EXPLICITLY OUTSIDE THE CURRENT CORE SCOPE**

Future scope:

- Automatic handling/escalation when a teacher never responds.
- A recovery workflow when all mentor candidates reject.
- Handing a project to future student batches.
- Successor onboarding.
- Cross-batch project revival.

Not required for this initial version:

- Paid AI chatbot.
- Retrieval-augmented project assistant.
- Vector database.
- Paid résumé-parsing API.
- Automatic legal IP filing.
- Certified electronic-signature service.
- Built-in video conferencing.
- Complex calendar scheduling.
- External messaging services.
- Non-OTP email campaigns.
- Public internet access to research communities.
- Automatic authorship rankings.
- Automatic intellectual property ownership decisions.
- A separate student offer-decline workflow.
- Additional main community cards beyond the agreed five.

Document history supports traceability now; it does not mean successor handover has already been implemented.

Do not claim basic matching is AI unless an actual AI method is implemented and described accurately.


**K. TESTING AND DEMONSTRATION EXPECTATIONS**

When implementation is authorised, test connected user journeys.

Use designated demo/test accounts representing:

- Student proposer.
- Student applicant.
- Another student applicant.
- Teacher mentor.
- Teacher proposer.
- Student team leader.
- Unrelated college user.
- Selected but unsigned student.

Important verification cases:

1. A personal email is rejected in both UI and server requests.
2. Fixed demo OTP cannot authenticate arbitrary real users.
3. Real OTP expires on the server.
4. A new user cannot bypass profile completion.
5. A returning user reaches the dashboard.
6. Logout preserves all saved data.
7. A student can create a recruitment notice.
8. A teacher can create a recruitment notice.
9. Mentor suggestions use actual shared profile attributes.
10. Rejection notifies the next teacher once.
11. Acceptance attaches the mentor.
12. All students can browse published recruitment notices.
13. Filters change the displayed results correctly.
14. Applications preserve the submitted résumé.
15. Résumé extraction failure still permits manual completion.
16. A teacher can review and shortlist applicants.
17. A meeting notification reaches the intended student.
18. Only selected students receive selection letters.
19. Issuing a letter does not unlock private content.
20. An unsigned student cannot access the community.
21. A missing required agreement blocks community creation.
22. Community creation is mentor-only and does not duplicate.
23. The teacher can appoint the project team leader.
24. All five community cards open working pages.
25. Summary edits persist.
26. Chat messages persist and appear for another member.
27. Tasks can be assigned and submitted with files.
28. Submitted work awaits review.
29. Approved work updates task completion.
30. Changes requested preserve the earlier submission.
31. A revised document preserves older versions.
32. File comments remain attached to the right context.
33. History records the actor, action, and time.
34. Notifications remain after logout.
35. One project cannot access another project’s private files.
36. Teacher IP updates are visible to community members.
37. Private IP updates do not automatically appear in achievements.
38. Completion preserves project history.
39. Database and uploaded files survive a restart.
40. Important pages work on desktop and mobile.

Use a realistic connected demonstration:

- A student signs up.
- Completes their profile.
- Creates an idea.
- Requests a mentor.
- The teacher accepts.
- Another student discovers the notice and applies.
- The mentor reviews the résumé and optionally sends a meeting invitation.
- The mentor selects the student.
- A selection letter is issued.
- The required agreement is completed.
- The mentor creates the community.
- The mentor appoints a team leader.
- The team leader creates a sprint and task.
- A member uploads a PPT and submits work.
- The reviewer requests changes or approves it.
- Progress and history update.
- The team uses chat and announcements.
- The project is completed.
- The teacher posts an IP update.
- An approved achievement can be shown on the dashboard.

Never claim a test passed unless it ran successfully.

Keep real email delivery tests separate from demo authentication tests.

Do not claim a feature is implemented merely because its screen exists.


**L. WORKING WITH ME DURING IMPLEMENTATION**

I am a student and need understandable guidance.

Explain:

- What is being implemented.
- What now works.
- What was tested.
- What requires external setup.
- What remains incomplete.

Do not repeatedly ask for permission for routine coding decisions once I have asked you to implement a part.

When an external account becomes necessary, provide:

- Service name.
- Why it is needed.
- Current free-plan eligibility.
- Whether payment details are required.
- Official setup link.
- Clear steps.
- What non-secret information you need from me.
- Where secrets should be entered privately.
- How we will verify the setup.

Do not ask me to create every possible account at the beginning.

Do not purchase anything or enable paid upgrades.

Do not assume changing the model or giving one giant implementation prompt will remove the need for incremental testing.

When implementation begins:

- Inspect existing files first.
- Preserve user work.
- Identify whether older Next.js/Supabase code exists.
- Explain any mismatch with the agreed Django stack before making destructive changes.
- Build one coherent module or workflow at a time.
- Test its database behaviour and permissions.
- Verify the important interface.
- Update status documentation.
- Continue according to the implementation request.

Maintain documentation covering:

- Final requirements.
- Architecture.
- Module-to-requirement mapping.
- Permissions.
- State transitions.
- Technical assumptions.
- Completed work.
- In-progress work.
- Tests actually run.
- External integrations still unverified.
- Future scope.
- Local setup.
- Deployment.
- Database and file backup.
- Known hosting limitations.

Keep confidential files, real database files, OTP secrets, SMTP credentials, and signed agreements out of source control.

When building is authorised, this should become a working application, not only documentation.


**M. WHAT TO DO AFTER READING THIS INITIAL CONTEXT PROMPT**

This message gives you the full context.

For this first response:

1. Confirm that you understand the project as ten connected product parts.
2. Summarise the complete journey accurately.
3. Confirm the Django, HTML/CSS/JavaScript, and SQLite starting stack.
4. Explicitly preserve these important corrections:
   - Part 5 remains applicant review, shortlisting, and optional meeting.
   - Part 6 is selection/offer letters.
   - Part 7 is the confidentiality agreement.
   - There is no separate offer accept/decline step.
   - An unsigned student has no private community access.
   - The mentor manually creates the community after all intended student members have completed the required agreement.
   - Community membership is automatically added after that mentor action.
   - The teacher appoints the team leader.
   - The community has five primary pages.
   - Task submissions require review before approved completion.
   - Task files support comments and preserved versions.
   - History updates automatically from saved work.
   - IP Progress is Part 10.
   - Successor handover is future scope.
5. If a workspace is available, save this specification as a project requirements document without discarding details.
6. Record unresolved decisions separately from confirmed requirements.
7. Do not create application code, deploy, or start external account setup yet.

Wait for my next instruction about detailed planning or the first implementation part.