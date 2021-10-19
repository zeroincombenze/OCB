# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class res_company(orm.Model):
    _inherit = "res.company"

    def _getDefaultShop(self, cr, uid, context=None):
        sale_shop_obj = self.pool['sale.shop']
        sale_shop_ids = sale_shop_obj.search(cr, uid, [], context=context)
        if sale_shop_ids:
            return sale_shop_ids[0]
        else:
            return False

    _columns = {
        'property_repair_product_id': fields.property(
            'product.product',
            type='many2one',
            relation="product.product",
            string="Repair Generic Product",
            method=True,
            view_load=True,
        ),
        'repair_shop_id': fields.many2one('sale.shop', 'Shop', required=True),
        'advance_product_id': fields.property(
            'product.product',
            type='many2one',
            relation="product.product",
            string="Repair Advance Product",
            method=True,
            view_load=True,
            help=_('A product to be used in advance invoice')
        ),
        'repair_location_id': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string='Stock Location',
            method=True,
            required=True,
            help=_('A location of a product during repair')
        ),
        'group_service_line': fields.boolean('Group Service Line'),
        'update_service': fields.boolean('Update Service from Timesheet'),
        'auto_exit_product': fields.boolean('Auto Exit Picking'),
        'skip_quotation_on_onsite': fields.boolean('Skip Quotation'),

    }

    _defaults = {
        'repair_shop_id': _getDefaultShop,
        'update_service': True,
        'auto_exit_product': True,
    }