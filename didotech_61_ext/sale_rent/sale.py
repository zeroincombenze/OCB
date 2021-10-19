# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013-2014
#    Didotech srl
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

from openerp.osv import orm
from openerp.tools.translate import _


class sale_advance_payment_inv(orm.TransientModel):
    _inherit = "sale.advance.payment.inv"
    
    # Update reference with more information on order linked to advance invoice
    def create_invoices(self, cr, uid, ids, context=None):
        res = super(sale_advance_payment_inv, self).create_invoices(cr, uid, ids, context)
        obj_sale = self.pool['sale.order']
        inv_obj = self.pool['account.invoice']
        ctx = res['context']
        list_inv = ctx['invoice_id']
        for sale_adv_obj in self.browse(cr, uid, ids, context=context):
            for sale in obj_sale.browse(cr, uid, context.get('active_ids', []), context=context):
                ref = ''
                for sale_ol in sale.order_line:
                    if sale_ol.asset_id:
                        ref += _(' - Ref. {0}').format(sale_ol.asset_id.complete_name)
        for inv in inv_obj.browse(cr, uid, list_inv):
            for inv_line in inv.invoice_line:
                name = inv_line.name + ref
                inv_line.write({'name': name})
        return res