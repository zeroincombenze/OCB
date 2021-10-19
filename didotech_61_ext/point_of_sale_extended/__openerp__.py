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
    'name': 'Point Of Sale',
    'version': '3.18.22.32',
    'category': 'Point Of Sale',
    "sequence": 6,
    'description': """
This module provides a quick and easy sale process.
===================================================
tomatically.
    * Allow to refund former sales.
    """,
    'author': 'Didotech SRL',
    'depends': [
        'point_of_sale',
        'account',
        'account_voucher',
        'hr',
        'res_users_helper_functions',
        'hr_timesheet',
        'stock_picking_barcode',
        'product_visible_discount',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',
        'security/pos_security.xml',
        'security/stock_security.xml',
        'views/account_invoice_view.xml',
        'views/account_bank_statement.xml',
        'views/stock_picking_view.xml',
        'views/warehouse_menu.xml',
        'views/pos_history_view.xml',
        'views/point_of_sale_view.xml',
        'views/sale_shop_view.xml',
        # 'pos/point_make_payment_view.xml',
        'pos/cron.xml',
        'pos/reports.xml',
        'pos/data/email_template.xml',
        'wizard/wizard_history_creation.xml',
        'wizard/wizard_history_print.xml',
        'views/hr_employee_view.xml',
    ],
    'external_dependencies': {
        'python': [
            'barcode'  # pip install pyBarcode
        ],
    }

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
