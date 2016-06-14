# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
import datetime
from decimal import Decimal

import pytest

from shoop_boleto.constants import BankService
from shoop_boleto.models import StoredBoleto
from shoop_boleto.plugins import BoletoGeneratorCheckoutPlugin, BoletoInfoOrderHistoryPlugin
from shoop_tests.xtheme.test_plugins import get_context

from shoop.testing.factories import (
    create_order_with_product, get_default_product, get_default_shop, get_default_supplier
)
from shoop.testing.utils import apply_request_middleware

from django.core.urlresolvers import reverse


def create_order():
    PRODUCTS_TO_SEND = 10
    product = get_default_product()
    supplier = get_default_supplier()
    order = create_order_with_product(
        product,
        supplier=supplier,
        quantity=PRODUCTS_TO_SEND,
        taxless_base_unit_price=10,
        tax_rate=Decimal("0.5")
    )
    order.cache_prices()
    order.check_all_verified()
    order.save()
    return order


def get_context(rf, path):
    request = rf.get(path)
    request.shop = get_default_shop()
    apply_request_middleware(request)
    return {"request": request}


@pytest.mark.django_db
def test_checkout_generator_plugin(rf):
    order = create_order()
    boleto = StoredBoleto.objects.create(order=order,
                                         bank_service=BankService.CECRED,
                                         due_date=datetime.date.today())

    context = get_context(rf, reverse("shoop:order_complete", kwargs={"pk":order.pk, "key":order.key}))
    plugin = BoletoGeneratorCheckoutPlugin({})

    assert int(plugin.get_context_data(context)["order_pk"]) == order.pk
    assert plugin.get_context_data(context)["order_key"] == order.key
    assert int(plugin.get_context_data(context)["boleto"].id) == boleto.id

    # wrong path
    context = get_context(rf, "/")
    assert plugin.get_context_data(context).get("order_pk") is None

    # order does not exist
    context = get_context(rf, reverse("shoop:order_complete", kwargs={"pk":31231, "key":"3123213"}))
    assert not plugin.get_context_data(context)["order_pk"] is None
    assert not plugin.get_context_data(context)["order_key"] is None
    assert plugin.get_context_data(context).get("boleto") is None


@pytest.mark.django_db
def test_order_history_generator_plugin(rf):
    order = create_order()
    plugin = BoletoInfoOrderHistoryPlugin({})

    context = get_context(rf, reverse("shoop:show-order", kwargs={"pk":order.pk}))
    assert plugin.get_context_data(context)["order"].id == order.id

    # wrong path
    context = get_context(rf, "/")
    assert plugin.get_context_data(context).get("order") is None

    # order does not exist
    context = get_context(rf, reverse("shoop:show-order", kwargs={"pk":332312321}))
    assert plugin.get_context_data(context).get("order") is None
