# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import jsonfield.fields
import enumfields.fields
import shoop.core.fields
import shoop_boleto.constants


class Migration(migrations.Migration):

    dependencies = [
        ('shoop', '0030_purchaseorder'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoletoPaymentProcessor',
            fields=[
                ('paymentprocessor_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shoop.PaymentProcessor', serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name': 'Boleto bancário',
                'verbose_name_plural': 'Boletos bancários',
            },
            bases=('shoop.paymentprocessor',),
        ),
        migrations.CreateModel(
            name='BoletoSequenceNumber',
            fields=[
                ('bank_service', enumfields.fields.EnumField(max_length=10, primary_key=True, verbose_name='Serviço', serialize=False, enum=shoop_boleto.constants.BankService)),
                ('last_number', models.BigIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)])),
            ],
            options={
                'verbose_name': 'Número sequencial de boleto',
                'verbose_name_plural': 'Números sequenciais de boleto',
            },
        ),
        migrations.CreateModel(
            name='CecredBoletoBehaviorComponent',
            fields=[
                ('servicebehaviorcomponent_ptr', models.OneToOneField(parent_link=True, primary_key=True, to='shoop.ServiceBehaviorComponent', serialize=False, auto_created=True)),
                ('num_sequencial', models.BigIntegerField(default=1, verbose_name='Número sequencial do próximo boleto', help_text='Este número será utilizado caso ele seja maior do que o último armazenado. Se ele for menor, este será desconsiderado. CUIDADO: apenas informe este campo se você sabe o que está fazendo. O objetivo é ajustar o número sequencial inicial caso boletos já tenham sido emitidos anteriormente através de outro software.')),
                ('local_pagamento', models.TextField(max_length=60, verbose_name='Local de pagamento')),
                ('cedente', models.TextField(verbose_name='Nome do cedente', max_length=60, help_text='É o emissor do título')),
                ('prazo_vencimento', models.PositiveSmallIntegerField(default=5, verbose_name='Prazo para o vencimento do boleto', help_text='Quantidade de dias que será adicionado a data do pedido para atribuir como vencimento do boleto.')),
                ('instrucoes', models.TextField(verbose_name='Instruções', null=True, max_length=60, help_text='Máximo de 8 linhas com 50 caracteres cada.', blank=True)),
                ('especie_doc', enumfields.fields.EnumIntegerField(default=0, verbose_name='Espécie do documento', enum=shoop_boleto.constants.DocumentType)),
                ('layout', models.CharField(max_length=5, verbose_name='Layout', choices=[('v06', 'Layout versão 6 - Fev/16')])),
                ('agencia', models.CharField(verbose_name='Número da agência', max_length=6, help_text='Apenas números com o dígito verificador, ex: 01010')),
                ('conta', models.CharField(verbose_name='Número da conta', max_length=15, help_text='Apenas números com o dígito verificador, ex: 1234568')),
                ('convenio', models.CharField(max_length=6, verbose_name='Número do convênio')),
                ('carteira', models.CharField(max_length=2, verbose_name='Número da carteira')),
            ],
            options={
                'abstract': False,
            },
            bases=('shoop.servicebehaviorcomponent', models.Model),
        ),
        migrations.CreateModel(
            name='StoredBoleto',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('status', enumfields.fields.EnumIntegerField(default=0, blank=True, verbose_name='Situação', enum=shoop_boleto.constants.BoletoStatus)),
                ('bank_service', enumfields.fields.EnumField(max_length=10, verbose_name='Serviço', enum=shoop_boleto.constants.BankService)),
                ('due_date', models.DateField(verbose_name='Data do vencimento')),
                ('number_line', models.CharField(null=True, max_length=50, verbose_name='Linha digitável')),
                ('bar_code', models.CharField(null=True, max_length=50, verbose_name='Código de barras')),
                ('nosso_numero', models.CharField(null=True, max_length=50, verbose_name='Nosso número')),
                ('info', jsonfield.fields.JSONField(null=True, verbose_name='Informações do boleto')),
                ('total_value', shoop.core.fields.MoneyValueField(default=0, editable=False, verbose_name='Valor do Boleto', max_digits=36, decimal_places=9)),
                ('payment_date', models.DateTimeField(null=True, verbose_name='Data do pagamento', blank=True)),
                ('payment_amount_value', shoop.core.fields.MoneyValueField(default=0, editable=False, verbose_name='Valor pago', max_digits=36, decimal_places=9)),
                ('order', models.OneToOneField(to='shoop.Order', verbose_name='Pedido', related_name='boleto')),
            ],
            options={
                'verbose_name': 'Boleto bancário',
                'verbose_name_plural': 'Boletos bancários',
            },
        ),
    ]
