# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Orders Barcode
#    Copyright (C) 2016 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#    $Id$
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
    'name': 'Manufacturing Orders Barcode',
    'version': '0.1.0.5',
    'author': 'TechSpell srl',
    'website': 'http://www.techspell.eu',
    'category': 'Manufacturing',
    'sequence': 15,
    'summary': 'Prints Manufacturing Orders using Barcode.',
    'images': [],
    'depends': ['mrp', 'mrp_operations'],
    'description': """
Manufacturing Orders Barcode
==============================================

This module adds capability to print Manufacturing Orders using Barcode.

It can be integrated with external applications to use barcode reader to register

Work Order activities (start, pause, resume, finish) directly from barcode.

Ask to TechSpell to obtain Windows Application "LibrERP MRP Companion".

    """,
    'data': [
        'report/mrp_order.xml',
        'data/mrp_operations.xml',
        ],
    'demo': [
        ],
    'test': [
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
