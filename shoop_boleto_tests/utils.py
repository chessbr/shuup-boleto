# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from decimal import Decimal

from shoop_boleto.models import BoletoPaymentProcessor

from shoop.core.defaults.order_statuses import create_default_order_statuses
from shoop.core.models._product_shops import ShopProduct
from shoop.testing.factories import _get_service_provider, get_default_product, get_default_shop
from shoop.testing.mock_population import populate_if_required
from shoop.xtheme._theme import set_current_theme

PRODUCT_PRICE = Decimal(15.0)


def get_payment_provider(**kwargs):
    provider = _get_service_provider(BoletoPaymentProcessor)

    # override attributes
    for k,v in kwargs.items():
        if hasattr(provider, k):
            setattr(provider, k, v)

    provider.save()
    return provider


def initialize():
    get_default_shop()
    set_current_theme('shoop.themes.classic_gray')
    create_default_order_statuses()
    populate_if_required()

    default_product = get_default_product()
    sp = ShopProduct.objects.get(product=default_product, shop=get_default_shop())
    sp.default_price = get_default_shop().create_price(PRODUCT_PRICE)
    sp.save()
