# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import parler.models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackingItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(default=b'ESSENTIAL', max_length=1024, choices=[(b'ESSENTIAL', b'Essential'), (b'STATISTICS', b'Statistics'), (b'MARKETING', b'Marketing')])),
                ('ordering', models.IntegerField(default=0, verbose_name='Ordering')),
                ('site', models.ManyToManyField(to='sites.Site', blank=True)),
            ],
            options={
                'ordering': ('ordering',),
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TrackingItemTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('name', models.CharField(max_length=1024, verbose_name='Name')),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='django_privacy_mgmt.TrackingItem', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'managed': True,
                'db_table': 'django_privacy_mgmt_trackingitem_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'tracking item Translation',
            },
        ),
        migrations.AlterUniqueTogether(
            name='trackingitemtranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
