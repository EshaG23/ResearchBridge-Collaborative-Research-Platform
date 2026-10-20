# Publishing the source on GitHub

Use this repository folder, not its parent workspace:

```cmd
cd /d "C:\Users\Disha\Documents\Codex\2026-09-11\hi\outputs\researchbridge"
```

If Git reports **dubious ownership**, trust only this specific repository:

```cmd
git config --global --add safe.directory C:/Users/Disha/Documents/Codex/2026-09-11/hi/outputs/researchbridge
```

This exception is needed only when Git reports that error. Do not use a wildcard safe-directory exception.

## Review before staging

```cmd
git status --short
git ls-files -ci --exclude-standard
```

The second command should print nothing: it detects tracked files that now match ignore rules. `.gitignore` does not remove files already committed and does not clean historical commits.

Keep source, migrations, templates, static assets, dependency requirements, scripts, placeholder configuration and fictional demo rosters. Exclude private data, database files, uploaded signatures/resumes/chat media, secrets, environment files, archives, backups and local virtual environments.

Real university roster data must not replace the public fictional files under `demo_rosters/`. The demonstration password and OTP in the source are intentionally public and only for local demos. Never put real credentials in documentation or source.

## Stage and inspect

```cmd
git add .
git diff --cached --stat
git diff --cached --name-only
git diff --cached --check
```

Review the staged file list before committing. If any private material appears, stop and remove it from staging before continuing. Uploading files manually through the GitHub website does not apply the local `.gitignore`.

## Commit and push

Create an empty GitHub repository first. Replace the uppercase placeholders below with your GitHub account and repository name:

```cmd
git commit -m "Prepare ResearchBridge source for GitHub"
git branch -M main
git remote -v
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Only run `git remote add origin` if no `origin` remote exists. If one exists, inspect its destination before pushing instead of replacing it blindly. A non-empty remote may require reconciling its commits; do not force-push to bypass that.

No database reset is required to publish source. Local ignored data stays on your laptop. A fresh checkout creates its own local database and demo accounts using the README commands.

This checklist concerns source publication. It is not a production deployment audit or an automated guarantee that no unknown secret can exist.
