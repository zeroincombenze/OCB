# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
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
    'name': "Intrastat",
    'version': '2.1.3.3',
    'category': 'Accounting & Finance',
    'description': """
Intrastat
====================================

    """,
    'author': 'ISA srl - Akretion - Didotech srl',
    'website': 'http://www.didotech.com',
    'depends' : ['base',
                 'l10n_it_base',
                 'account',
                 'l10n_it_account',
                 'l10n_it_vat_registries',
                 'purchase',
                 'sale',
                 'stock',                 #'l10n_it_base',                 #'intrastat_base',
                 ],
    'data': [
              'security/ir.model.access.csv',
              'security/intrastat_group.xml',
              'cee/account_cee_tables_view.xml',
              'cee/account_view.xml',
              'product/product_product_view.xml',
              'res/res_company_view.xml',
              'res/res_partner_view.xml',
              'invoice/account_invoice_line_view.xml',
              'purchase/purchase_view.xml',
              'sale/sale_view.xml',
              'stock_picking/stock_picking_view.xml',
      ],
    'init_xml': [
              'data/account.cee.combined.nomenclature.csv',
              'data/account.cee.service.codes.csv',
              'data/account.cee.nat.of.trans.csv',
              'data/account.cee.way.of.freight.csv',
              'data/account.cee.payment.methods.csv',
    ],
    'demo': [],
    'test': [
             'test/invoice.yml',
    ],
    'active': False,
    'installable': True
}
