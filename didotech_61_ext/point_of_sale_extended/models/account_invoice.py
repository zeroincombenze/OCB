# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Didotech SRL
#
#                          All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'payment_journal_id': fields.many2one('account.journal', 'Payment Journal', readonly=True, states={'draft': [('readonly', False)]}, ),
    }

    def onchange_pos_partner_id(self, cr, uid, ids, type, partner_id,
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):

        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,
            date_invoice, payment_term, partner_bank_id, company_id)
        result['value'].update({'move_products': True})

        shop_ids = self.pool['sale.shop'].search(cr, uid, [('pos_user_id', '=', uid)])
        if shop_ids:
            shop = self.pool['sale.shop'].browse(cr, uid, shop_ids)[0]
            result['value'].update({'location_id': shop.warehouse_id and shop.warehouse_id.lot_stock_id.id or False})

        return result

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids:
            return []
        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_partner_id': inv.partner_id.id,
                'default_amount': inv.residual,
                'default_name': inv.name,
                'close_after_process': True,
                'invoice_type': inv.type,
                'default_type': inv.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice', 'out_refund') and 'receipt' or 'payment',
                'journal_id': inv.payment_journal_id and inv.payment_journal_id.id or False,
            }
        }
