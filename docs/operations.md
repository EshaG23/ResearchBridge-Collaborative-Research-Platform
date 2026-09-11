# Operations and persistence

## Local data

The local settings create `private/` and `private/uploads/` if absent. Migrations create/update `private/db.sqlite3`; startup does not reset it or seed demo records. The ignored development secret persists across restarts. Uploaded content has no public URL mapping.

Never put the database, signed agreements, real files, SMTP credentials, OTP secrets, or `.development-secret` into source control. Production secret values should be entered through the host environment, not pasted into chat or tracked files.

## Backup and restore procedure

For the small SQLite demonstration, stop the web server and other writers before copying data. Back up the entire `private/` directory (or the configured persistent data directory) to a separate protected location. This keeps the SQLite database and uploaded files from the same stopped state. Keep source and migrations in Git separately. Back up production secrets through the host's private configuration process.

To restore, stop the server, preserve the current data directory as a recovery copy, restore the matching database and uploads into the configured location, install the pinned requirements and apply migrations for that source version, then verify record counts and representative authorised file downloads. Do not replace an active database. A complete database/file backup-and-restore demonstration remains a Module 20 check; uploads are not implemented in Module 1.

## Production preparation (not yet deployed)

Use `config.settings.production`. Configure `DJANGO_SECRET_KEY` (strong random value, at least 50 characters), `DJANGO_ALLOWED_HOSTS` (comma-separated exact hosts), and `RESEARCHBRIDGE_DATA_DIR` (existing writable persistent directory). Collect static assets with `manage.py collectstatic --noinput` using the selected settings. Never route the private upload directory as static/media content.

Production defaults require HTTPS and secure cookies. Determine trusted proxy settings from the host's documentation before deployment; incorrect proxy configuration may cause redirect loops. Run `check --deploy` against the actual production environment before launch.

PythonAnywhere Free is only the proposed initial host. Storage, outgoing network/email limits, renewal requirements, and persistent-file behaviour must be checked at deployment time. No free hosting capability or email delivery has been verified yet. Keep local execution available regardless.

Real OTP setup belongs to Module 3/20 as appropriate. The current dummy email backend sends no messages and no code is claimed to have been sent. Never enable a console backend for real OTP logging.
