# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import unicode_literals

from shoop_boleto.models import BoletoPaymentProcessor, CecredBoletoBehaviorComponent

from shoop.admin.forms import ShoopAdminForm

from django import forms


class BoletoPaymentProcessorForm(ShoopAdminForm):
    class Meta:
        model = BoletoPaymentProcessor
        exclude = ["identifier"]


class CecredBoletoBehaviorComponentForm(forms.ModelForm):
    class Meta:
        model = CecredBoletoBehaviorComponent
        exclude = ["identifier"]
        widgets = {
            'cedente': forms.Textarea(attrs={'rows': 1}),
            'local_pagamento': forms.Textarea(attrs={'rows': 1}),
            'instrucoes': forms.Textarea(attrs={'rows': 4})
        }
