# Generated by Django 4.2 on 2025-05-15 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restapi_core', '0010_auto_20250515_1849'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='contributors',
        ),
    ]
