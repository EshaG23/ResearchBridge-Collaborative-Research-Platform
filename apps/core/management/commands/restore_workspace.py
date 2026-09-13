from django.core.management.base import BaseCommand,CommandError
from apps.core.backup import restore
class Command(BaseCommand):
    help='Verify a backup and restore into a NEW directory without replacing existing data.'
    def add_arguments(self,parser):parser.add_argument('source');parser.add_argument('destination')
    def handle(self,*args,**options):
        try:count=restore(options['source'],options['destination'])
        except (ValueError,OSError) as exc:raise CommandError(str(exc))
        self.stdout.write(self.style.SUCCESS(f'Restored and verified {count} files. Point the stopped application to this directory before starting.'))
