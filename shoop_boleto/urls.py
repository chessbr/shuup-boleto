# -*- coding: utf-8 -*-
# This file is part of Shoop Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from shoop_boleto.views import BoletoVisualizationView

from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^boleto/(?P<order_pk>.+?)/(?P<order_key>.+?)/$', BoletoVisualizationView.view_boleto, name='view_boleto'),
)
