from django.conf import settings
from apps.profiles.taxonomy import DEPARTMENT_NAMES
from django.core.management.base import BaseCommand, CommandError
from apps.profiles.models import Department, Skill, ResearchInterest

class Command(BaseCommand):
    help = 'Explicitly seed labelled demo taxonomy; creates no accounts.'
    def handle(self, *args, **options):
        if not settings.DEBUG or settings.AUTHENTICATION_MODE != 'demo':
            raise CommandError('Only run this in local demo mode.')
        for name in DEPARTMENT_NAMES:
            Department.objects.get_or_create(name=name, defaults={'is_demo': False})
        for name in ['Python','JavaScript','Data analysis','Electronics','CAD','Research writing','Design','Statistics']:
            Skill.objects.get_or_create(name=name)
        for name in ['Artificial intelligence','Sustainability','Robotics','Healthcare technology','Education','Materials','Human-computer interaction']:
            ResearchInterest.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Taxonomy ready using the department list supplied by the project owner.'))
