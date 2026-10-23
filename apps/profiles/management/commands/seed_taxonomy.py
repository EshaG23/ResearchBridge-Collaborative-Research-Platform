"""Create supported profile choices without creating or completing any account."""
from django.core.management.base import BaseCommand
from apps.profiles.taxonomy import DEPARTMENT_NAMES
from apps.profiles.models import Department, Skill, ResearchInterest


class Command(BaseCommand):
    help = 'Create standard departments, skills and interests; safe to repeat.'

    def handle(self, *args, **options):
        for name in DEPARTMENT_NAMES:
            Department.objects.get_or_create(name=name)
        for name in ['Python', 'JavaScript', 'Data analysis', 'Electronics', 'CAD', 'Research writing', 'Design', 'Statistics']:
            Skill.objects.get_or_create(name=name)
        for name in ['Artificial intelligence', 'Sustainability', 'Robotics', 'Healthcare technology', 'Education', 'Materials', 'Human-computer interaction']:
            ResearchInterest.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('Profile choices ready; no accounts or profiles changed.'))
