# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from decimal import Decimal

import pytest

from shoop_boleto.admin.order_section import BoletoOrderSection
from shoop_boleto.constants import BankService, BoletoStatus, DocumentType
from shoop_boleto.models import BoletoPaymentProcessor
from shoop_boleto_tests.utils import get_payment_provider, initialize
from shoop_tests.front.test_checkout_flow import fill_address_inputs
from shoop_tests.utils import SmartClient

from shoop.core.models._orders import Order
from shoop.testing.factories import (
    get_default_product, get_default_shipping_method, get_default_shop, get_default_supplier,
    get_default_tax_class
)
from shoop.testing.soup_utils import extract_form_fields
from shoop.testing.utils import apply_request_middleware
from shoop.utils.importing import load

from django.core.urlresolvers import reverse


def create_success_order_with_boleto():
    # Create methods
    shipping_method = get_default_shipping_method()
    processor = get_payment_provider()
    assert isinstance(processor, BoletoPaymentProcessor)
    choices = processor.get_service_choices()
    assert len(choices) == 1

    payment_method = processor.create_service(
        BankService.CECRED.value,
        identifier="cecred",
        shop=get_default_shop(),
        name="boleto cecred",
        enabled=True,
        tax_class=get_default_tax_class())

    # Configura de acordo
    behavior_component = payment_method.behavior_components.first()
    behavior_component.local_pagamento = "a simple test"
    behavior_component.cedente = "a simple user"
    behavior_component.prazo_vencimento = 4
    behavior_component.instrucoes = ["line1", "line2"]
    behavior_component.especie_doc = DocumentType.DM
    behavior_component.layout = 'v06'
    behavior_component.agencia = '123431'
    behavior_component.conta = '6427364732'
    behavior_component.convenio = '123456'
    behavior_component.carteira = '12'
    behavior_component.save()

    c = SmartClient()
    default_product = get_default_product()

    basket_path = reverse("shoop:basket")
    c.post(basket_path, data={
        "command": "add",
        "product_id": default_product.pk,
        "quantity": 1,
        "supplier": get_default_supplier().pk
    })

    # Resolve paths
    addresses_path = reverse("shoop:checkout", kwargs={"phase": "addresses"})
    methods_path = reverse("shoop:checkout", kwargs={"phase": "methods"})
    confirm_path = reverse("shoop:checkout", kwargs={"phase": "confirm"})

    # Phase: Addresses
    addresses_soup = c.soup(addresses_path)
    inputs = fill_address_inputs(addresses_soup, with_company=False)
    c.post(addresses_path, data=inputs)

    c.post(
        methods_path,
        data={
            "payment_method": payment_method.pk,
            "shipping_method": shipping_method.pk
        }
    )

    c.get(confirm_path)
    confirm_soup = c.soup(confirm_path)
    c.post(confirm_path, data=extract_form_fields(confirm_soup))

    order = Order.objects.filter(payment_method=payment_method).first()

    process_payment_path = reverse("shoop:order_process_payment", kwargs={"pk": order.pk, "key": order.key})
    process_payment_return_path = reverse("shoop:order_process_payment_return",kwargs={"pk": order.pk, "key": order.key})
    order_complete_path = reverse("shoop:order_complete",kwargs={"pk": order.pk, "key": order.key})

    c.get(process_payment_path)
    c.get(process_payment_return_path)
    c.get(order_complete_path)

    order.refresh_from_db()
    return order


@pytest.mark.django_db
def test_boleto_views_success(rf, admin_user):
    initialize()

    view = load("shoop.admin.views.dashboard.DashboardView").as_view()
    request = apply_request_middleware(rf.get("/"), user=admin_user)
    response = view(request)
    assert response.status_code == 200


    view = load("shoop_boleto.admin.views.DashboardView").as_view()
    request = apply_request_middleware(rf.get("/"), user=admin_user)
    response = view(request)
    assert response.status_code == 200
    
    order = create_success_order_with_boleto()
    
    assert BoletoOrderSection.visible_for_order(order)
    context_data = BoletoOrderSection.get_context_data(order)
    assert context_data == {
            'order': order,
            'due_date': order.boleto.due_date,
            'bank_service': order.boleto.bank_service,
            'number_line': order.boleto.number_line,
            'total': order.boleto.total,
            'payment_date': order.boleto.payment_date,
            'payment_amount': order.boleto.payment_amount,
            'nosso_numero': order.boleto.nosso_numero,
            'status': order.boleto.status,
            'num_sequencial': order.boleto.info['num_sequencial'],
        }
    

    assert order.boleto.status == BoletoStatus.Created
    assert order.boleto.payment_date is None
    assert order.boleto.total.value == order.taxful_total_price.value
    assert order.boleto.payment_amount.value == Decimal()

    assert BoletoOrderSection.get_context_data(Order()) == {}

    # atribui como Pago
    view = load("shoop_boleto.admin.views.PayBoletoView").as_view()
    request = apply_request_middleware(rf.post("/"), user=admin_user)
    response = view(request, pk=order.pk)
    assert response.status_code == 200
    order.boleto.refresh_from_db()
    assert order.boleto.status == BoletoStatus.Paid
    assert not order.boleto.payment_date is None
    assert order.boleto.total.value == order.taxful_total_price.value
    assert order.boleto.payment_amount.value == order.taxful_total_price.value


    # limpa o status
    view = load("shoop_boleto.admin.views.ResetBoletoView").as_view()
    request = apply_request_middleware(rf.post("/"), user=admin_user)
    response = view(request, pk=order.pk)
    assert response.status_code == 200
    order.boleto.refresh_from_db()
    assert order.boleto.status == BoletoStatus.Created
    assert order.boleto.payment_date is None
    assert order.boleto.total.value == order.taxful_total_price.value
    assert order.boleto.payment_amount.value == Decimal()


    # cancela
    view = load("shoop_boleto.admin.views.CancelBoletoView").as_view()
    request = apply_request_middleware(rf.post("/"), user=admin_user)
    response = view(request, pk=order.pk)
    assert response.status_code == 200
    order.boleto.refresh_from_db()
    assert order.boleto.status == BoletoStatus.Expired
    assert order.boleto.payment_date is None
    assert order.boleto.total.value == order.taxful_total_price.value
    assert order.boleto.payment_amount.value == Decimal()
