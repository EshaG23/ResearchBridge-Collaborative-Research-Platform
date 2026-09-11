# Architecture and implementation mapping

## Foundation

One Django deployment, server-rendered HTML, custom CSS, small JavaScript interactions, SQLite, and private persistent file storage. Django 5.2.17 LTS is pinned with its installed dependencies; it supports Python 3.13. Official reference: https://docs.djangoproject.com/en/5.2/releases/5.2/

`config/settings/base.py` holds shared configuration. `local.py` provides development settings and an ignored, persistent development secret. `production.py` requires an explicit secret, host allowlist, and persistent data directory; WSGI/ASGI default to production. `manage.py` defaults to local development. Production settings are a starting configuration, not a deployment claim.

`apps/accounts` owns a custom email-based user model established before initial migrations. Email is trimmed and lowercased, validated for exact college domain on normal writes, and uniquely constrained case-insensitively in the database. No automatic verification or teacher privileges are assigned. Bulk writes bypass application validation and must not be used for future account creation. Future OTP verification services must create accounts only after a successful challenge.

Views should validate forms, call business services, and render results. Future cross-record operations must use transactions and reusable project permission checks. Notifications and activity events must be recorded alongside saved business actions. Polling will display persisted notifications/chat; it is not their storage mechanism.

## Module mapping

| Coding module | Scope | Main Django apps | Product part |
|---|---|---|---|
| 1 | Foundation, configuration, documentation | core, accounts, config | Cross-cutting |
| 2 | Shared UI and navigation | core, templates, static | Cross-cutting |
| 3 | College OTP and sessions | accounts | 1 |
| 4 | Onboarding, profiles, shared taxonomy | profiles | 2 |
| 5 | Project permissions and private file foundation | core, documents | Cross-cutting |
| 6 | Persistent notifications | notifications | Cross-cutting |
| 7 | Ideas and separate recruitment/private records | projects | 3 |
| 8 | Mentor ranking and sequential requests | mentorship | 3 |
| 9 | Dashboard, discovery, filtering | projects | 4 |
| 10 | Applications and submitted résumé snapshots | recruitment, documents | 4 |
| 11 | Review, shortlist, optional meeting | recruitment | 5 |
| 12 | Immutable selection letters | recruitment, documents | 6 |
| 13 | Agreement evidence, versions, verification | agreements | 7 |
| 14 | Mentor-created community and leader appointment | communities | 8 |
| 15 | Summary and sprints | communities, tasks, documents | 8 |
| 16 | Chat and announcements | collaboration | 8 |
| 17 | Tasks, submissions, reviews, approved progress | tasks, documents | 8 |
| 18 | History, file comments/versions, contribution views | documents, core | 9 |
| 19 | Completion, IP updates, approved achievements | ip_progress, projects | 10 and 3 |
| 20 | Connected tests, polish, real email, deployment | All | All |

Only core/accounts have behaviour in Module 1. Other app packages are organisational scaffolding, not completed features.

## Dependencies and data ownership

Profiles and projects share controlled department, skill, and interest records. Applications reference immutable submitted résumé versions. Letters preserve issued content. Agreements reference their exact template/evidence. Community creation checks the intended roster and all required agreements transactionally. Membership and teacher approval are distinct from platform administration.

Tasks belong to projects/sprints; reviews reference specific submissions and file versions. Logical documents own immutable file revisions. Activity events reference actual saved work and retain actor context. Add activity recording from Module 7 onward; do not defer recording until the Module 18 history UI. File-version groundwork begins in Module 5.

No paid AI dependency, external chat service, React, Redis, Celery, or separate database server is introduced. PostgreSQL migration remains possible through Django models/migrations.
