# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from enumfields import Enum

from django.utils.translation import ugettext_lazy as _


class BankService(Enum):
    BB = '001'
    CECRED = '085'
    CEF = '104'

    class Labels:
        BB = _('001 - Banco do Brasil')
        CECRED = _('085 - CECRED')
        CEF = _('104 - Caixa Econômica Federal')


class BoletoStatus(Enum):
    Created = 0
    Paid = 1
    Expired = 2

    class Labels:
        Created = _(u'Criado')
        Paid = _(u'Pago')
        Expired = _(u'Vencido')


class DocumentType(Enum):
    DM = 0
    DS = 1
    RC = 2
    NF = 4

    class Labels:
        DM = _(u'Duplicata Mercantil')
        DS = _(u'Duplicata de Serviço')
        RC = _(u'Recibo')
        NF = _(u'Nota Fiscal')
