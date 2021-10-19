# -*- coding: utf-8 -*-

from openerp.osv import fields
from openerp.osv import orm


class account_fiscal_position(orm.Model):
    _inherit = 'account.fiscal.position'

    _columns = {
        'virtual_stamp': fields.boolean('Virtual Stamp'),
        'stamp_amount': fields.float('Stamp Amount'),
        'fattura_pa': fields.boolean('Fattura PA')
    }

