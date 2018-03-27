# -*- coding: utf-8 -*-
#
# Copyright 2010, Odoo Italian Community <http://www.odoo-italia.org>)
# Copyright 2010, Servabit srl
# Copyright 2010, Agile Business Group sagl
# Copyright 2010, Domsense srl
# Copyright 2010, Albatos srl
# Copyright 2011-2017, Associazione Odoo Italia <https://odoo-italia.org>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
{
    'name': 'Italy - Accounting',
    'version': '7.0.0.2.1',
    'depends': ['base_vat', 'account_chart', 'base_iban'],
    'author': 'OpenERP Italian Community',
    'description': """
Esempio Piano dei conti italiano
================================

Italian accounting chart and localization.
    """,
    'license': 'AGPL-3',
    'category': 'Localization/Account Charts',
    'website': 'http://www.openerp-italia.org/',
    'data': [
        'data/account.account.template.csv',
        'data/account.tax.code.template.csv',
        'account_chart.xml',
        'data/account.tax.template.csv',
        'data/account.fiscal.position.template.csv',
        'l10n_chart_it_generic.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'images': ['images/config_chart_l10n_it.jpeg', 'images/l10n_it_chart.jpeg'],
}
