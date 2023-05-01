from django.conf import settings
from django.db import migrations


def create_system_user(apps, schema_editor):
    user_model = apps.get_model(settings.AUTH_USER_MODEL)
    user_model.objects.create(
        username='system',
        email='cms@summitsalon.com',
        is_active=True,
        is_superuser=True,
        is_staff=True,
        password='Change Me!',
        first_name='System',
        last_name='Automation',
    )


def remove_system_user(apps, schema_editor):
    user_model = apps.get_model(settings.AUTH_USER_MODEL)
    try:
        user_model.objects.get(username='system').delete()
    except user_model.DoesNotExists:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20201120_1403'),
    ]

    operations = [
        migrations.RunPython(
            create_system_user, remove_system_user
        ),
    ]
