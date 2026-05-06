from django.db import migrations


VALID_STATUSES = {
    'submitted',
    'reviewed',
    'shortlisted',
    'rejected',
    'withdrawn',
}


def backfill_status(apps, schema_editor):
    Application = apps.get_model('applications', 'Application')
    for application in Application.objects.all().only('id', 'status'):
        if application.status not in VALID_STATUSES:
            application.status = 'submitted'
            application.save(update_fields=['status'])


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_application_status'),
    ]

    operations = [
        migrations.RunPython(backfill_status, migrations.RunPython.noop),
    ]
