"""Explicit, offline reset of research content, never of account credentials."""
import json
import shutil
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.core.backup import digest, verify
from apps.profiles.models import Profile, ResumeVersion

CONTENT_APPS = {'projects', 'mentorship', 'recruitment', 'agreements',
                'communities', 'collaboration', 'tasks', 'documents',
                'notifications', 'ip_progress'}
CONFIRMATION = 'RESET HOSTED DEMO KEEP ACCOUNTS'


def deletion_order():
    """Child-first order, including automatic M2M tables; fail on new cycles."""
    targets = {m for m in apps.get_models(include_auto_created=True)
               if m._meta.app_label in CONTENT_APPS}
    targets.add(ResumeVersion)
    remaining = set(targets)
    result = []
    while remaining:
        parents = {f.remote_field.model for m in remaining for f in m._meta.fields
                   if f.is_relation and f.remote_field.model != m
                   and f.remote_field.model in remaining}
        leaves = sorted(remaining - parents, key=lambda m: m._meta.label)
        if not leaves:
            raise CommandError('New circular dependencies require review; nothing reset.')
        result.extend(leaves)
        remaining.difference_update(leaves)
    return result


def checked_uploads():
    data = Path(settings.DATA_DIR).resolve()
    raw = Path(settings.MEDIA_ROOT).absolute()
    if raw.is_symlink() or raw.resolve() != data / 'uploads':
        raise CommandError('Requires a real DATA_DIR/uploads directory, without links.')
    for parent in [raw, *raw.parents]:
        if parent.is_symlink():
            raise CommandError('Linked upload paths are not supported.')
    if raw.exists():
        if not raw.is_dir():
            raise CommandError('Upload root is not a directory.')
        for item in raw.rglob('*'):
            if item.is_symlink() or not item.resolve().is_relative_to(raw.resolve()):
                raise CommandError('Linked or escaping upload files are not supported.')
            if not item.is_file() and not item.is_dir():
                raise CommandError('Special upload files are not supported.')
    return raw.resolve()


def make_backup(destination, uploads):
    destination.mkdir(mode=0o700, parents=False)
    connection.ensure_connection()
    with closing(sqlite3.connect(destination / 'db.sqlite3')) as target:
        connection.connection.backup(target)
    if uploads.exists():
        shutil.copytree(uploads, destination / 'uploads')
    else:
        (destination / 'uploads').mkdir()
    files = {p.relative_to(destination).as_posix(): digest(p)
             for p in destination.rglob('*') if p.is_file()}
    (destination / 'manifest.json').write_text(
        json.dumps({'format': 1, 'files': files}, indent=2), encoding='utf-8')
    verify(destination)


def reset_database(order):
    # Nullable self-links otherwise block bulk deletion (replies/version chains).
    for model in order:
        for field in model._meta.fields:
            if field.is_relation and field.remote_field.model == model:
                if not field.null:
                    raise CommandError('Non-null self-reference requires manual review.')
                model.objects.update(**{field.name: None})
        model.objects.all().delete()
    for user in User.objects.filter(roster_role__in=['student', 'teacher']):
        profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': user.roster_role})
        blank = Profile(user=user, role=user.roster_role)
        values = {f.attname: getattr(blank, f.attname) for f in Profile._meta.concrete_fields
                  if f.name not in {'id', 'user', 'updated_at'}}
        values['updated_at'] = timezone.now()
        Profile.objects.filter(pk=profile.pk).update(**values)
        profile.skills.clear()
        profile.interests.clear()


class Command(BaseCommand):
    help = 'Preview or explicitly reset hosted research data; preserve all users and passwords.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--confirm', help='Exact phrase: ' + CONFIRMATION)
        parser.add_argument('--writers-stopped', action='store_true')
        parser.add_argument('--backup-dir', help='New private directory outside DATA_DIR and source code.')

    def handle(self, *args, **options):
        if connection.vendor != 'sqlite' or connection.in_atomic_block:
            raise CommandError('Requires SQLite and no surrounding transaction.')
        order = deletion_order()
        uploads = checked_uploads()
        self.stdout.write('Database: ' + str(connection.settings_dict['NAME']))
        self.stdout.write('Uploads: ' + str(uploads))
        self.stdout.write(f'KEEP all {User.objects.count()} users, passwords, roles, taxonomy, migrations and configuration.')
        self.stdout.write('RESET student/teacher profiles to blank, unapproved, incomplete onboarding.')
        for model in order:
            self.stdout.write(f'DELETE {model._meta.label}: {model.objects.count()}')
        files = [p for p in uploads.rglob('*') if p.is_file()] if uploads.exists() else []
        self.stdout.write(f'DELETE private uploads (including orphans): {len(files)} files, {sum(p.stat().st_size for p in files)} bytes.')
        if options['dry_run'] or not options['confirm']:
            self.stdout.write('PREVIEW ONLY. No data or files changed. Use --confirm with the exact phrase to execute.')
            return
        if options['confirm'] != CONFIRMATION:
            raise CommandError('Confirmation phrase does not match; nothing reset.')
        if not options['writers_stopped'] or not options['backup_dir']:
            raise CommandError('Stop web traffic, scheduled tasks and all other writers; require --writers-stopped and --backup-dir.')
        destination = Path(options['backup_dir']).expanduser().absolute()
        if destination != destination.resolve() or destination.exists():
            raise CommandError('Backup must be a new directory without linked parent paths.')
        if any(destination.is_relative_to(Path(p).resolve()) for p in [settings.DATA_DIR, settings.BASE_DIR]):
            raise CommandError('Backup must be outside DATA_DIR and project source/static directories.')
        if not destination.parent.is_dir():
            raise CommandError('Create the private backup parent directory first.')
        # Exclusive file also prevents two cooperating reset commands from running together.
        lock = uploads.parent / '.reset-hosted-demo.lock'
        try:
            lock_file = lock.open('x')
        except FileExistsError:
            raise CommandError('Reset lock exists. Inspect previous reset/backup before removing it.') from None
        quarantine = uploads.parent / ('.reset-uploads-' + uuid.uuid4().hex)
        moved = False
        committed = False
        recovery_failed = False
        try:
            lock_file.close()
            make_backup(destination, uploads)
            self.stdout.write('Verified private database/upload backup: ' + str(destination))
            original_users = list(User.objects.order_by('pk').values())
            with transaction.atomic():
                reset_database(order)
                if list(User.objects.order_by('pk').values()) != original_users:
                    raise CommandError('Account preservation check failed; rolling back.')
                connection.check_constraints()
                if uploads.exists():
                    uploads.rename(quarantine)
                    moved = True
                uploads.mkdir(mode=0o700)
            committed = True
            if moved:
                # This exact validated, random sibling contains only the old uploads.
                shutil.rmtree(quarantine)
            self.stdout.write(self.style.SUCCESS('Reset complete. All account records/password hashes preserved. Users must complete their profiles again.'))
        except Exception as exc:
            if not committed and moved:
                try:
                    if uploads.exists():
                        uploads.rmdir()  # Refuse to remove unexpected new files.
                    quarantine.rename(uploads)
                except OSError as recovery_error:
                    recovery_failed = True
                    raise CommandError(f'Database rolled back but uploads need recovery from {quarantine}; backup: {destination}. Reset lock retained. {recovery_error}') from recovery_error
            if committed:
                raise CommandError(f'Database reset committed, but upload cleanup needs attention at {quarantine}. Backup: {destination}. {exc}') from exc
            raise CommandError(f'Reset failed; database transaction rolled back. Backup (if completed): {destination}. {exc}') from exc
        finally:
            if not recovery_failed:
                lock.unlink()
