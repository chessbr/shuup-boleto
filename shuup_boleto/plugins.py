# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from shuup_boleto.models import StoredBoleto

from shuup.core.models import Order
from shuup.xtheme.plugins._base import TemplatedPlugin

from django.core.urlresolvers import resolve, Resolver404
from django.utils.translation import ugettext_lazy as _


class BoletoGeneratorCheckoutPlugin(TemplatedPlugin):
    """
    Plugin para exibir botão para gerar o boleto do pedido
    """
    identifier = "shuup_boleto.checkout_boleto_generator"
    name = _(u"Link para visualizar boleto bancário na finalização do pedido")
    template_name = "plugins/checkout_boleto_generator.jinja"

    def get_context_data(self, context):
        """
        obtém a pk e a key do pedido e coloca no contexto
        """

        context_data = super(BoletoGeneratorCheckoutPlugin, self).get_context_data(context)
        request = context_data["request"]

        try:
            resolved = resolve(request.path)

            if resolved.view_name == 'shuup:order_complete':
                context_data["order_pk"] = resolved.kwargs.get('pk')
                context_data["order_key"] = resolved.kwargs.get('key')
                context_data["boleto"] = StoredBoleto.objects.get(order__pk=context_data["order_pk"],
                                                                  order__key=context_data["order_key"])

        except Resolver404:
            pass
        except StoredBoleto.DoesNotExist:
            pass

        return context_data


class BoletoInfoOrderHistoryPlugin(TemplatedPlugin):
    """
    Plugin para exibir dados do boleto no histório do pedido
    """
    identifier = "shuup_boleto.order_history_boleto_info"
    name = _(u"Informações do boleto bancário no histórico de pedido")
    template_name = "plugins/order_history_boleto_info.jinja"

    def get_context_data(self, context):
        """
        obtém o boleto do pedido e adiciona ele no contexto
        """

        context_data = super(BoletoInfoOrderHistoryPlugin, self).get_context_data(context)
        request = context_data["request"]

        try:
            resolved = resolve(request.path)

            if resolved.view_name == 'shuup:show-order':
                context_data["order"] = Order.objects.get(pk=resolved.kwargs.get('pk'))

        except Resolver404:
            pass
        except Order.DoesNotExist:
            pass

        return context_data
