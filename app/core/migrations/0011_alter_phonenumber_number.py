# Generated by Django 4.2.11 on 2024-04-23 22:08

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_phonenumber_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonenumber',
            name='number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=16, region=None, unique=True),
        ),
    ]
