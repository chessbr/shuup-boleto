# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from shuup_boleto.admin.forms import BoletoPaymentProcessorForm, CecredBoletoBehaviorComponentForm


def test_forms():
    # just for coverage
    f = BoletoPaymentProcessorForm()
    f.is_valid()

    f = CecredBoletoBehaviorComponentForm()
    f.is_valid()
