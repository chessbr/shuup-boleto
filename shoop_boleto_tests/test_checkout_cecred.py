# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from mock import patch
import pytest

from shoop_boleto.constants import BankService, DocumentType
from shoop_boleto.models import BoletoPaymentProcessor, CecredBoletoBehaviorComponent, StoredBoleto
from shoop_boleto_tests.utils import get_payment_provider, initialize
from shoop_tests.front.test_checkout_flow import fill_address_inputs
from shoop_tests.utils import SmartClient

from shoop.core.models._orders import Order, PaymentStatus
from shoop.testing.factories import (
    get_default_product, get_default_shipping_method, get_default_shop, get_default_supplier,
    get_default_tax_class
)
from shoop.testing.soup_utils import extract_form_fields

from django.core.urlresolvers import reverse
from django.http.response import HttpResponse


@pytest.mark.django_db
def test_boleto_cecred_success():
    """
    Usuário faz a compra e seleciona boleto como forma de pagamento (3 vezes seguidas)
    Boleto CECRED configurado
    """

    initialize()

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


    for ix in range(3):

        c = SmartClient()
        default_product = get_default_product()

        basket_path = reverse("shoop:basket")
        add_to_basket_resp = c.post(basket_path, data={
            "command": "add",
            "product_id": default_product.pk,
            "quantity": 1,
            "supplier": get_default_supplier().pk
        })
        assert add_to_basket_resp.status_code < 400


        # Resolve paths
        addresses_path = reverse("shoop:checkout", kwargs={"phase": "addresses"})
        methods_path = reverse("shoop:checkout", kwargs={"phase": "methods"})
        confirm_path = reverse("shoop:checkout", kwargs={"phase": "confirm"})


        # Phase: Addresses
        addresses_soup = c.soup(addresses_path)
        inputs = fill_address_inputs(addresses_soup, with_company=False)
        response = c.post(addresses_path, data=inputs)
        assert response.status_code == 302, "Address phase should redirect forth"
        assert response.url.endswith(methods_path)

        # Phase: Methods
        assert Order.objects.filter(payment_method=payment_method).count() == ix
        response = c.post(
            methods_path,
            data={
                "payment_method": payment_method.pk,
                "shipping_method": shipping_method.pk
            }
        )

        assert response.status_code == 302, "Methods phase should redirect forth"
        assert response.url.endswith(confirm_path)
        response = c.get(confirm_path)
        assert response.status_code == 200

        # Phase: Confirm
        assert Order.objects.count() == ix
        confirm_soup = c.soup(confirm_path)
        response = c.post(confirm_path, data=extract_form_fields(confirm_soup))
        assert response.status_code == 302, "Confirm should redirect forth"

        assert Order.objects.count() == ix+1
        order = Order.objects.filter(payment_method=payment_method).first()
        assert order.payment_status == PaymentStatus.NOT_PAID

        process_payment_path = reverse("shoop:order_process_payment", kwargs={"pk": order.pk, "key": order.key})
        process_payment_return_path = reverse("shoop:order_process_payment_return",kwargs={"pk": order.pk, "key": order.key})
        order_complete_path = reverse("shoop:order_complete",kwargs={"pk": order.pk, "key": order.key})

        assert response.url.endswith(process_payment_path), ("Confirm should have redirected to payment page")

        response = c.get(process_payment_path)
        assert response.status_code == 302, "Payment page should redirect forth"
        assert response.url.endswith(process_payment_return_path)

        response = c.get(process_payment_return_path)
        assert response.status_code == 302, "Payment return should redirect forth"
        assert response.url.endswith(order_complete_path)

        order.refresh_from_db()
        assert order.payment_status == PaymentStatus.NOT_PAID

        from python_boleto.cecred import CecredBoleto
        bcecred = CecredBoleto(**order.boleto.info)
        bcecred.validate()
        assert len(order.boleto.html) > 0
        
        # "visualiza o boleto"
        view_boleto_path = reverse("shoop:view_boleto", kwargs={"order_pk": order.pk, "order_key": order.key})
        response = c.get(view_boleto_path)
        assert HttpResponse(order.boleto.html).content == response.content


@pytest.mark.django_db
def test_boleto_cecred_error():
    """
    Usuário faz a compra e seleciona boleto como forma de pagamento
    Boleto CECRED configurado incorretamente
    Pedido finalizado com sucesso, boleto é gerado, mas incorretamente
    """
    initialize()

    c = SmartClient()
    default_product = get_default_product()

    basket_path = reverse("shoop:basket")
    add_to_basket_resp = c.post(basket_path, data={
        "command": "add",
        "product_id": default_product.pk,
        "quantity": 1,
        "supplier": get_default_supplier().pk
    })
    assert add_to_basket_resp.status_code < 400


    # Create methods
    shipping_method = get_default_shipping_method()
    processor = get_payment_provider()
    assert isinstance(processor, BoletoPaymentProcessor)

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
    behavior_component.convenio = '' # <==== Erro aqui
    behavior_component.carteira = '12'
    behavior_component.save()


    # Resolve paths
    addresses_path = reverse("shoop:checkout", kwargs={"phase": "addresses"})
    methods_path = reverse("shoop:checkout", kwargs={"phase": "methods"})
    confirm_path = reverse("shoop:checkout", kwargs={"phase": "confirm"})


    # Phase: Addresses
    addresses_soup = c.soup(addresses_path)
    inputs = fill_address_inputs(addresses_soup, with_company=False)
    response = c.post(addresses_path, data=inputs)
    assert response.status_code == 302, "Address phase should redirect forth"
    assert response.url.endswith(methods_path)

    # Phase: Methods
    assert Order.objects.filter(payment_method=payment_method).count() == 0
    response = c.post(
        methods_path,
        data={
            "payment_method": payment_method.pk,
            "shipping_method": shipping_method.pk
        }
    )

    assert response.status_code == 302, "Methods phase should redirect forth"
    assert response.url.endswith(confirm_path)
    response = c.get(confirm_path)
    assert response.status_code == 200

    # Phase: Confirm
    assert Order.objects.count() == 0
    confirm_soup = c.soup(confirm_path)
    response = c.post(confirm_path, data=extract_form_fields(confirm_soup))
    assert response.status_code == 302, "Confirm should redirect forth"

    assert Order.objects.count() == 1
    order = Order.objects.filter(payment_method=payment_method).first()
    assert order.payment_status == PaymentStatus.NOT_PAID

    process_payment_path = reverse("shoop:order_process_payment", kwargs={"pk": order.pk, "key": order.key})
    process_payment_return_path = reverse("shoop:order_process_payment_return",kwargs={"pk": order.pk, "key": order.key})
    order_complete_path = reverse("shoop:order_complete",kwargs={"pk": order.pk, "key": order.key})

    assert response.url.endswith(process_payment_path), ("Confirm should have redirected to payment page")

    response = c.get(process_payment_path)
    assert response.status_code == 302, "Payment page should redirect forth"
    assert response.url.endswith(process_payment_return_path)

    response = c.get(process_payment_return_path)
    assert response.status_code == 302, "Payment return should redirect forth"
    assert response.url.endswith(order_complete_path)

    order.refresh_from_db()
    assert order.payment_status == PaymentStatus.NOT_PAID

    from python_boleto.cecred import CecredBoleto
    bcecred = CecredBoleto(**order.boleto.info)

    # boleto não é valido
    with pytest.raises(ValueError):
        bcecred.validate()
        assert len(order.boleto.html) == 0


@pytest.mark.django_db
def test_boleto_cecred_error2():
    """
    Usuário faz a compra e seleciona boleto como forma de pagamento
    Boleto CECRED configurado incorretamente
    Pedido finalizado com sucesso, boleto NÃO é gerado
    """
    initialize()

    c = SmartClient()
    default_product = get_default_product()

    basket_path = reverse("shoop:basket")
    add_to_basket_resp = c.post(basket_path, data={
        "command": "add",
        "product_id": default_product.pk,
        "quantity": 1,
        "supplier": get_default_supplier().pk
    })
    assert add_to_basket_resp.status_code < 400


    # Create methods
    shipping_method = get_default_shipping_method()
    processor = get_payment_provider()
    assert isinstance(processor, BoletoPaymentProcessor)

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
    behavior_component.convenio = '32312'
    behavior_component.carteira = '12'
    behavior_component.save()


    # Resolve paths
    addresses_path = reverse("shoop:checkout", kwargs={"phase": "addresses"})
    methods_path = reverse("shoop:checkout", kwargs={"phase": "methods"})
    confirm_path = reverse("shoop:checkout", kwargs={"phase": "confirm"})


    # Phase: Addresses
    addresses_soup = c.soup(addresses_path)
    inputs = fill_address_inputs(addresses_soup, with_company=False)
    response = c.post(addresses_path, data=inputs)
    assert response.status_code == 302, "Address phase should redirect forth"
    assert response.url.endswith(methods_path)

    # Phase: Methods
    assert Order.objects.filter(payment_method=payment_method).count() == 0
    response = c.post(
        methods_path,
        data={
            "payment_method": payment_method.pk,
            "shipping_method": shipping_method.pk
        }
    )

    assert response.status_code == 302, "Methods phase should redirect forth"
    assert response.url.endswith(confirm_path)
    response = c.get(confirm_path)
    assert response.status_code == 200

    # quando vai gerar boleto estoura uma exceção
    with patch.object(CecredBoletoBehaviorComponent, 'generate_boleto') as mocked:
        mocked.side_effect = NotImplementedError()

        # Phase: Confirm
        assert Order.objects.count() == 0
        confirm_soup = c.soup(confirm_path)
        response = c.post(confirm_path, data=extract_form_fields(confirm_soup))
        assert response.status_code == 302, "Confirm should redirect forth"
    
        assert Order.objects.count() == 1
        order = Order.objects.filter(payment_method=payment_method).first()
        assert order.payment_status == PaymentStatus.NOT_PAID
    
        process_payment_path = reverse("shoop:order_process_payment", kwargs={"pk": order.pk, "key": order.key})
        process_payment_return_path = reverse("shoop:order_process_payment_return",kwargs={"pk": order.pk, "key": order.key})
        order_complete_path = reverse("shoop:order_complete",kwargs={"pk": order.pk, "key": order.key})
    
        assert response.url.endswith(process_payment_path), ("Confirm should have redirected to payment page")
    
        response = c.get(process_payment_path)
        assert response.status_code == 302, "Payment page should redirect forth"
        assert response.url.endswith(process_payment_return_path)
    
        response = c.get(process_payment_return_path)
        assert response.status_code == 302, "Payment return should redirect forth"
        assert response.url.endswith(order_complete_path)
    
        order.refresh_from_db()
        assert order.payment_status == PaymentStatus.NOT_PAID

        # BOLETO NÃO EXISTE
        assert not hasattr(order, 'boleto')
        assert not StoredBoleto.objects.filter(order=order).exists()
