# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Didotech (<http://www.didotech.com>)
#    All Rights Reserved
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

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import netsvc
LOGGER = netsvc.Logger()


class repair_set_origin(orm.TransientModel):
    _name = 'repair.set.origin'
    _description = 'Set origin and date of the product to repair'

    _columns = {
        'origin': fields.char("Origin", size=256, required=False ),
        'date': fields.datetime("Create Date", required=True),
    }
    
    _defaults = {
        'date': lambda self, cr, uid, context: datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    }

    def set_origin(self, cr, uid, ids, context=None):
        origin = self.browse(cr, uid, ids, context=context)[0].origin
        date = self.browse(cr, uid, ids, context=context)[0].date
        
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'repair.order', context['active_id'], 'reception_confirm', cr)
        
        repair_order = self.pool['repair.order'].browse(cr, uid, context['active_id'])
        in_picking_id = repair_order.in_picking_id and repair_order.in_picking_id.id or False
        if in_picking_id:
            self.pool['stock.picking'].write(cr, uid, in_picking_id, {
                'origin': origin,
                'date': date,
                'ddt_in_reference': origin,
                'ddt_in_date': date[0:10]
                })
        return {'type': 'ir.actions.act_window_close'}
