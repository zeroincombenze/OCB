# -*- coding: utf-8 -*-
#
# Copyright 2018-20 - SHS-AV s.r.l. <https://www.zeroincombenze.it/>
#
# Contributions to development, thanks to:
# * Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
#
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
{
    'name': 'midea_extend_partner',
    'summary': 'Sample module to extend res.partner model',
    'version': '6.0.0.1.0',
    'category': 'Generic Modules/Accounting',
    'author': 'Odoo Community Association (OCA), SHS-AV s.r.l.',
    'website': 'https://odoo-community.org/',
    'depends': ['base'],
    'data': [
        'views/partner_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'description': r'''
Overview / Panoramica
=====================

Questo modulo è un esempio di come estendere la tabella res.partner
''',
}
