# Generated by Django 4.2.11 on 2024-05-03 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_church'),
    ]

    operations = [
        migrations.AlterField(
            model_name='church',
            name='denomination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.denomination'),
        ),
    ]