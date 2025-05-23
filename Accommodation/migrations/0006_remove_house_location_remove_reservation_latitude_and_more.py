# Generated by Django 5.1.7 on 2025-04-11 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Accommodation", "0005_house_rating_reservation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="house",
            name="location",
        ),
        migrations.RemoveField(
            model_name="reservation",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="reservation",
            name="longitude",
        ),
        migrations.AddField(
            model_name="house",
            name="latitude",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="house",
            name="longitude",
            field=models.FloatField(default=0.0),
        ),
    ]
