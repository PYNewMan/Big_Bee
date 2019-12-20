# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-12 13:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Akcar2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('car_id', models.CharField(max_length=20, unique=True, verbose_name='爱卡车辆ID')),
                ('brand', models.CharField(max_length=200, verbose_name='牌子')),
                ('car_params', models.TextField(default='', verbose_name='车辆信息')),
                ('pic_url', models.TextField(default='', verbose_name='车图url')),
                ('score_kb', models.TextField(default='', verbose_name='爱卡用户评分')),
                ('series', models.CharField(max_length=200, verbose_name='车型系列')),
            ],
            options={
                'db_table': 'Akcar2',
            },
        ),
    ]
