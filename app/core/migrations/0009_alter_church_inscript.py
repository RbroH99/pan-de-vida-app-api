# Generated by Django 4.2.11 on 2024-05-05 18:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_church_inscript'),
    ]

    operations = [
        migrations.AlterField(
            model_name='church',
            name='inscript',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]