# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.


from shoop.apps import AppConfig


class ShoopBoletoAppConfig(AppConfig):
    name = "shoop_boleto"
    verbose_name = "Shoop Boleto"
    provides = {
        "service_provider_admin_form": [
            "shoop_boleto.admin.forms:BoletoPaymentProcessorForm",
        ],
        "service_behavior_component_form": [
            "shoop_boleto.admin.forms:CecredBoletoBehaviorComponentForm",
        ],
        "admin_order_section": [
             "shoop_boleto.admin.order_section:BoletoOrderSection"
        ],
        "admin_module": [
            "shoop_boleto.admin:BoletoModule",
        ],
        "xtheme_plugin": [
            "shoop_boleto.plugins:BoletoGeneratorCheckoutPlugin",
            "shoop_boleto.plugins.BoletoInfoOrderHistoryPlugin"
        ],
        "front_urls_pre": [
            "shoop_boleto.urls:urlpatterns"
        ],
    }
