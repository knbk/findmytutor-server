# Generated by Django 2.0 on 2018-03-28 21:09

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20180328_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, null=True, srid=4326),
        ),
    ]
