# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

import logging

from shuup_boleto.models import StoredBoleto

from django.http.response import HttpResponse, HttpResponseServerError
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class BoletoVisualizationView(object):

    @staticmethod
    def view_boleto(request, order_pk, order_key):

        try:
            boleto = StoredBoleto.objects.get(order__pk=order_pk, order__key=order_key)
            return HttpResponse(boleto.html)

        except:
            logger.exception(u"Erro ao visualizar boleto do pedido {0}".format(order_pk))
            return HttpResponseServerError(_(u"Erro ao gerar boleto ou documento não encontrado."))
