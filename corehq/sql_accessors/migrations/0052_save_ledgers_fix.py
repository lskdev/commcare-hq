# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-24 12:55
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations

from corehq.sql_db.operations import noop_migration


class Migration(migrations.Migration):

    dependencies = [
        ('sql_accessors', '0051_merge_20170724_1255'),
    ]

    operations = [
        noop_migration()
    ]
