from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from apps.profiles.models import Department, Skill, ResearchInterest

class Command(BaseCommand):
    help = 'Explicitly seed labelled demo taxonomy; creates no accounts.'
    def handle(self, *args, **options):
        if not settings.DEBUG or settings.AUTHENTICATION_MODE != 'demo':
            raise CommandError('Only run this in local demo mode.')
        for name in ['Computing', 'Electronics', 'Mechanical Engineering', 'Civil Engineering', 'Management']:
            Department.objects.get_or_create(name=f'Demo — {name}', defaults={'is_demo': True})
        for name in ['Python','JavaScript','Data analysis','Electronics','CAD','Research writing','Design','Statistics']:
            Skill.objects.get_or_create(name=name)
        for name in ['Artificial intelligence','Sustainability','Robotics','Healthcare technology','Education','Materials','Human-computer interaction']:
            ResearchInterest.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Demo taxonomy ready. These are not official university department names.'))
