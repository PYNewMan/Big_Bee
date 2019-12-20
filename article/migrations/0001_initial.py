# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-13 13:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='文章题目')),
                ('author', models.CharField(max_length=20, verbose_name='作者')),
                ('content', models.TextField(default='', verbose_name='文章内容')),
            ],
            options={
                'db_table': 'Article',
            },
        ),
    ]
