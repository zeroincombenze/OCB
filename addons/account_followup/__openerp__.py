# -*- coding: utf-8 -*-
# Copyright 2019 - Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
# Code full inherited by account_follow_up 8.0 of OCA
#
{
    'name': 'Payment Follow-up Management',
    'version': '8.0.1.0.1',
    'category': 'Accounting & Finance',
    'author': 'Odoo SA',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['account',
                'account_accountant',
                'mail'],
    'data': [
        'security/account_followup_security.xml',
        'security/ir.model.access.csv',
        'report/account_followup_report.xml',
        'data/account_followup_data.xml',
        'views/account_followup_view.xml',
        'views/account_followup_customers.xml',
        'wizard/account_followup_print_view.xml',
        'views/res_config_view.xml',
        'report/report_followup.xml',
        'report/account_followup_reports.xml'
    ],
    'demo': ['data/account_followup_demo.xml'],
    'test': [
        'test/account_followup.yml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
