# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trans', '0017_translation_translating'),
    ]

    operations = [
        migrations.AddField(
            model_name='UserContest',
            name='extra_country1_count',
            field=models.PositiveIntegerField(default=0)
        ),
        migrations.AddField(
            model_name='UserContest',
            name='extra_country2_count',
            field=models.PositiveIntegerField(default=0)
        ),
        migrations.AlterField(
            model_name='User',
            name='num_of_contestants',
            field=models.PositiveIntegerField(default=0)
        ),
    ]
