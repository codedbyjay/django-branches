# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('branches', '0002_server_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='intialized',
            field=models.BooleanField(default=False),
        ),
    ]
