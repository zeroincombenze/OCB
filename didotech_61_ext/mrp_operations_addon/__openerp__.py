# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Operations Enhancement
#    Copyright (C) 2016 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#    Copyright (C) 2020 Didotech Srl
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
    'name': 'Manufacturing Operations Enhancement',
    'version': '3.10.8.76',
    'author': 'TechSpell srl',
    'website': 'http://www.techspell.eu',
    'category': 'Manufacturing',
    'sequence': 15,
    'summary': 'Extends Work Orders.',
    'images': [],
    'depends': [
        'mrp',
        'mrp_operations',
        'res_users_helper_functions',
        'hr_timesheet'
    ],
    'description': """
Manufacturing Operations Enhancement
==============================================

This module adds capability to manage real pause in Work Order.

Closing a Work Order using 'Finished' status it will be evaluated the

real delay between "Start" and "Finish" dates, subtracting all the pauses.

This allow you to obtain real costs (worked hours) related to a Work Order.

You will manage sale orders related to your own Order (one or more sale orders).


Ask to TechSpell to obtain 'Manufacturing Orders Barcode' module and the related

Windows Application "LibrERP MRP Companion".

    """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/workflow.xml',
        'views/mrp_workcenter_view.xml',
        'views/mrp_production_view.xml',
        'views/mrp_production_workcenter_line_view.xml',
        'views/mrp_fraction_operations_view.xml'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
