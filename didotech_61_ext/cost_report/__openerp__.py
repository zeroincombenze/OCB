# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product Detailed Structure Cost Report, Open Source    
#    Copyright (C) 2017 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#
#    Created on: 2017-12-01
#    Author : Fabio Colognesi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Product Detailed Structure Cost Report',
    'version': '0.1.3.0',
    'author': 'TechSpell srl',
    'website': 'http://www.techspell.eu',
    'category': 'Business Analysis',
    'sequence': 15,
    'summary': 'Creates detailed reports about product cost structure.',
    'images': [],
    'depends': ['mrp'],
    'description': """
Detailed Structure Cost Report in LibrErp
==============================================

This module adds capability to explode cost structure report to all levels of a complex Bill of Material.

    """,
    'data': [
        'report/price.xml',
        'wizard/cost_report_view.xml',
       ],
    'demo': [
        ],
    'test': [
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
