# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0008_project_change_branch_task_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='change_branch_task_id',
        ),
        migrations.AddField(
            model_name='changebranchlog',
            name='task_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
