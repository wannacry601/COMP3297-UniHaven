# Generated by Django 5.1.7 on 2025-04-27 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accommodation', '0016_university_house_cuhk_house_hkust_house_flat_number_and_more'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='house',
            constraint=models.UniqueConstraint(fields=('room_number', 'flat_number', 'floor_number', 'geo_address'), name='unique_house_address'),
        ),
    ]
