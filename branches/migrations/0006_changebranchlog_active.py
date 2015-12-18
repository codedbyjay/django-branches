# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0005_server_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='changebranchlog',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
