# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0012_auto_20151225_0407'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='changebranchlog',
            name='task_id',
        ),
        migrations.AddField(
            model_name='changebranchrequest',
            name='task_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
