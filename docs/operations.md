# Operations and persistence

Local demo data lives in private/demo: SQLite database, private uploads and persistent development secret. Startup never resets data. Keep private data, secrets and backups out of source control and public static hosting.

## Running from CMD

From the project folder, run:

```bat
start-demo.cmd
```

For a fresh machine with Python installed, first run setup-demo.cmd to create the environment, install dependencies and migrate. Roster import is explicit; see demo_rosters/README.md. The .env.example file is a configuration reference; it is not automatically loaded.

## Backup and restore

Stop all web servers and writers first. Use the Python interpreter from the project's virtual environment (or the existing ../../work/.venv on this laptop):

```bat
python manage.py backup_workspace private/backups/my-backup --writers-stopped
python manage.py restore_workspace private/backups/my-backup private/restored-workspace
```

Choose new directory names. Backup verifies SQLite integrity and file SHA256 checksums; restore refuses to overwrite existing directories and verifies checksums. Keep copies outside the laptop too. To activate a restore, stop the server, archive the current private/demo directory, and move the restored directory to private/demo. Preserve source and migrations in Git separately. Never replace an active database.

The pre-reset demo backup is private/release-backups/before-reset-20260913-final. Its 11 files were restored and verified in a separate folder. The previous demo directory is also retained as private/demo-before-reset-20260913-final.

## Production preparation: not deployed

Use config.settings.production, a strong DJANGO_SECRET_KEY, exact DJANGO_ALLOWED_HOSTS, RESEARCHBRIDGE_AUTH_MODE=real and a persistent RESEARCHBRIDGE_DATA_DIR. Configure SMTP through environment variables listed in .env.example. Never publish private uploads or log real OTPs. Configure HTTPS, serve collected static assets, use a production WSGI/ASGI server, and run check --deploy against the actual environment. /health/ performs a database connectivity check without exposing configuration.

Real SMTP credentials and a hosting destination have not been supplied. Actual delivery, HTTPS hosting and recovery on that host remain to be verified before public launch. Demo OTP 123456 is only for local demo mode.


## Repeatable local reset

Stop all server processes first. From the project folder run `reset-demo.cmd`. It refuses a listener on port 8000, validates paths, archives private/demo as private/demo-backup-TIMESTAMP, migrates a fresh database, seeds taxonomy and imports 5 students plus 5 teachers. Servers on custom ports must also be stopped manually. Then run `start-demo.cmd`. This archive operation does not produce a checksum manifest; use backup_workspace for a separately verified backup. An isolated repeated-reset test confirmed account counts, incomplete profiles, zero projects and retention of prior files.
