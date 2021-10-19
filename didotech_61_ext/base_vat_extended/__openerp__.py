# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'VAT Number Partner Search',
    'version': '3.1.10.3',
    "category": 'Hidden/Dependency',
    'complexity': "easy",
    'description': """

    Using VIES Website find partner data for easy insert

    """,
    'author': 'Didotech SRL',
    'depends': [
        'base_vat',
        'account',
        'crm_lead_correct'
    ],
    'website': 'http://www.didotech.com',
    'data': [
        'views/partner_view.xml',
        'views/crm_view.xml'
    ],
    'installable': True,
    'auto_install': True,
    'external_dependencies': {
        'python': ['pyvies'],
    }
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
