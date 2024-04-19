# Generated by Django 4.2.11 on 2024-04-19 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_medicine_measurement_units_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicine',
            name='measurement',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
