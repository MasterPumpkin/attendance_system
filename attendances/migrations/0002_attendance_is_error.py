# Generated by Django 5.1.3 on 2024-12-07 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='is_error',
            field=models.BooleanField(default=False),
        ),
    ]