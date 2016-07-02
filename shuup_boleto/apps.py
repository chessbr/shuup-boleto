# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.


from shuup.apps import AppConfig


class ShuupBoletoAppConfig(AppConfig):
    name = "shuup_boleto"
    verbose_name = "Shuup Boleto"
    provides = {
        "service_provider_admin_form": [
            "shuup_boleto.admin.forms:BoletoPaymentProcessorForm",
        ],
        "service_behavior_component_form": [
            "shuup_boleto.admin.forms:CecredBoletoBehaviorComponentForm",
        ],
        "admin_order_section": [
             "shuup_boleto.admin.order_section:BoletoOrderSection"
        ],
        "admin_module": [
            "shuup_boleto.admin:BoletoModule",
        ],
        "xtheme_plugin": [
            "shuup_boleto.plugins:BoletoGeneratorCheckoutPlugin",
            "shuup_boleto.plugins.BoletoInfoOrderHistoryPlugin"
        ],
        "front_urls_pre": [
            "shuup_boleto.urls:urlpatterns"
        ],
    }
