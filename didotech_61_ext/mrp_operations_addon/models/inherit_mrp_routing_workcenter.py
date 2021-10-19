# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class MrpRoutingWorkcenter(orm.Model):
    _inherit = 'mrp.routing.workcenter'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
    }
