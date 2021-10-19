# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Orders Barcode
#    Copyright (C) 2016 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#    $Id$
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


class mrp_production_workcenter_line(orm.Model):
    _name = "mrp.production.workcenter.line"
    _inherit = "mrp.production.workcenter.line"

    _columns = {
        'opbcode': fields.char('Operation BarCode', size=13),
    }

##################################################################################################################
#                   Overridden original functions and methods
##################################################################################################################

    def create(self, cr, uid, vals, context=None):
        """
            Adds operation code, from Sequence, to be used with fixed length barcode.
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        newname = ''
        objSequence = self.pool['ir.sequence']
        sequenceids = objSequence.search(cr, uid, [('code', '=', 'mrp.production.workcenter.line')], context=context)
        for sequenceid in sequenceids:
            newname = objSequence.get_id(cr, uid, sequenceid, 'id', context)
            break
        vals['opbcode'] = newname
        return super(mrp_production_workcenter_line, self).create(cr, uid, vals, context)
