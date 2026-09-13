from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from apps.core.backup import backup
class Command(BaseCommand):
    help='Back up the stopped workspace database, uploads and development secret with integrity checks.'
    def add_arguments(self,parser):
        parser.add_argument('destination');parser.add_argument('--writers-stopped',action='store_true')
    def handle(self,*args,**options):
        if not options['writers_stopped']:raise CommandError('Stop all web servers and other writers, then pass --writers-stopped.')
        try:count=backup(settings.DATA_DIR,options['destination'])
        except (ValueError,OSError) as exc:raise CommandError(str(exc))
        self.stdout.write(self.style.SUCCESS(f'Backup verified: {count} files. Keep it private.'))
