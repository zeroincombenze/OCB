# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011 - TODAY Didotech Inc. (<http://www.didotech.com>)
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
##############################################################################
{
    'name': 'Repair Center',
    'version': '4.17.36.38',
    'category': 'Generic Modules/Service',
    'description': """
        This module is a service management module for repair shops or repair depots
        Repair Centre module is for repair shops or repair depots that receive items for repair, and possibly also subcontract out items for repair.
        
        Repair Center handles this scenarios:
        - reception - analysis - confirmation - repair - delivery - invoice - end
        - reception - analysis - confirmation - A invoice - repair - delivery - end
        - reception - waranty repair - delivery - invoice to manufacturer - done
        - repair on-site - invoice - done
        - repair own products - done
        
        Possible improvement (code is disabled)
        - reception - analysis - not repairable, but on warranty - delivery to manufacturer - reception - delivery - done
        
        After installation 'Advance product' and 'Repair Shop' should be setted manualy in Company -> Configuration -> Repair Center
    """,
    'author': 'Deneroteam - Didotech',
    'website': 'http://www.deneroteam.com',
    'depends': [
        'base',
        'mail',
        'sale',
        'purchase',
        'stock',
        'account',
        'product_manufacturer',
        'l10n_it_base',
        'product_extended',
        'product_bom',
        'l10n_it_sale',
        'work_order',
        'material_asset',
        'report_aeroo',
        'core_extended',
        'sale_order_reopen'
    ],
    'data': [
        'security/repair_security.xml',
        "security/ir.model.access.csv",
        'wizard/cancel_repair_view.xml',
        'wizard/not_repairable_view.xml',
        'wizard/repair_set_origin.xml',
        'wizard/repair_set_partner.xml',
        'repair_center_data.xml',
        'repair_center_view.xml',
        'sale_order_data.xml',
        'company_view.xml',
        'repair_center_workflow.xml',
        'sale_validation_workflow.xml',
        'attachment_view.xml',
        'report/report.xml',
        'wizard/repair_invoice_create.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
}
