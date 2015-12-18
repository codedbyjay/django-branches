# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0003_server_intialized'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeBranchLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('current_branch', models.CharField(max_length=255)),
                ('previous_branch', models.CharField(max_length=255, null=True, blank=True)),
                ('change_branch_script', models.TextField(null=True, blank=True)),
                ('log_filename', models.FileField(null=True, upload_to=b'', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='change_branch_script',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='changebranchlog',
            name='project',
            field=models.ForeignKey(related_name='change_branch_logs', to='branches.Project'),
        ),
    ]
