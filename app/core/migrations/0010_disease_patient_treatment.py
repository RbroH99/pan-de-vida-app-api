# Generated by Django 4.2.11 on 2024-05-06 19:13

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_church_inscript'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(editable=False, max_length=12, unique=True)),
                ('ci', models.CharField(max_length=11, unique=True)),
                ('inscript', models.DateField(default=django.utils.timezone.now)),
                ('church', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.church')),
                ('contact', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.contact')),
            ],
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disease', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.disease')),
                ('medicine', models.ManyToManyField(blank=True, null=True, to='core.medicine')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.patient')),
            ],
        ),
    ]
