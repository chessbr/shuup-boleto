# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.currencybound import CurrencyBound
from shuup.admin.utils.urls import admin_url

from django.utils.translation import ugettext_lazy as _


class BoletoModule(CurrencyBound, AdminModule):
    name = _("Boleto")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:boleto.dashboard")

    def get_urls(self):
        return [
            admin_url(
                "^boleto/$",
                "shuup_boleto.admin.views.DashboardView",
                name="boleto.dashboard"
            ),
            admin_url(
                "^boleto/(?P<pk>\d+)/pay/$",
                "shuup_boleto.admin.views.PayBoletoView",
                name="boleto.pay-boleto"
            ),
            admin_url(
                "^boleto/(?P<pk>\d+)/reset/$",
                "shuup_boleto.admin.views.ResetBoletoView",
                name="boleto.reset-boleto"
            ),
            admin_url(
                "^boleto/(?P<pk>\d+)/cancel/$",
                "shuup_boleto.admin.views.CancelBoletoView",
                name="boleto.cancel-boleto"
            ),
        ]

    def get_menu_entries(self, request):
        category = _("Boleto")
        return [
            MenuEntry(
                text="Boleto",
                icon="fa fa-barcode",
                url="shuup_admin:boleto.dashboard",
                category=category,
                aliases=[_("Show Dashboard")]
            ),
        ]
