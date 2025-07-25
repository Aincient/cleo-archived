# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-02 12:33
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cached_api_calls', '0002_auto_20180501_0933'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoCoding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(db_index=True, unique=True, verbose_name='Location name')),
                ('raw_response', models.TextField(blank=True, null=True, verbose_name='Raw response')),
                ('geolocation', django.contrib.gis.db.models.fields.PointField(blank=True, default='', srid=4326, verbose_name='Geo coordinates')),
                ('created', models.DateField(auto_now_add=True)),
                ('updated', models.DateField(auto_now=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.AlterField(
            model_name='translation',
            name='original',
            field=models.TextField(db_index=True, verbose_name='Original'),
        ),
    ]
