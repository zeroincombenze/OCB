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
import netsvc


class repair_set_partner(orm.TransientModel):
    _name = 'repair.set.partner'
    _description = 'Set partner'

    _columns = {
        'partner_id': fields.many2one('res.partner', "Customer", required=True),
        'address_invoice_id': fields.many2one("res.partner.address", "Invoice Address", domain="[('partner_id', '=', partner_id)]"),
        'address_contact_id': fields.many2one("res.partner.address", "Main Address", domain="[('partner_id', '=', partner_id)]"),
    }
    
    def _get_default_value(self, cr, uid, field, context=None):
        if context.get('repair_order_id', False):
            repair_order = self.pool['repair.order'].browse(cr, uid, context['repair_order_id'], context)
            if repair_order and repair_order.product_id and repair_order.product_id.manufacturer:
                
                if field == 'partner_id':
                    return repair_order.product_id.manufacturer.id
                else:
                    partner_address = self.pool['res.partner'].address_get(cr, uid, [repair_order.product_id.manufacturer.id], ['default', 'contact', 'invoice'])
                    if field == 'address_contact_id':
                        return partner_address.get('default', False) or partner_address.get('contact', False)
                    elif field == 'address_invoice_id':
                        return partner_address.get('invoice', False) or partner_address.get('default', False) or partner_address.get('contact', False)
        return
    
    _defaults = {
        'partner_id': lambda self, cr, uid, context: self._get_default_value(cr, uid, 'partner_id', context),
        'address_contact_id': lambda self, cr, uid, context: self._get_default_value(cr, uid, 'address_contact_id', context),
        'address_invoice_id': lambda self, cr, uid, context: self._get_default_value(cr, uid, 'address_invoice_id', context),
    }

    def set_partner(self, cr, uid, ids, context=None):
        if context.get('sale_order_id', False):
            wf_service = netsvc.LocalService("workflow")
            
            context['set_partner_id'] = ids[0]
            
            # Create invoice
            self.pool['sale.order'].action_invoice_create(cr, uid, [context['sale_order_id']], context=context)
            wf_service.trg_validate(uid, 'sale.order', context['sale_order_id'], 'manual_invoice', cr)
        
        return {'type': 'ir.actions.act_window_close'}

    def on_change_partner(self, cr, uid, ids, partner_id, context=None):
        if partner_id:
            partner_address = self.pool['res.partner'].address_get(cr, uid, [partner_id], ['default', 'contact', 'invoice'])

            return {'value': {
                'address_contact_id': partner_address.get('default', False) or partner_address.get('contact', False),
                'address_invoice_id': partner_address.get('invoice', False) or partner_address.get('default', False) or partner_address.get('contact', False),
            }}
        else:
            return {'value': {}}
