# -*- coding: utf-8 -*-
# This file is part of Shuup Boleto.
#
# Copyright (c) 2016, Rockho Team. All rights reserved.
# Author: Christian Hess
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from babel.messages import frontend as babel
import setuptools

"""
    How to translate:
    Babel integration: http://babel.pocoo.org/en/stable/setup.html

    - Extract messages:
        `python setup.py extract_messages -D django --output-file shuup_boleto/locale/django.pot`

    - Update an existing catalog (language):
        `python setup.py -D django update_catalog -l pt_BR -i shuup_boleto/locale/django.pot -d shuup_boleto/locale`

    - Compile catalog:
        `python setup.py compile_catalog -D django -d shuup_boleto/locale -l pt_BR`

    - Create a new catalog (language):
        `python setup.py init_catalog -D django -l pt_BR -i shuup_boleto/locale/django.pot -d shuup_boleto/locale`
"""

NAME = 'shuup-boleto'
VERSION = '1.0.0'
DESCRIPTION = 'Boleto payment add-on for Shuup'
AUTHOR = 'Rockho Team'
AUTHOR_EMAIL = 'rockho@rockho.com.br'
URL = 'http://www.rockho.com.br/'
LICENSE = 'AGPL-3.0'

EXCLUDED_PACKAGES = [
    'shuup_boleto_tests', 'shuup_boleto_tests.*',
]

REQUIRES = [
]

if __name__ == '__main__':
    setuptools.setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        url=URL,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license=LICENSE,
        packages=["shuup_boleto"],
        include_package_data=True,
        install_requires=REQUIRES,
        entry_points={"shuup.addon": "shuup_boleto=shuup_boleto"},
        cmdclass={'compile_catalog': babel.compile_catalog,
                  'extract_messages': babel.extract_messages,
                  'init_catalog': babel.init_catalog,
                  'update_catalog': babel.update_catalog},
        message_extractors={
            'shuup_boleto': [
                ('**.py', 'python', None),
                ('**/templates/**.html', 'jinja2', None),
                ('**/templates/**.jinja', 'jinja2', None)
            ],
        }
    )
