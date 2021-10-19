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

import netsvc
wf_service = netsvc.LocalService("workflow")


class SelectRentAsset(orm.TransientModel):
    _name = 'select.rent.asset'
    
    _columns = {
        'name': fields.char(_('Asset code'), size=128),
        'rent_line_ids': fields.one2many('select.rent.lines', 'select_rent_asset_id', string=_('Rent Lines')),
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'partner_id': fields.related('order_id', 'partner_id', type='many2one', relation='res.partner', string="Partner", store=False),
    }
    
    def reserve_asset(self, cr, uid, select_rent_ids, context=None):
        if context is None:
            context = {}
        
        rent_period_obj = self.pool['asset.rent.period']

        asset_location_property_obj = self.pool['asset.location.property']

        source_location_property = asset_location_property_obj.get_location(cr, uid, 'asset.asset')
        if source_location_property and source_location_property.stock_location:
            source_location_id = source_location_property.stock_location.id
        else:
            raise orm.except_orm(_('Warning'), _('Please set asset main location (Asset/Configuration/Asset Location)'))

        dest_location_property = asset_location_property_obj.get_location(cr, uid, 'res.partner')
        if dest_location_property and dest_location_property.stock_location:
            dest_location_id = dest_location_property.stock_location.id
        else:
            raise orm.except_orm(_('Warning'), _('Please set asset Partner (Customer) location (Asset/Configuration/Asset Location)'))

        picking_lines = []

        select_rent_asset = self.browse(cr, uid, select_rent_ids[0])

        for line in select_rent_asset.rent_line_ids:
            picking_lines.append({
                # 'name': rent_period.asset_id.asset_product_id.product_product_id.name_get()[0][1],
                'name': line.name,
                'origin': select_rent_asset.order_id.name,
                'address_id': select_rent_asset.order_id.partner_shipping_id.id,
                'product_id': line.asset_id.asset_product_id.product_product_id.id,
                'product_qty': 1,
                'product_uom': line.asset_id.asset_product_id.uom_id.id,
                'date_expected': line.date_start,
                'date': line.date_start,
                'prodlot_id': line.asset_id.serial_number.id,  # Serial number
                'location_id': source_location_id,  # Source location
                'location_dest_id': dest_location_id,  # Destination location (9 - customer)
                'partner_id': select_rent_asset.order_id.partner_id.id,
                'sale_line_id': line.sale_line_id.id
            })
            #self.pool['sale.order.line'].write(cr, uid, line.id, {'product_uom_qty_2invoice': line.product_uom_qty})

        if picking_lines:
            # Create stock.picking
            picking_id = self.pool['stock.picking'].create(cr, uid, {
                'origin': select_rent_asset.order_id.name,
                'address_id': select_rent_asset.order_id.partner_shipping_id.id,
                'date': line.date_start,
                'min_date': line.date_start,
                'max_date': line.date_end,
                'location_id': source_location_id,  # Source location
                'location_dest_id': dest_location_id,  # Destination location (9 - customer)
                'partner_id': select_rent_asset.order_id.partner_id.id,
                'move_type': 'direct',
                'auto_picking': False,
                'type': 'out',
                'sale_id': select_rent_asset.order_id.id,
                'number_of_packages': 0,
                'move_lines': [(0, False, line) for line in picking_lines],
                'invoice_state': 'none',
                'stock_journal_id': source_location_property.stock_location.chained_journal_id and source_location_property.stock_location.chained_journal_id.id or False
            })

            self.pool['stock.picking'].draft_validate(cr, uid, [picking_id], context)

        wf_service.trg_validate(uid, 'sale.order', select_rent_asset.order_id.id, 'rent_selected', cr)

        return {'type': 'ir.actions.act_window_close'}
    
    
class SelectRentLines(orm.TransientModel):
    _name = 'select.rent.lines'
        
    _columns = {
        'name': fields.char(_('Description'), size=128),
        'complete_name': fields.char(_('Description'), size=128),
        'sale_line_id': fields.many2one('sale.order.line', _('Sale Order Line')),
        'asset_id': fields.many2one('asset.asset', _('Asset')),
        'free_asset_ids': fields.many2many('asset.asset', string='Assets'),
        'date_start': fields.related('sale_line_id', 'date_start_rent', type='date', store=False, string=_('Start')),
        'date_end': fields.related('sale_line_id', 'date_end_rent', type='date', store=False, string=_('End')),
        'select_rent_asset_id': fields.many2one('select.rent.asset')
    }
