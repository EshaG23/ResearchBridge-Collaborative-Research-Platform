from django.db import migrations


def add_departments(apps, schema_editor):
    Department = apps.get_model('profiles', 'Department')
    for name in ['CSE', 'AIML', 'AIDS', 'BCA', 'MCA', 'EE', 'ECS', 'MECH', 'CIVIL', 'ROBOTICS']:
        Department.objects.using(schema_editor.connection.alias).get_or_create(name=name, defaults={'is_demo': False})


class Migration(migrations.Migration):
    dependencies = [('profiles', '0001_initial')]
    operations = [migrations.RunPython(add_departments, migrations.RunPython.noop)]
