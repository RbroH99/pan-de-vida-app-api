# Generated by Django 4.2.11 on 2024-05-01 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_munincipality_municipality'),
    ]

    operations = [
        migrations.CreateModel(
            name='Denomination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
            ],
        ),
    ]
