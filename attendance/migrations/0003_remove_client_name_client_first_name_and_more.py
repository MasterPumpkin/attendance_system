# Generated by Django 5.1.3 on 2024-12-03 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_attendance_is_closed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='name',
        ),
        migrations.AddField(
            model_name='client',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]