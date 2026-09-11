# Module 9 — project discovery

Open Discover projects in the sidebar, or use the same filters on Dashboard. Initially every recruiting project across departments is included; the profile department never automatically restricts results. Draft, awaiting-mentor and closed records are excluded.

Search matches title, recruitment summary and available roles, never confidential text. Optional department, research-domain and required-skill filters combine with AND. Clear filters restores the default view. Sort by newest creation (default), oldest creation, most open positions, or case-insensitive title; stable ID tie-breakers avoid ambiguous ordering. Each page contains up to 12 projects and pagination preserves search/filter/sort parameters. Invalid filter values display errors and no results rather than silently broadening access.

Cards show recruitment data, required skills, departments, positions and mentor/proposer name. They link to the existing permission-checked project overview. The grid uses three desktop columns, two intermediate columns and one phone column. No confidential data, phone numbers or résumés are loaded by discovery. Login and completed-profile gates remain enforced, responses are not cached, and the listing is read-only.

Validation: 44 relevant project, mentorship and core tests passed, including 8 new discovery tests for filtering, search boundaries, ordering, pagination, empty states, invalid inputs, access and demo isolation. Browser verified two real saved recruiting projects, CSE filtering down to one, and three-column desktop layout. No new sample projects or user data changes were needed. Module 10 will connect applications; this module does not claim application submission is available.
