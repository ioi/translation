# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trans', '0011_auto_20170727_1509'),
    ]

    operations = [
        migrations.RunSQL(
            'ALTER TABLE "trans_country" DROP CONSTRAINT "trans_country_pkey" CASCADE'
        ),
        migrations.RunSQL(
            'ALTER TABLE "trans_language" DROP CONSTRAINT "trans_language_pkey" CASCADE',
        ),

        migrations.AlterField(
            model_name='country',
            name='code',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='language',
            name='code',
            field=models.CharField(max_length=255, primary_key=True, serialize=False),
        ),

        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='Language', to_field='code'),
        ),
        migrations.AlterField(
            model_name='user',
            name='country',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='Country', to_field='code'),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
