# Generated by Django 5.1.7 on 2025-04-27 17:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accommodation', '0017_house_unique_house_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='flat_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='house',
            name='floor_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='house',
            name='geo_address',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='house',
            name='room_number',
            field=models.CharField(blank=True, default=0, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='specialist',
            name='university',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='specialists', to='Accommodation.university'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='university',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='Accommodation.university'),
            preserve_default=False,
        ),
    ]
