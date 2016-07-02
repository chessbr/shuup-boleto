# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import shuup.core.fields
import enumfields.fields
import jsonfield.fields
import shuup_boleto.constants


class Migration(migrations.Migration):

    dependencies = [
        ('shuup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoletoPaymentProcessor',
            fields=[
                ('paymentprocessor_ptr', models.OneToOneField(to='shuup.PaymentProcessor', serialize=False, auto_created=True, primary_key=True, parent_link=True)),
            ],
            options={
                'verbose_name': 'Boleto bancário',
                'verbose_name_plural': 'Boletos bancários',
            },
            bases=('shuup.paymentprocessor',),
        ),
        migrations.CreateModel(
            name='BoletoSequenceNumber',
            fields=[
                ('bank_service', enumfields.fields.EnumField(serialize=False, primary_key=True, enum=shuup_boleto.constants.BankService, verbose_name='Serviço', max_length=10)),
                ('last_number', models.BigIntegerField(validators=[django.core.validators.MinValueValidator(1)], default=0)),
            ],
            options={
                'verbose_name': 'Número sequencial de boleto',
                'verbose_name_plural': 'Números sequenciais de boleto',
            },
        ),
        migrations.CreateModel(
            name='CecredBoletoBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(to='shuup.ServiceBehaviorComponent', serialize=False, auto_created=True, primary_key=True, parent_link=True)),
                ('num_sequencial', models.BigIntegerField(verbose_name='Número sequencial do próximo boleto', help_text='Este número será utilizado caso ele seja maior do que o último armazenado. Se ele for menor, este será desconsiderado. CUIDADO: apenas informe este campo se você sabe o que está fazendo. O objetivo é ajustar o número sequencial inicial caso boletos já tenham sido emitidos anteriormente através de outro software.', default=1)),
                ('local_pagamento', models.TextField(verbose_name='Local de pagamento', max_length=60)),
                ('cedente', models.TextField(verbose_name='Nome do cedente', help_text='É o emissor do título', max_length=60)),
                ('prazo_vencimento', models.PositiveSmallIntegerField(verbose_name='Prazo para o vencimento do boleto', help_text='Quantidade de dias que será adicionado a data do pedido para atribuir como vencimento do boleto.', default=5)),
                ('instrucoes', models.TextField(null=True, verbose_name='Instruções', blank=True, help_text='Máximo de 8 linhas com 50 caracteres cada.', max_length=60)),
                ('especie_doc', enumfields.fields.EnumIntegerField(enum=shuup_boleto.constants.DocumentType, verbose_name='Espécie do documento', default=0)),
                ('layout', models.CharField(verbose_name='Layout', choices=[('v06', 'Layout versão 6 - Fev/16')], max_length=5)),
                ('agencia', models.CharField(verbose_name='Número da agência', help_text='Apenas números com o dígito verificador, ex: 01010', max_length=6)),
                ('conta', models.CharField(verbose_name='Número da conta', help_text='Apenas números com o dígito verificador, ex: 1234568', max_length=15)),
                ('convenio', models.CharField(verbose_name='Número do convênio', max_length=6)),
                ('carteira', models.CharField(verbose_name='Número da carteira', max_length=2)),
            ],
            options={
                'abstract': False,
            },
            bases=('shuup.servicebehaviorcomponent', models.Model),
        ),
        migrations.CreateModel(
            name='StoredBoleto',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('status', enumfields.fields.EnumIntegerField(enum=shuup_boleto.constants.BoletoStatus, verbose_name='Situação', blank=True, default=0)),
                ('bank_service', enumfields.fields.EnumField(enum=shuup_boleto.constants.BankService, verbose_name='Serviço', max_length=10)),
                ('due_date', models.DateField(verbose_name='Data do vencimento')),
                ('number_line', models.CharField(null=True, verbose_name='Linha digitável', max_length=50)),
                ('bar_code', models.CharField(null=True, verbose_name='Código de barras', max_length=50)),
                ('nosso_numero', models.CharField(null=True, verbose_name='Nosso número', max_length=50)),
                ('info', jsonfield.fields.JSONField(null=True, verbose_name='Informações do boleto')),
                ('total_value', shuup.core.fields.MoneyValueField(verbose_name='Valor do Boleto', decimal_places=9, max_digits=36, editable=False, default=0)),
                ('payment_date', models.DateTimeField(null=True, verbose_name='Data do pagamento', blank=True)),
                ('payment_amount_value', shuup.core.fields.MoneyValueField(verbose_name='Valor pago', decimal_places=9, max_digits=36, editable=False, default=0)),
                ('order', models.OneToOneField(related_name='boleto', verbose_name='Pedido', to='shuup.Order')),
            ],
            options={
                'verbose_name': 'Boleto bancário',
                'verbose_name_plural': 'Boletos bancários',
            },
        ),
    ]
