# Module 12 - Offer letters

Completed: mentor preparation, explicit preview/issuance, immutable selection snapshot, stored printable PDF, private recipient/current mentor access, and persistent deduplicated in-app notification linking to the application and its letter.

Only finally selected applications qualify. The mentor supplies the actual selected role. Signed previews expire after 30 minutes and bind the mentor, application and revisions. Issuance is serialized with the project lock and constrained to one letter per application. Failed database writes clean up the stored PDF. Letters cannot be edited through the model save method or portal; privileged database administrators remain capable of changing database/storage contents.

PDFs preserve the actual submitted student identity, project, mentor, role, date, unique reference, and next steps, with a SHA-256 digest. HTML views read the stored snapshot. No institutional signature, additional offer acceptance or private project access is created. Agreement signing belongs to Module 13 and community access to Module 14.

Try: mentor -> My applications -> project applicant -> Shortlist -> Finalize selection -> Prepare offer letter -> enter role -> Preview -> Issue. Student -> Notifications or My applications -> application -> View offer letter -> Download printable PDF.

Validation: 101 Django tests pass, including six new offer-letter tests covering eligibility, access/CSRF, preview/confirmation, expiration/tampering/staleness, duplicate retries, rollback cleanup, immutable contents, PDF text/hash and protected/missing downloads. Standard and long-content PDFs rendered and visually inspected. Responsive browser page inspected with synthetic data in an isolated test database. Live user data was not reseeded or reset.

Operations: migration recruitment.0003_offerletter; ReportLab 4.4.9 plus pinned dependencies. Private PDF storage follows MEDIA_ROOT. Back up database and private files together. A future demo reset must remove OfferLetter records before protected applications and remove associated files after backup.
