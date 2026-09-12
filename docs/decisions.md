# Confirmed scope, assumptions, and pending decisions

## Confirmed

The full original specification is preserved without alteration in `requirements-original.md`. There are ten connected product parts and twenty coding stages. No requirement is removed to fit the user's approximately 15–20-hour availability; this is a planning target, not a guaranteed completion time. Report actual progress and limitations rather than silently simplifying scope.

Django, templates, CSS, JavaScript, SQLite, persistent private storage, in-app notifications and chat, no required payments. Professional blue/near-black/white UI. No public-internet community. Successor handover, mentor nonresponse escalation, and all-rejected recovery remain future scope.

## Reversible implementation defaults

- Django 5.2 LTS and Python 3.13; dependencies pinned for reproducible installation.
- Lowercase entire account email and trim surrounding whitespace.
- Custom user model now, before dependent tables exist; role-specific profiles arrive in Module 4.
- Local data under ignored `private/`, configurable through `RESEARCHBRIDGE_DATA_DIR`; no public media route.
- Separate local/production settings. No OTP mode enabled until implemented.
- Later demo teachers explicitly provisioned/admin-approved; no faculty verification inferred from email ownership.
- Later deterministic mentor scoring and one active request at a time; explain scoring and keep remaining candidates ranked after the chosen first recipient.
- Proposed one active sprint, mentor reviews leader tasks, mentor confirms project completion.
- Label sample agreements and temporary department fixtures; never claim institutional approval.

## Unresolved institutional/product details

1. Exact teacher verification process and final department list.
2. Mentor matching defaults now implemented: 50 domain, 20 department, up to 30 skill coverage; ties by name then user ID. These remain configurable implementation choices.
3. Achievement time range and approval authority.
4. Selection-letter wording and format.
5. College-authorised NDA wording and letterhead.
6. Approved electronic-signing method and physical-copy verification process.
7. Explicit selected-roster change policy.
8. Module 11 default: student proposers receive an overview only; private applications, résumés and meetings remain applicant/current-approved-mentor only.
9. Final project-completion authority.
10. File types/size limits and optional résumé-autofill fields.
11. Whether multiple sprints may be active.

These remain decisions to settle when relevant. Do not turn uploaded NDA files into automatic verification. Do not block independent development waiting for authorised wording or assets.

## External setup not started

Real Gmail SMTP eligibility/delivery, PythonAnywhere free-plan suitability, and approved college assets are unverified. No account setup, purchase, or deployment has been performed. Verify current official instructions and actual service limits when those integrations are needed.
