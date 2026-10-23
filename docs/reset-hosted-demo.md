# Reset the hosted demo while keeping accounts

Run these commands in a PythonAnywhere Bash console, in `~/researchbridge`, with
the hosting virtual environment activated. `deploy/manage_hosted.py` reads your
existing private hosted configuration; this command never overwrites it.

## Preview (safe while the site is running)

```bash
python deploy/manage_hosted.py reset_hosted_demo --dry-run
```

The preview prints model counts, upload file count/size and the configured database
and upload paths. It creates no backup and makes no changes. Running without a
confirmation phrase is also preview-only. Counts may change while users are active.

## Execute only when ready

First disable the web application in PythonAnywhere's Web tab and stop scheduled
tasks, consoles or other processes that write to this database or upload directory.
The flag below is your explicit acknowledgement; the command cannot independently
stop PythonAnywhere workers. Keep them stopped until the command finishes.

```bash
mkdir -p ~/researchbridge-backups
chmod 700 ~/researchbridge-backups
python deploy/manage_hosted.py reset_hosted_demo --writers-stopped --backup-dir "$HOME/researchbridge-backups/before-reset-$(date +%Y%m%d-%H%M%S)" --confirm "RESET HOSTED DEMO KEEP ACCOUNTS"
```

Use a new backup folder each time. Keep it outside the source code, DATA_DIR and
public static directories. Ensure sufficient disk space for a complete database and
upload copy. Backup or verification failure prevents any reset. Backups contain
private records, password hashes, signatures and media; never publish or commit them.

After success, re-enable/reload the web application. Existing users sign in with
their **same current email and password**, then fill their own profiles again.

## What changes

- Preserves every User row, its ID, email, roster role, password hash, active/demo
  flags, admin permissions and other account fields. It neither imports a roster
  nor creates replacement accounts. Existing disabled accounts remain disabled.
- Resets student/teacher profiles to model defaults: blank personal/research
  information, no department/year/availability, no skills/interests, incomplete
  onboarding and no teacher approval. Missing profiles are created with roster role.
- Deletes research records across projects, mentorship, recruitment, offer letters,
  agreements/signatures/reviews, communities, memberships, summaries, sprints,
  collaboration/chat/polls/history, tasks/submissions/reviews/contributions,
  documents/versions, notifications, IP progress and achievements; deletes résumés.
- Removes all contents of the configured private `DATA_DIR/uploads`, including
  orphaned files. A new empty upload directory is left ready for use.
- Preserves shared departments, skills, research interests, migration history,
  authentication settings, sessions, authentication throttles and hosted secret key.
  Existing login throttling remains in effect; the command does not bypass it.
- Uses no flush, database drop, local demo reset script or private configuration edit.

## Backup and failure recovery

Before deletion, the SQLite backup API creates a consistent database copy and all
uploads are copied. SHA-256 manifest verification and SQLite integrity checking
must pass. Only database and uploads are backed up; hosted configuration is left
untouched. Dependency ordering includes join tables and protected version/reply
chains. Database changes run in one transaction and user records are compared
before commit. New circular model dependencies cause a safe refusal.

Uploads are renamed to a unique private sibling directory during the transaction.
An ordinary failure rolls back database deletion and restores the original upload
directory. After commit, the old upload directory is removed. If that cleanup fails,
the error explicitly says the database committed and gives the remaining directory;
do not assume the reset rolled back. Keep the site stopped and inspect the backup.

A process kill or machine failure cannot be made atomic across SQLite and the
filesystem. An exclusive `.reset-hosted-demo.lock` prevents another reset from
starting after an interrupted run. Keep writers stopped, inspect the backup and
any `.reset-uploads-*` folder, and restore the verified database/uploads together
before clearing that lock. Never merge an old database with new uploads.

For a full recovery, use the existing restore command into a **new** data directory:

```bash
python deploy/manage_hosted.py restore_workspace --help
```

Follow its arguments, then deliberately point the hosted data-directory setting to
the restored directory and reload. Do not overwrite the running database. The reset
command itself never edits that setting or automatically restores a committed reset.

## Verification

`apps/core/test_hosted_reset.py` runs only against isolated test databases/uploads.
It checks five student and five teacher logins with their original passwords,
unchanged User fields, onboarding redirects, protected linked records and versions,
taxonomy/migrations, verified backup contents, repeatability, refusal/preview,
backup failures, transaction rollback and upload recovery. It does not use or test
your live passwords and never resets hosted data as part of development testing.
