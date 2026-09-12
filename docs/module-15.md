# Module 15 - Editable summary and sprints

The Summary card now opens a working editable research overview. Mentor/current eligible team leader can edit detailed description, problem statement, objectives, existing solutions, research gap and a progress narrative. The initial description comes from the confidential proposal; after first save the community summary is a separate editable research record, preserving the original proposal. Other members can read; outsiders and members with unverified agreements cannot.

Custom sections support add/edit/order. Lower order values appear first with stable record-ID ordering for ties. Each change preserves actor, timestamp, before/after content and confirmation key in immutable community history. The summary shows the latest 40 edit events; older events remain stored for the later history module. Community revision checks prevent stale overwrites; the project lock and confirmation key enforce retry safety.

The research library supports presentation, literature-paper and reference categories, HTTPS links, and private PDF/PPTX uploads up to 5 MB. PPTX validation checks bounded ZIP/XML contents and rejects macros and embedded programs; legacy PPT is not accepted. Downloads require current community membership/eligibility, use no-store responses, and never expose public media URLs. File contents, metadata and SHA-256 remain preserved; upload a revised resource instead of editing existing evidence. Failed transactions remove saved files.

The To-do card now opens sprint planning: a variable number of ordered sprints with title, goal, optional planned start/end dates, status and narrative updates. Dates are validated and at most one sprint can be Active, enforced in both database and transactional service. Complete or return the active sprint to Planned before starting another. Statuses can be revised with history. Summary and community home show current/next sprint and completed/total sprint counts. Progress is explicitly sprint-status progress, not task progress. No task totals are fabricated or manually duplicated.

Module boundaries: editable summary and sprint planning are complete. Chat/announcements remain Module 16; individual tasks/reviews and task-derived totals remain Module 17; IP tracking remains Module 19. The five main cards continue to lead to their protected section pages.

Validation includes role/access checks, leader revocation, default summary reads without writes, form POSTs and CSRF, custom-section ordering, stale writes/retries/history, date validation/single-active constraint, real sprint progress, private downloads, HTTPS/file-source validation, PPTX validation and failed-save cleanup. Summary and sprint board visually reviewed using isolated QA records, with no live project seeding.

Operations: migration communities.0002_projectsummary_summarysection_sprint_summaryresource. Back up database and private files together. A future full demo reset must remove summary resources, custom sections, sprint records and summary records before their protected community, along with existing community events/memberships. Task relationships introduced later must be respected before removing sprints.

Final validation: all 126 Django regression tests passed. System checks and migration consistency checks passed.
