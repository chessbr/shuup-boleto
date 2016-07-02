# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.


import pytest

from shuup_boleto.models import BoletoBehaviorComponentMixin
from shuup_boleto_tests.utils import initialize
from shuup_tests.utils import SmartClient

from django.core.urlresolvers import reverse


def test_mixin():
    with pytest.raises(AttributeError):
        BoletoBehaviorComponentMixin().generate_boleto(None, None)


@pytest.mark.django_db
def test_boleto_not_exists():
    initialize()
    view_boleto_path = reverse("shuup:view_boleto", kwargs={"order_pk": 123, "order_key": "32131"})
    response = SmartClient().get(view_boleto_path)
    assert response.status_code == 500
