# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
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
    "name": "Rent Product",
    "version": "3.11.42.22",
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    'category': 'Sales Management',
    "description": """
       Module gives possibility to rent a product for a given period.
       
       To make it work you should:
        - create an asset
        - this asset should be in a category which has a connected service product
        - when this service product is added to a sale.order at some point you will be able
          to select an asset from assets of connected category.
          
       Can be incompatible with:
        - sale_layout
        - account_analytic_default
    """,
    "depends": [
        'base',
        'sale',
        'sale_journal',
        'sale_order_confirm',
        'product_bom',
        'material_asset',
        'core_extended',
        'public_holidays',
        'account',
        'sale_margin'
    ],
    "data": [
        'views/sale_order_view.xml',
        'asset_view.xml',
        'company_view.xml',
        'stock_view.xml',
        'wizard/select_asset_view.xml',
        'wizard/confirmation_view.xml',
        # 'wizard/stock_return_picking_view.xml',
        'sale_workflow.xml',
        'security/ir.model.access.csv',
    ],
    "active": False,
    "installable": True,
}
