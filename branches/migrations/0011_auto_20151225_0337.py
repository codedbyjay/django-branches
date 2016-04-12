# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0010_changebranchrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changebranchrequest',
            name='change_branch_log',
            field=models.OneToOneField(null=True, blank=True, to='branches.ChangeBranchLog'),
        ),
    ]
