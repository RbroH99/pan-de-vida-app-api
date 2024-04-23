# Generated by Django 4.2.11 on 2024-04-23 21:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_phonenumber_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonenumber',
            name='contact',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.contact'),
            preserve_default=False,
        ),
    ]