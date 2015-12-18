# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0004_auto_20150823_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='username',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
