from uuid import uuid4
from django.db import migrations

def generate_tokens(apps, schema_editor):
    CompleteUser = apps.get_model('main', 'CompleteUser')
    for user in CompleteUser.objects.all():
        user.email_confirmation_token = uuid4()
        user.save(update_fields=['email_confirmation_token'])

class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_completeuser_email_confirmation_token_and_more'),
    ]
    operations = [
        migrations.RunPython(generate_tokens),
    ]
