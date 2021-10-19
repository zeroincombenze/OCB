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
import decimal_precision as dp


# class stock_return_picking_memory(orm.TransientModel):
#     _inherit = "stock.return.picking.memory"
#
#     _columns = {
#         'product_uom_qty_2invoice': fields.float('Quantity (UoM) to invoice', digits_compute=dp.get_precision('Product UoS'), required=True, readonly=False),
#     }
    
    
class stock_return_picking(orm.TransientModel):
    _inherit = 'stock.return.picking'
    
    def default_get(self, cr, uid, fields, context=None):
        """
         To get default values for the object.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param fields: List of fields for which we want default values
         @param context: A standard dictionary
         @return: A dictionary with default values for all field in ``fields``
        """
        
        defaults = super(stock_return_picking, self).default_get(cr, uid, fields, context=context)

        if context.get('active_id', False):
            stock_picking = self.pool['stock.picking'].browse(cr, uid, context['active_id'], context)
            if stock_picking.rentable:
                defaults['invoice_state'] = '2binvoiced'
        
        if defaults.get('product_return_moves', False):
            for move in defaults['product_return_moves']:
                stock_move = self.pool['stock.move'].browse(cr, uid, move['move_id'], context)
                # move['product_uom_qty_2invoice'] = stock_move.sale_line_id.product_uom_qty_2invoice
        
        return defaults

    # def create_returns(self, cr, uid, ids, context=None):
    #     data = self.browse(cr, uid, ids[0], context=context)
    #     for return_move in data.product_return_moves:
    #         self.pool['sale.order.line'].write(cr, uid, return_move.move_id.sale_line_id.id, {'product_uom_qty_2invoice': return_move.product_uom_qty_2invoice})
    #
    #     return super(stock_return_picking, self).create_returns(cr, uid, ids, context=context)
