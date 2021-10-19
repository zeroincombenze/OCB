# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
#    Copyright 2015 Agile Business Group <http://www.agilebg.com>
#    Copyright (C) 2018-2020 Didotech Srl <http://www.didotech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Italian Localization - E-Fattura',
    'version': '6.1.10.20.12',
    'category': 'Localization/Italy',
    'summary': 'Electronic invoices',
    'author': 'Davide Corio, Agile Business Group, Innoviu, Didotech srl',
    'website': 'http://www.odoo-italia.org',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Italian Localization - Fattura Elettronica
==========================================

Base module to handle FatturaPA data.
http://fatturapa.gov.it

See l10n_it_fatturapa_out and l10n_it_fatturapa_in.


Installation
============

This module requires PyXB 1.2.4
http://pyxb.sourceforge.net/


Configuration
=============

 * Edit the FatturaPA fields of the partners (in partner form) who will receive
   (send) the electronic invoices. IPA code is mandatory, EORI code is not.
 * Configure payment terms filling the fatturaPA fields related to payment
   terms and payment methods.
 * Configure taxes about 'Non taxable nature', 'Law reference'
   and 'VAT payability'
 * Configure FatturaPA data in Accounting Configuration. Note that a sequence
   'fatturaPA' is already loaded by the module and selectable.


Update
======

A new version of files _ds.py and fatturapa_v_1_x.py can be produced from file *.xsd:

$ pyxbgen -u Schema_del_file_xml_FatturaPA_versione_1.2.xsd -m fatturapa_v_1_2


Info
====

http://www.fatturapa.gov.it/export/fatturazione/it/normativa/f-2.htm



Credits
=======

Contributors
------------

* Davide Corio <davide.corio@abstract.it>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Roberto Onnis <roberto.onnis@innoviu.com>
* Alessio Gerace <alessio.gerace@agilebg.com>
* Carlo Vettore <carlo.vettore@didotech.com>
* Andrei Levin <andrei.levin@didotech.com>

Maintainer
----------

This module is maintained by Didotech srl.

""",
    'license': 'AGPL-3',
    "depends": [
        'account',
        'l10n_it_base',
        'l10n_it_ade',
        'document',
        'l10n_it_ipa',
        'l10n_it_rea',
        'base_iban',
        'l10n_it_account',
        ],
    "data": [
        'data/fatturapa_data.xml',
        'data/welfare.fund.type.csv',
        'data/company_data.xml',
        'views/account_view.xml',
        'views/company_view.xml',
        'views/partner_view.xml',
        'views/account_fiscal_position_view.xml',
        'security/ir.model.access.csv',
    ],
    "test": [],
    "demo": ['demo/account_invoice_fatturapa.xml'],
    "installable": True,
    'external_dependencies': {
        'python': ['pyxb'],
    }
}
