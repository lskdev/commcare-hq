# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from __future__ import absolute_import
from django.conf import settings
from django.db import migrations

from corehq.sql_db.operations import RawSQLMigration, HqRunSQL

migrator = RawSQLMigration(('corehq', 'sql_proxy_accessors', 'sql_templates'), {
    'PL_PROXY_CLUSTER_NAME': settings.PL_PROXY_CLUSTER_NAME
})


class Migration(migrations.Migration):

    dependencies = [
        ('sql_proxy_accessors', '0027_add_undelete_functions'),
    ]

    operations = [
        HqRunSQL(
            "DROP FUNCTION IF EXISTS get_case_ids_in_domain(TEXT, TEXT, TEXT[], BOOLEAN)",
            "SELECT 1"
        ),
        migrator.get_migration('get_case_ids_in_domain_2.sql'),
        HqRunSQL(
            "DROP FUNCTION IF EXISTS get_deleted_case_ids_by_owner(TEXT, TEXT)",
            "SELECT 1"
        )
    ]
