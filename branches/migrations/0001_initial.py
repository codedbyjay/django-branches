# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('repositories', models.ManyToManyField(to='branches.Repository', through='branches.Project', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='repository',
            field=models.ForeignKey(related_name='projects', to='branches.Repository'),
        ),
        migrations.AddField(
            model_name='project',
            name='server',
            field=models.ForeignKey(related_name='projects', to='branches.Server'),
        ),
    ]
