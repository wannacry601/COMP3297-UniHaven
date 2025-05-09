# Generated by Django 5.1.7 on 2025-04-27 15:41

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accommodation', '0015_remove_notification_model'),
        ('authtoken', '0004_alter_tokenproxy_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='house',
            name='CUHK',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='house',
            name='HKUST',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='house',
            name='flat_number',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='house',
            name='floor_number',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='house',
            name='geo_address',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='house',
            name='room_number',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.CreateModel(
            name='HouseUniversity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Accommodation.house')),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Accommodation.university')),
            ],
            options={
                'unique_together': {('house', 'university')},
            },
        ),
        migrations.AddField(
            model_name='house',
            name='universities',
            field=models.ManyToManyField(related_name='houses', through='Accommodation.HouseUniversity', to='Accommodation.university'),
        ),
        migrations.AddField(
            model_name='specialist',
            name='university',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specialists', to='Accommodation.university'),
        ),
        migrations.AddField(
            model_name='student',
            name='university',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='Accommodation.university'),
        ),
        migrations.CreateModel(
            name='UniversityToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='authtoken.token')),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Accommodation.university')),
            ],
        ),
    ]
