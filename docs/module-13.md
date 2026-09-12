# Module 13 - Confidentiality agreements

Implemented the selected-student agreement workflow, linked from offer letters, applications and project pages. Selected applicants require an issued offer letter. The mentor may explicitly include a student proposer in the intended team; the action records who enrolled them and why. Teachers have no additional NDA obligation.

## Signing

Students read the full versioned agreement and choose drawn (mouse, touch or stylus), typed-full-name, or physical signature upload. Electronic signatures require name matching, explicit consent and current-password confirmation before an exact agreement/signature preview and final confirmation. The account password is never stored in the evidence. Password checks are rate-limited. Signed preview tokens expire after 15 minutes, bind the account authentication hash, student, project/revision, current template digest and previous evidence version. A password change invalidates an outstanding token. The demo password-reset OTP is not used as signing authentication.

Physical agreements can be downloaded for printing. PDF/PNG/JPEG signed copies are validated (5 MB maximum; bounded image dimensions); images are retained as PDF pages. Students confirm their password and consent before submission. Physical uploads and electronic signatures are both pending until the current approved mentor verifies them. For physical copies the mentor must inspect every page, identity, project, signature and date. The server requires an explicit inspection acknowledgement in the review form.

## Records and access

Each submission preserves exact template/version/text, student/project identity, name, method, consent, signature strokes where applicable, server timestamp, evidence PDF, physical copy if present and SHA-256 fingerprints. PDF signature strokes retain the capture pad aspect ratio. Verification events preserve actor, time and notes. Models reject ordinary edits to existing evidence/history; the portal exposes no edit/delete endpoints. Privileged database/storage administrators remain outside this application-level immutability boundary.

Recipient and current authorised mentor only can retrieve evidence. File responses are private/no-store and sandboxed. The mentor checks stored file fingerprints before approval. Corrections append review history, make the agreement incomplete, and allow a new immutable submission. Old files and reviews remain available. Transactions, project locks and unique request keys prevent duplicate submissions/notifications; failed saves clean up files.

## Community readiness

The mentor checklist includes every selected applicant plus explicitly enrolled student proposers. Missing, pending or correction-requested evidence blocks agreement_gate(project). No unsigned student is silently removed. Empty rosters are not ready. Signing/verification creates no community or private membership. Module 14 must recheck this gate while holding the project lock before mentor-controlled community creation; later roster changes need an explicit recorded policy and must preserve the gate.

## Institutional configuration

The default sample-nda-1 is visibly labelled development wording, not college-approved. This is electronic completion evidence, not a certificate-backed DSC/eSign service. Licensed-provider integration and college approval are external prerequisites for that claim; no fake certificates, official signatures or approvals are generated. Reference: https://cca.gov.in/eSign.html

The template schema lives in apps/agreements/templates.py. A deployment may set AGREEMENT_TEMPLATE_PATH to a server-controlled JSON document with version, title, identity, sample, notice, clauses and consent. A revised template needs a new version; issued snapshots never reread that file. The PDF branding function is replaceable when authorised institutional assets and required wording are supplied. Sample approval is a demo workflow fact, not institutional/legal certification.

## Validation and operations

Full regression: 112 tests passed before final polish. Final focused suite: 11 agreement tests passed, including electronic preview/confirm, physical HTTP submission, mandatory mentor acknowledgement, retries, expired/tampered/stale tokens, wrong password, signature validation, private access, revoked mentor, corrected version history, unsigned roster blocking, proposer enrollment, invalid files and failed-save cleanup. Browser draw/clear and physical-method controls verified; latest PDF terms and signature pages visually inspected. QA uses isolated test data and temporary private storage, leaving live student records untouched.

Migration: agreements.0001_initial. Back up the database and private uploads together. Future demo reset order: AgreementReview, AgreementEvidence, Agreement, then protected projects/users. Preserve backups and remove corresponding files deliberately.
