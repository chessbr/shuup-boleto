# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from decimal import Decimal

import shoop_boleto
from shoop_boleto.constants import BoletoStatus
from shoop_boleto.models import StoredBoleto

from django.http.response import HttpResponse
from django.utils.timezone import now
from django.views.generic.base import TemplateView, View

TRANSACTION_DETAIL_TEMPLAE = 'boleto/admin/order_section_transaction_detail.jinja'


class DashboardView(TemplateView):
    template_name = "boleto/admin/dashboard.jinja"
    title = "Boleto"

    def get_context_data(self, **kwargs):
        context_data = super(DashboardView, self).get_context_data(**kwargs)
        context_data.update({'VERSION': shoop_boleto.__version__})
        return context_data


class PayBoletoView(View):

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        boleto = StoredBoleto.objects.get(order__pk=pk)
        boleto.payment_date = now()
        boleto.payment_amount = boleto.total
        boleto.status = BoletoStatus.Paid
        boleto.save(update_fields=['payment_date', 'payment_amount_value', 'status'])
        return HttpResponse()


class ResetBoletoView(View):

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        boleto = StoredBoleto.objects.get(order__pk=pk)
        boleto.payment_date = None
        boleto.payment_amount_value = Decimal()
        boleto.status = BoletoStatus.Created
        boleto.save(update_fields=['payment_date', 'payment_amount_value', 'status'])
        return HttpResponse()


class CancelBoletoView(View):

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        boleto = StoredBoleto.objects.get(order__pk=pk)
        boleto.status = BoletoStatus.Expired
        boleto.save(update_fields=['status'])
        return HttpResponse()
