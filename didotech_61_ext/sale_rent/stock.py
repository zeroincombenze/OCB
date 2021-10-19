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


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _has_rentables(self, cr, uid, ids, field_name, args, context):
        result = {}
        
        for picking_id in ids:
            for stock_move in self.pool['stock.picking'].browse(cr, uid, picking_id, context).move_lines:
                if stock_move.sale_line_id.rentable:
                    result[picking_id] = True
                    break
            else:
                result[picking_id] = False
        return result
    
    _columns = {
        'rentable': fields.function(_has_rentables, method=True, string=_('Can be rented'), type='boolean', store=True),
    }

    def _get_rent_taxes_invoice(self, cr, uid, move_line, type):
        """ Gets taxes on invoice
        @param move_line: Stock move lines
        @param type: Type of invoice
        @return: Taxes Ids for the move line
        """

        taxes = move_line.sale_line_id.product_id.taxes_id

        if move_line.picking_id and move_line.picking_id.address_id and move_line.picking_id.address_id.partner_id:
            return self.pool['account.fiscal.position'].map_tax(
                cr,
                uid,
                move_line.picking_id.address_id.partner_id.property_account_position,
                taxes
            )
        else:
            return map(lambda x: x.id, taxes)

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
                              invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """

        if move_line.sale_line_id \
                and move_line.sale_line_id.product_id \
                and move_line.sale_line_id.product_id.type == 'service' \
                and move_line.sale_line_id.rentable:

            if group and picking.name:
                name = picking.name + '-' + move_line.sale_line_id.name
            else:
                name = move_line.sale_line_id.name
                
            name = "{sale_name} - {name}".format(sale_name=name, name=move_line.product_id.name)

            origin = move_line.picking_id.name or ''
            if move_line.picking_id.origin:
                # Carlo add id of sale.order.line for report
                origin += ':' + move_line.picking_id.origin + ':' + str(move_line.sale_line_id.id)
            
            #account_id = move_line.asset_id.account_income_id and 
            #if not account_id:
            account_id = move_line.asset_id.account_income_id.id or \
                move_line.sale_line_id.product_id.product_tmpl_id.property_account_income.id or \
                move_line.sale_line_id.product_id.categ_id.property_account_income_categ.id

            if invoice_vals['fiscal_position']:
                fp_obj = self.pool['account.fiscal.position']
                fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
                account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)

            # set UoS if it's a sale and the picking doesn't have one
            uos_id = move_line.sale_line_id.product_uos and move_line.product_uos.id or False
            if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
                uos_id = move_line.sale_line_id.product_uom.id

            return {
                'name': name,
                'origin': origin,
                'invoice_id': invoice_id,
                'uos_id': uos_id,
                'product_id': move_line.sale_line_id.product_id.id,
                'account_id': account_id,
                'price_unit': move_line.sale_line_id.price_unit,
                'discount': self._get_discount_invoice(cr, uid, move_line),
                # 'quantity': move_line.sale_line_id.product_uom_qty_2invoice or move_line.sale_line_id.product_uom_qty,
                'quantity': move_line.sale_line_id.product_uom_qty,
                'invoice_line_tax_id': [(6, 0, self._get_rent_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
                'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
            }
        else:
            return super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context)
        
    def _get_invoice_type(self, pick):
        if pick.invoice_state == '2binvoiced' and pick.rentable:
            return 'out_invoice'
        else:
            return super(stock_picking, self)._get_invoice_type(pick)


class stock_move(orm.Model):
    _inherit = 'stock.move'
    
    _columns = {
        # 'product_uom_qty_2invoice': fields.related('sale_line_id', 'product_uom_qty_2invoice', type='float', string=_('Quantity (UoM) to invoice'), store=False),
        'asset_id': fields.many2one('asset.asset', 'Asset', required=False)
        # 'product_id': fields.many2one('product.product', 'Product', required=False, select=True, domain=[('type','<>','service')],states={'done': [('readonly', True)]}),
        # 'asset_category_id': fields.many2one('asset.category', _('Asset Category'))
    }

    # def _check_product_category_required(self, cr, uid, ids, context=None):
    #     if ids and not isinstance(ids, (list, tuple)):
    #         ids = [ids]
    #
    #     for move in self.browse(cr, uid, ids, context):
    #         if not move.product_id and not move.asset_category_id:
    #             return False
    #
    #     return True
    #
    # _constraints = [
    #     (_check_product_category_required, _("At least product_id or asset category can't be empty"), ['asset_category_id', 'product_id'])
    # ]
