# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0009_auto_20151225_0235'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeBranchRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('branch', models.CharField(max_length=255)),
                ('status', models.CharField(default=b'requested', max_length=50, verbose_name=b'Status')),
                ('change_branch_log', models.ForeignKey(blank=True, to='branches.ChangeBranchLog', null=True)),
                ('project', models.ForeignKey(related_name='change_branch_requests', to='branches.Project')),
            ],
        ),
    ]
