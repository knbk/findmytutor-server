# Generated by Django 2.0 on 2018-03-28 21:19

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20180328_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326),
        ),
    ]