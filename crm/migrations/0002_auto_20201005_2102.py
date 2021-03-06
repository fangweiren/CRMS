# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2020-10-05 13:02
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='campuses',
            options={'verbose_name': '校区', 'verbose_name_plural': '校区'},
        ),
        migrations.AlterModelOptions(
            name='classlist',
            options={'verbose_name': '已报课程', 'verbose_name_plural': '已报课程'},
        ),
        migrations.AlterModelOptions(
            name='customer',
            options={'verbose_name': '客户', 'verbose_name_plural': '客户'},
        ),
        migrations.AddField(
            model_name='enrollment',
            name='contract_agreed',
            field=models.BooleanField(default=False, verbose_name='我已认真阅读完培训协议并同意全部协议内容'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='class_list',
            field=models.ManyToManyField(blank=True, null=True, to='crm.ClassList', verbose_name='已报班级'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)', '请输入正确的邮箱')], verbose_name='email address'),
        ),
    ]
