# Generated by Django 4.2.11 on 2024-05-05 18:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_church_inscript'),
    ]

    operations = [
        migrations.AlterField(
            model_name='church',
            name='inscript',
            field=models.DateField(default=datetime.datetime(2024, 5, 5, 18, 29, 31, 884133, tzinfo=datetime.timezone.utc)),
        ),
    ]
