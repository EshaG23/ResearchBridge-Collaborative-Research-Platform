import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.accounts.models import User
from apps.accounts.validators import normalise_college_email
from apps.profiles.models import Profile, Department

class Command(BaseCommand):
    help='Import a student/faculty JSON roster. Existing passwords and profiles are preserved.'
    def add_arguments(self,parser):
        parser.add_argument('file')
        parser.add_argument('--demo',action='store_true')
    def handle(self,*args,**options):
        demo=options['demo']
        if demo and (not settings.DEBUG or settings.AUTHENTICATION_MODE!='demo'):
            raise CommandError('Demo rosters are allowed only in local demo mode.')
        if not demo and settings.AUTHENTICATION_MODE!='real':
            raise CommandError('Real rosters require real authentication mode and separate real storage.')
        try:
            document=json.loads(Path(options['file']).read_text(encoding='utf-8'))
            role=document['role']; rows=document['accounts']
            if role not in {'student','teacher'} or not isinstance(rows,list):
                raise ValueError
            seen=set()
            with transaction.atomic():
                for row in rows:
                    email=normalise_college_email(row['email'])
                    if email in seen or not row['name'].strip() or not row.get('initial_password'):
                        raise ValueError('Duplicate email or missing required values')
                    seen.add(email)
                    user=User.objects.filter(email=email).first()
                    if user and (user.is_demo!=demo or (user.roster_role and user.roster_role!=role)):
                        raise ValueError('Existing account mode or role conflicts with roster')
                    if not user:
                        user=User.objects.create_user(email,row['initial_password'],is_demo=demo,roster_role=role)
                    else:
                        if not user.has_usable_password():
                            user.set_password(row['initial_password'])
                        user.roster_role=role; user.save()
                    department=Department.objects.get(name=row['department'])
                    profile,created=Profile.objects.get_or_create(user=user,defaults={'role':role,'name':row['name'],'department':department})
                    if profile.role and profile.role!=role:
                        raise ValueError('Existing profile role conflicts with roster')
                    profile.role=role
                    if not profile.name: profile.name=row['name']
                    if not profile.department_id: profile.department=department
                    profile.teacher_approved=(role=='teacher')
                    profile.save()
        except (OSError,ValueError,KeyError,TypeError,ValidationError,Department.DoesNotExist) as error:
            raise CommandError('Roster import failed; check schema, domains, departments, duplicate entries, and role conflicts.') from error
        self.stdout.write(self.style.SUCCESS(f'Imported {len(rows)} {role} accounts; existing passwords and profile details retained.'))
