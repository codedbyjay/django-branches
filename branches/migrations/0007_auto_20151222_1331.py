# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0006_changebranchlog_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='server',
            old_name='intialized',
            new_name='initialized',
        ),
    ]
