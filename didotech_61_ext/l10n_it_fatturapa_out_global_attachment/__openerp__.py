# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016-2020 Didotech srl
#
##############################################################################
{
    'name': 'Italian Localization - FatturaPA - Emission',
    'version': '6.1.0.2.0',
    'category': 'Localization/Italy',
    'summary': 'Electronic invoices emission',
    'author': 'Didotech SRL',
    'description': """

Italian Localization - FatturaPA - Emission
===========================================

""",
    'website': 'http://www.didotech.com',
    'license': 'AGPL-3',
    "depends": [
        'l10n_it_fatturapa',
        'l10n_it_fatturapa_out',
    ],
    "data": [
        'views/company_view.xml',
        'wizard/wizard_export_fatturapa_view.xml',
    ],
    "test": [],
    "installable": True,
}
