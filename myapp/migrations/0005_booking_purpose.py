# Generated by Django 5.1 on 2024-10-03 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_auditorium_timeslot_booking_workingday_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='purpose',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
