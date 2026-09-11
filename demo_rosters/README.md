# Demo university rosters

These JSON data files are fictional university-record stand-ins, not actual university data. They are imported into SQLite; login never reads readable passwords from a file at runtime.

| Role | Email | Initial password |
|---|---|---|
| Student | demo.student@rbunagpur.in | ResearchDemo!2026 |
| Student | demo.applicant@rbunagpur.in | ResearchDemo!2026 |
| Student | student.one@rknec.in | ResearchDemo!2026 |
| Faculty | demo.teacher@rbunagpur.in | ResearchDemo!2026 |
| Faculty | faculty.one@rknec.in | ResearchDemo!2026 |

The shared password above is for these fictional local demo accounts only. Both domains are allowed for both roles; the roster assigns the role. Existing profile details and résumé files are preserved on import.

From the project folder:

```powershell
..\..\work\.venv\Scripts\python.exe manage.py migrate
..\..\work\.venv\Scripts\python.exe manage.py seed_demo_taxonomy
..\..\work\.venv\Scripts\python.exe manage.py import_roster demo_rosters/students.json --demo
..\..\work\.venv\Scripts\python.exe manage.py import_roster demo_rosters/faculty.json --demo
```

The importer validates the whole file and rolls back on a conflict. It rejects invalid domains, missing data, duplicate emails and conflicting existing roles. It creates hashed initial passwords and never resets an existing usable password during re-import. Removing a row does not delete the existing account; an administrator must explicitly deactivate it.

To add demo accounts, add entries to the appropriate file and re-run its import command. Do not put real university records or real initial passwords in this tracked directory. Real rosters belong in protected storage and require real mode, with no `--demo` flag.

Forgot Password uses 123456 only in the isolated local demo, only for existing registered accounts. Real delivery uses a random code and still requires SMTP setup. Password changes update the database hash, not these initial-credential files. If a password has been changed, use the new password or Forgot Password.
