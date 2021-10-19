# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class MrpWorkcenter(orm.Model):
    _inherit = 'mrp.workcenter'

    _order = "resource_id"

    _columns = {
        'user_ids': fields.many2many('res.users', string='Users')
    }
