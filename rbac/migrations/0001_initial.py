# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-10-11 06:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Permissions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='标题')),
                ('url', models.CharField(max_length=32)),
                ('is_menu', models.BooleanField(default=False)),
                ('icon', models.CharField(blank=True, max_length=24, null=True)),
            ],
            options={
                'verbose_name_plural': '权限',
                'verbose_name': '权限',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32)),
                ('permissions', models.ManyToManyField(blank=True, null=True, to='rbac.Permissions')),
                ('user', models.ManyToManyField(related_name='roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '角色',
                'verbose_name': '角色',
            },
        ),
    ]
