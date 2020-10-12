# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-10-12 05:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0002_auto_20201012_1247'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, unique=True, verbose_name='菜单名称')),
                ('icon', models.CharField(blank=True, max_length=24, null=True)),
            ],
            options={
                'verbose_name_plural': '菜单',
                'verbose_name': '菜单',
            },
        ),
        migrations.RenameField(
            model_name='permissions',
            old_name='is_menu',
            new_name='show',
        ),
        migrations.RemoveField(
            model_name='permissions',
            name='icon',
        ),
        migrations.AddField(
            model_name='permissions',
            name='menu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Menu', verbose_name='所属菜单'),
        ),
    ]