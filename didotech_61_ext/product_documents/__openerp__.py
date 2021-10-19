# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 Didotech SRL
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
    'name': 'Product History Grouped',
    'version': '3.0.0.0',
    "category": 'Hidden/Dependency',
    'complexity': "easy",
    'description': """

    This Module add a history for the product / customer on multiple document

    """,
    'author': 'Didotech SRL',
    'depends': [
        'base',
        'product',
        'sale',
        'account',
        'purchase'
    ],
    'website': 'http://www.didotech.com',
    'data': [
        'security/ir.model.access.csv',
        'views/product_document_grouped.xml',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
