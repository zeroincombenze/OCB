import time
import hashlib
from openerp.osv import orm, fields
from openerp.tools.translate import _


class PosMakePayment(orm.TransientModel):
    _inherit = 'pos.make.payment'

    _columns = {
        'hashcode': fields.char('Hashcode', size=128),
    }

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'payment_date' in vals and 'amount' in vals:
            key = u'{}_{}_{}'.format(uid, vals['payment_date'], vals['amount'])
            hash_key = hashlib.sha224(key.encode('utf8')).hexdigest()
            payment_ids = self.search(cr, uid, [('hashcode', '=', hash_key)], context=context, limit=1)
            if payment_ids:
                return payment_ids[0]
            vals['hashcode'] = hash_key
        return super(PosMakePayment, self).create(cr, uid, vals, context)
