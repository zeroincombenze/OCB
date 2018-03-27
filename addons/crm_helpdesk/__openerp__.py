# -*- coding: utf-8 -*-
#    Copyright (C) 2004-2017 Odoo S.A. (<http://www.odoo.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
{
    'name': 'Helpdesk',
    'category': 'Customer Relationship Management',
    'version': '8.0.1.0',
    'description': """
Helpdesk Management.
====================

Like records and processing of claims, Helpdesk and Support are good tools
to trace your interventions. This menu is more adapted to oral communication,
which is not necessarily related to a claim. Select a customer, add notes and
categorize your interventions with a channel and a priority level.
    """,
    'author': 'Odoo SA',
    'website': 'https://www.odoo.com',
    'depends': ['crm'],
    'data': [
        'crm_helpdesk_view.xml',
        'crm_helpdesk_menu.xml',
        'security/ir.model.access.csv',
        'report/crm_helpdesk_report_view.xml',
        'crm_helpdesk_data.xml',
    ],
    'demo': ['crm_helpdesk_demo.xml'],
    'test': ['test/process/help-desk.yml'],
    'installable': True,
    'auto_install': False,
}
