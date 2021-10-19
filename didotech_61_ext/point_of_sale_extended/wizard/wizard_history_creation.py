# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import time

from openerp.osv import orm, fields
from openerp.tools.translate import _


class PosHistoryCreation(orm.TransientModel):
    _name = "pos.history.creation"

    def _get_shop(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        return self.pool['pos.order']._default_shop(cr, uid, context)

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, domain=[('pos_user_id', '!=', False)]),
        'date': fields.date('Date', required=True),
    }

    _defaults = {
        'shop_id': _get_shop,
        'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def confirm(self, cr, uid, ids, context=None):
        pos_order_obj = self.pool['pos.order']
        pos_history_obj = self.pool['pos.history']
        bank_statement_obj = self.pool['account.bank.statement']
        for wizard in self.browse(cr, uid, ids, context):
            from_date = '{} 00:00:00'.format(wizard.date)
            to_date = '{} 23:59:59'.format(wizard.date)

            pos_order_domain = self.pool['pos.history']._get_domain(from_date, to_date)
            pos_order_domain.append(('shop_id', '=', wizard.shop_id.id))

            pos_order_ids = pos_order_obj.search(cr, uid, pos_order_domain, context=context)

            history_ids = pos_history_obj.search(cr, uid, [('date', '=', wizard.date), ('shop_id', '=', wizard.shop_id.id), ('state', '=', 'draft')], context=context)
            if history_ids:
                pos_order_obj.write(cr, uid, pos_order_ids, {'history_id': history_ids[0]}, context=context)
            else:
                history_vals = {
                    'date': wizard.date,
                    'pos_order_ids': [(6, 0, pos_order_ids)],
                    'company_id': 1,
                    'shop_id': wizard.shop_id.id
                }
                history_ids = pos_history_obj.create(cr, uid, history_vals, context=context)
                history_ids = [history_ids]

            bank_statement_ids = bank_statement_obj.search(cr, uid, [('journal_id.journal_user', '=', wizard.shop_id.pos_user_id.id), ('date', '=', wizard.date), ('state', '!=', 'done')], context=context)
            if bank_statement_ids:
                bank_statement_obj.write(cr, uid, bank_statement_ids, {'history_id': history_ids[0]}, context)

        return {
            'name': _('Pos History'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.history',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': history_ids[0],
        }


