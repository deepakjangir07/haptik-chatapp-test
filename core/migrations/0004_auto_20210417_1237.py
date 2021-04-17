# Generated by Django 3.0.7 on 2021-04-17 12:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0003_connection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='connection',
            name='user',
        ),
        migrations.AddField(
            model_name='connection',
            name='user',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
