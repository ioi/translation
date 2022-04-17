# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trans', '0018_extra_country_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='User',
            name='online',
            field=models.BooleanField(default=False)
        ),
    ]
