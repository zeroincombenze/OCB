# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011-2012 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011-2018 Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################.

{
    'name': 'Standard Base company',
    'version': '2.0.2.5',
    'category': 'Profile Standard Service Company - for OpenErp 6.1',
    'description': """
        A profile module to manage standard company profile.
    """,
    'author': 'Didotech Srl',
    'website': 'http://www.didotech.com',
    'depends': [
        'base_vat_unique',
        'crm',
        'crm_lead_correct',
        'l10n_it_base',
        'l10n_it_sale',
        'l10n_it_sale_report',
        'l10n_it_account_report',
        'l10n_it_vat_registries',
        'account_accountant',
        'invoice_proforma',
        'account_vat_period_end_statement',
        'account_invoice_template',
        'purchase_requisition',
        'purchase_requisition_extended',
        'product_manufacturer',
        'stock',
        'stock_picking_extended',
        'dt_product_serial',
        'delivery',
        'report_aeroo',
        # 'report_aeroo_ooo',
        # 'product_catalog_extend',
        'account_voucher',
        'account_invoice_entry_date',
        'partner_subaccount',
        'product_filter_availability_ext_isa',
        'product_code_category',
        'mail',
        'base_ordered',
        'email_extended',
        'dt_avanzosc_product_category_ext',
        'account_due_list',
        'massive_category_change',
        'massive_price_change',
        'sale_order_confirm',
        'web_theme',
        'c2c_sequence_fy',
        'account_fiscal_year_closing',
        'account_invoice_force_number',
        'purchase_no_gap',
        'purchase_order_reopen',
        'sale_order_reopen',
        'stock_picking_reopen',
        'partner_blacklist',
        'module_version',
        'product_price_history',
        'db_backup_ept',
        'account_no_dashboard',
        'admin_no_dashboard',
        'purchase_no_dashboard',
        'sale_no_dashboard',
        'stock_no_dashboard',
        'l10n_base_data_it',
        'base_action_rule_triggers',
        'dt_product_pricelist_fixed_price',
        'account_invoice_filter',
        'stock_picking_filter',
        'sale_order_filter',
        'account_financial_report_webkit',
        'report_webkit_lib',
        'stock_move_extended',
        'account_invoice_extended',
        'account_bank',
        'purchase_discount'
    ],
    'external_dependancies': {
        'bin': [
            'postfix'
        ]
    },
        
    'data': [
        'security/ir.model.access.csv',
        'ir_attachment_view.xml',
        'email_data_template.xml',
        'goods_description_data.xml', # carlo per avere i termini del magazzino in italiano
        'crm_lead_data.xml', # carlo per avere i termi del crm in italiano
        'sale_data.xml',
        'product_view.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': True,
}
