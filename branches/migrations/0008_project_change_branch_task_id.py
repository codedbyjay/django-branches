# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0007_auto_20151222_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='change_branch_task_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
