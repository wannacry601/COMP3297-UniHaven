# Generated by Django 5.2 on 2025-04-15 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("Accommodation", "0012_rating_created_at_rating_student_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Notification",
        ),
    ]
