# -*- coding: utf-8 -*-
# © 2018-2020 Andrei Levin - Didotech srl (www.didotech.com)

{
    "name": "Document 2C FatturaPA",
    "version": "3.3.30.13",
    "author": "Nicola Gramola <nicola.gramola@didotech.com> - Didotech SRL",
    "category": 'Partner',
    "description": """
Gestione Fattura Elettronica in 2C
==================================

    """,
    'website': 'www.didotech.com',
    "depends": [
        "base",
        'document',
        'l10n_it_fatturapa_out'
    ],
    'data': [
        # 'security/ir_model_access.csv',
        'views/company_view.xml',
        'views/account_view.xml',
        'views/fattura_view.xml',
        'wizard/wizard_import_invoice_view.xml',
        'wizard/wizard_create_export_invoice_view.xml',
        'data/2c_data.xml',
        'cron.xml',
    ],
    'external_dependencies': {
        'python': [
            'zeep',
        ]
    },
    'installable': True,
    'auto_install': False,
}
