# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from datetime import timedelta
import logging

from enumfields.fields import EnumField, EnumIntegerField
from jsonfield import JSONField

from shuup_boleto.constants import BankService, BoletoStatus, DocumentType

from shuup.core.fields import MoneyValueField
from shuup.core.models import PaymentProcessor, ServiceChoice
from shuup.core.models._service_base import ServiceBehaviorComponent
from shuup.utils.analog import LogEntryKind
from shuup.utils.properties import MoneyProperty

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import F
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class BoletoBehaviorComponentMixin(models.Model):
    bank_service = None

    num_sequencial = models.BigIntegerField(verbose_name=_('Número sequencial do próximo boleto'),
                                            help_text=_('Este número será utilizado caso ele seja maior do que o último armazenado. '
                                                        'Se ele for menor, este será desconsiderado. CUIDADO: apenas informe este campo '
                                                        'se você sabe o que está fazendo. O objetivo é ajustar o número sequencial '
                                                        'inicial caso boletos já tenham sido emitidos anteriormente através de outro software.'),
                                            default=1)

    local_pagamento = models.TextField(verbose_name=_('Local de pagamento'),
                                       max_length=60)

    cedente = models.TextField(verbose_name=_('Nome do cedente'),
                               max_length=60,
                               help_text=_('É o emissor do título'))

    prazo_vencimento = models.PositiveSmallIntegerField(verbose_name=_('Prazo para o vencimento do boleto'),
                                                        default=5,
                                                        help_text=_('Quantidade de dias que será adicionado a '
                                                                    'data do pedido para atribuir como vencimento do boleto.'))

    instrucoes = models.TextField(verbose_name=_('Instruções'),
                                  max_length=60, blank=True, null=True,
                                  help_text=_('Máximo de 8 linhas com 50 caracteres cada.'))

    especie_doc = EnumIntegerField(DocumentType,
                                   verbose_name=_('Espécie do documento'),
                                   default=DocumentType.DM)

    class Meta:
        abstract = True

    def get_context_data(self, service, order):
        boleto_data = {
            "valor_documento": order.taxful_total_price.value,
            "data_documento": order.created_on.date(),
            "numero_documento": order.pk,
            "especie": "R$",
            "sacado": str(order.billing_address),
            "aceite": 'N',
            "local_pagamento": self.local_pagamento,
            "especie_doc": self.especie_doc,
            "vencimento": order.created_on.date() + timedelta(days=self.prazo_vencimento),
            "cedente": self.cedente,
            "instrucoes": self.instrucoes.split("\n") if self.instrucoes else []
        }

        # Adiciona endereço melhor formatado
        # e informações complementares no sacado
        # quando Shuup BR estiver instalado
        if "shuup_br" in settings.INSTALLED_APPS:

            try:
                from shuup_br.models import PersonType
                person_id = ''

                if order.creator.person_type == PersonType.FISICA:
                    person_id = order.creator.pf_person.cpf
                elif order.creator.person_type == PersonType.JURIDICA:
                    person_id = order.creator.pj_person.cnpj

                sacado = order.billing_address.name

                if person_id:
                    sacado = "{0} - {1}".format(sacado, person_id)

                sacado_extra = []

                has_extra = hasattr(order.billing_address, 'extra')
                sacado_extra = [
                    "{0}, {1} - {2} - {3} - {4}".format(
                        order.billing_address.street,
                        order.billing_address.extra.numero if has_extra else '',
                        order.billing_address.street2,
                        order.billing_address.street3,
                        order.billing_address.postal_code
                    ),
                    "{0} - {1} - {2}".format(
                        order.billing_address.city,
                        order.billing_address.region,
                        order.billing_address.country
                    )
                ]

                boleto_data["sacado"] = sacado
                boleto_data["sacado_extra"] = sacado_extra
            except:
                pass

        return boleto_data

    def generate_boleto(self, service, order):
        if not self.bank_service:
            raise AttributeError("bank_service must be set to a valid value")

        boleto_data = self.get_context_data(service, order)

        with transaction.atomic():
            stored_boleto = StoredBoleto.objects.create(order=order,
                                                        due_date=boleto_data['vencimento'],
                                                        bank_service=self.bank_service,
                                                        total_value=order.taxful_total_price.value)

            return stored_boleto

    def next_sequence(self):
        with transaction.atomic():
            # Gera o numero sequencial do boleto
            # de acordo com o servico
            seq, created = BoletoSequenceNumber.objects.get_or_create(bank_service=self.bank_service,
                                                                      defaults={'last_number': self.num_sequencial or 1})
            if not created:
                seq.last_number = F('last_number') + 1
                seq.save(update_fields=['last_number'])
                seq.refresh_from_db()

            return seq.last_number


class CecredBoletoBehaviorComponent(ServiceBehaviorComponent, BoletoBehaviorComponentMixin):
    bank_service = BankService.CECRED

    CECRED_LAYOUT_CHOICES = (
        ('v06', _('Layout versão 6 - Fev/16')),
    )

    name = _("Boleto: Configuração 085-CECRED")
    help_text = _("Configurações do boleto do banco CECRED")

    layout = models.CharField(_("Layout"),
                              max_length=5,
                              choices=CECRED_LAYOUT_CHOICES)

    agencia = models.CharField(verbose_name=_('Número da agência'),
                               max_length=6,
                               help_text=_('Apenas números com o dígito verificador, ex: 01010'))

    conta = models.CharField(verbose_name=_('Número da conta'),
                             max_length=15,
                             help_text=_('Apenas números com o dígito verificador, ex: 1234568'))

    convenio = models.CharField(verbose_name=_('Número do convênio'), max_length=6)
    carteira = models.CharField(verbose_name=_('Número da carteira'), max_length=2)

    def get_context_data(self, service, order):
        boleto_data = super(CecredBoletoBehaviorComponent, self).get_context_data(service, order)

        boleto_data.update({
            "convenio": self.convenio,
            "carteira": self.carteira,
            "agencia": "".join([str(d) for d in self.agencia if d.isdigit()]),
            "conta_corrente": "".join([str(d) for d in self.conta if d.isdigit()]),
        })

        return boleto_data

    def generate_boleto(self, service, order):
        with transaction.atomic():
            stored_boleto = super(CecredBoletoBehaviorComponent, self).generate_boleto(service, order)

            from python_boleto.cecred import CecredBoleto
            boleto_data = self.get_context_data(service, order)
            boleto_data['num_sequencial'] = self.next_sequence()

            boleto_cecred = CecredBoleto(**boleto_data)

            # gera e salva a linha digitavel e o codigo de barras
            stored_boleto.number_line = boleto_cecred.linha_digitavel
            stored_boleto.bar_code = boleto_cecred.codigo_barras
            stored_boleto.nosso_numero = boleto_cecred.nosso_numero
            stored_boleto.info = boleto_cecred.__dict__
            stored_boleto.full_clean()
            stored_boleto.save(update_fields=['nosso_numero', 'number_line', 'bar_code', 'info'])

            try:
                boleto_cecred.validate()
            except Exception as exc:
                order.add_log_entry((_("O boleto gerado não é válido: {0}")).format(str(exc)), kind=LogEntryKind.ERROR)

            return stored_boleto


class BoletoPaymentProcessor(PaymentProcessor):
    '''
    Processador de pagamento Boleto
    '''

    class Meta:
        verbose_name = _('Boleto bancário')
        verbose_name_plural = _('Boletos bancários')

    def get_service_choices(self):
        return [
            ServiceChoice(BankService.CECRED.value, BankService.CECRED),
        ]

    def create_service(self, choice_identifier, **kwargs):
        service = super(BoletoPaymentProcessor, self).create_service(choice_identifier, **kwargs)

        behavior_class = BOLETO_BANK_BEHAVIORCOMPONENT_MAP.get(choice_identifier)
        if behavior_class:
            service.behavior_components.add(behavior_class.objects.create())
            service.save()

        return service

    def get_effective_name(self, service, source):
        return _("Boleto bancário")

    def process_payment_return_request(self, service, order, request):
        pass

    def get_payment_process_response(self, service, order, urls):
        behavior_class = BOLETO_BANK_BEHAVIORCOMPONENT_MAP.get(service.choice_identifier)

        try:

            with transaction.atomic():
                behavior_component = service.behavior_components.instance_of(behavior_class)[0]
                stored_boleto = behavior_component.generate_boleto(service, order)

                # salva nos dados adicionais o ID do boleto original (primeiro) gerado
                order.payment_data["boleto_id"] = stored_boleto.pk
                order.save()

                order.add_log_entry(_("Boleto gerado por %s") % behavior_component, kind=LogEntryKind.NOTE)

        except Exception as exc:
            logger.exception((_("Falha ao gerar boleto através da classe {0}: {1}").format(behavior_class, str(exc))))
            order.add_log_entry((_("Falha ao gerar boleto através da classe {0}: {1}").format(behavior_class, str(exc))), kind=LogEntryKind.ERROR)

        return HttpResponseRedirect(urls.return_url)


class StoredBoleto(models.Model):
    order = models.OneToOneField('shuup.Order',
                                 related_name='boleto',
                                 on_delete=models.CASCADE,
                                 verbose_name=_('Pedido'))
    status = EnumIntegerField(BoletoStatus,
                              verbose_name=_('Situação'),
                              default=BoletoStatus.Created,
                              blank=True)
    bank_service = EnumField(BankService, verbose_name=_('Serviço'))
    due_date = models.DateField(verbose_name=_('Data do vencimento'))
    number_line = models.CharField(verbose_name=_('Linha digitável'),
                                   max_length=54,
                                   null=True,
                                   help_text=_("Linha digitável formatada (54 caracteres)"))
    bar_code = models.CharField(verbose_name=_('Código de barras'), max_length=44, null=True)
    nosso_numero = models.CharField(verbose_name=_('Nosso número'), max_length=50, null=True)
    info = JSONField(verbose_name=_('Informações do boleto'), null=True)

    total = MoneyProperty('total_value', 'order.currency')
    total_value = MoneyValueField(editable=False, verbose_name=_('Valor do Boleto'), default=0)

    payment_date = models.DateTimeField(_('Data do pagamento'), null=True, blank=True)
    payment_amount = MoneyProperty('payment_amount_value', 'order.currency')
    payment_amount_value = MoneyValueField(editable=False, verbose_name=_('Valor pago'), default=0)

    class Meta:
        verbose_name = _('Boleto bancário')
        verbose_name_plural = _('Boletos bancários')

    @property
    def html(self):
        """ Retrieves the rendered HTML for the StoredBoleto """

        html = ''

        # se for CECRED..
        if self.bank_service == BankService.CECRED:
            from python_boleto.cecred import CecredBoleto
            boleto = CecredBoleto(**self.info)
            boleto.validate()
            html = boleto.export_html()

        return html


class BoletoSequenceNumber(models.Model):
    bank_service = EnumField(BankService, primary_key=True, verbose_name=_('Serviço'))
    last_number = models.BigIntegerField(default=0, validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _('Número sequencial de boleto')
        verbose_name_plural = _('Números sequenciais de boleto')


# Mapa indicando qual classe de behavior para um banco
BOLETO_BANK_BEHAVIORCOMPONENT_MAP = {
    BankService.CECRED.value: CecredBoletoBehaviorComponent,
}
