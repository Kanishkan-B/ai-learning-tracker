from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tracker', '0003_jobapplication'),
    ]

    operations = [
        migrations.AddField(
            model_name='learninglog',
            name='file_url',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='learninglog',
            name='file_base64',
        ),
    ]

