# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Operations Wizard
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
    'name': 'Manufacturing Operations Wizard',
    'version': '0.3.2.4',
    'author': 'TechSpell srl',
    'website': 'http://www.techspell.eu',
    'category': 'Manufacturing',
    'sequence': 15,
    'summary': 'Use Work Orders Wizard.',
    'images': [],
    'depends': ['mrp_operations_addon'],
    'description': """
Manufacturing Operations wizard
==============================================

This module adds capability to Start/Pause/End Work Orders managing them from a wizard.

Worked hours will be computed by Manufacturing Operation Enhancement module.

Ask to TechSpell to obtain 'Manufacturing Orders Barcode' module and the related

Windows Application "LibrERP MRP Companion".

    """,
    'data': [
        'wizard/mrp_operations_view.xml',
        'security/ir.model.access.csv',
        ],
    'depends': [
        'mrp_operations_addon'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
