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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sale_order_confirm_line(orm.TransientModel):
    _inherit = "sale.order.confirm.line"
    
    _columns = {
        'date_start_rent': fields.date('Rent start date', help='Date of the start of the leasing.'),
        'date_end_rent': fields.date('Rent end date', help='Date of the end of the leasing.'),
    }

    def onchange_date(self, cr, uid, ids, sale_line_id, date_start, date_end):
        # check if product is not already booked for the new period
        asset_rent_period_obj = self.pool['asset.rent.period']
        
        sale_line = self.pool['sale.order.line'].browse(cr, uid, sale_line_id)
        
        rent_period_ids = asset_rent_period_obj.search(cr, uid, [('order_line_id', '=', sale_line_id)])
        period_check = asset_rent_period_obj.check_overbooking(cr, uid, rent_period_ids[0], date_start, date_end)

        # TODO: figure out how to control overbooking
        # if period_check['date_start'] == 'confirmed' or period_check['date_end'] == 'confirmed':
        if period_check['rentable_free'] < 0:
            warning = _(u"'{product}' is not free for this period").format(product=sale_line.product_id.name)
            return {
                'value': {'date_start_rent': sale_line.date_start_rent, 'date_end_rent': sale_line.date_end_rent},
                'warning': {'title': _('Overbooking'), 'message': warning}
            }
        # elif period_check['state_start'] == 'reserved' or period_check['state_end'] == 'reserved':
        elif period_check['rentable_free'] < period_check['rentable_reserved']:
            warning = _(u"'{product}' is already reserved for this period").format(product=sale_line.product_id.name)
            return {
                'value': {},
                'warning': {'title': _('Overbooking'), 'message': warning}
            }
        else:
            return {'value': {}}


class sale_order_confirm(orm.TransientModel):
    _inherit = "sale.order.confirm"
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(sale_order_confirm, self).default_get(cr, uid, fields, context)
        
        for k, confirm_line in enumerate(res['confirm_line']):
            sale_order_line = self.pool['sale.order.line'].browse(cr, uid, confirm_line['sale_line_id'], context)
            
            res['confirm_line'][k].update({
                'date_start_rent': sale_order_line.date_start_rent,
                'date_end_rent': sale_order_line.date_end_rent
            })
            
        return res
    
    def sale_order_confirmated(self, cr, uid, ids, context=None):
        asset_rent_period_obj = self.pool['asset.rent.period']
        
        sale_order_confirm_data = self.browse(cr, uid, ids[0], context)
        for confirm_line in sale_order_confirm_data.confirm_line:
            rent_period_ids = asset_rent_period_obj.search(cr, uid, [('order_line_id', '=', confirm_line.sale_line_id.id)])
            asset_rent_period_obj.write(cr, uid, rent_period_ids, {'date_start': confirm_line.date_start_rent, 'date_end': confirm_line.date_end_rent})
        
        return super(sale_order_confirm, self).sale_order_confirmated(cr, uid, ids, context)
