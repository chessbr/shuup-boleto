# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shuup_boleto', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storedboleto',
            name='bar_code',
            field=models.CharField(max_length=44, null=True, verbose_name='C\xf3digo de barras'),
        ),
        migrations.AlterField(
            model_name='storedboleto',
            name='number_line',
            field=models.CharField(help_text='Linha digit\xe1vel formatada (54 caracteres)', max_length=54, null=True, verbose_name='Linha digit\xe1vel'),
        ),
    ]
