# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from shoop_boleto.models import BoletoPaymentProcessor

from shoop.admin.base import OrderSection


class BoletoOrderSection(OrderSection):
    identifier = 'boleto'
    name = 'Boleto'
    icon = 'fa-barcode'
    template = 'boleto/admin/order_section.jinja'
    extra_js = 'boleto/admin/order_section_extra_js.jinja'
    order = 10

    @staticmethod
    def visible_for_order(order):
        return isinstance(order.payment_method.payment_processor, BoletoPaymentProcessor)

    @staticmethod
    def get_context_data(order):
        if not hasattr(order, 'boleto'):
            return {}

        boleto = order.boleto

        return {
            'order': order,
            'due_date': boleto.due_date,
            'bank_service': boleto.bank_service,
            'number_line': boleto.number_line,
            'total': boleto.total,
            'payment_date': boleto.payment_date,
            'payment_amount': boleto.payment_amount,
            'nosso_numero': boleto.nosso_numero,
            'status': boleto.status,
            'num_sequencial': boleto.info['num_sequencial'],
        }
