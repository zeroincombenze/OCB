# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Didotech SRL
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


class hr_contractor_phone(orm.Model):
    _name = 'hr.contractor.phone'
    _rec_name = "type"

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for contractor_phone in self.browse(cr, uid, ids, context=context):
            name = u'{0}: {1}'.format(contractor_phone.type, contractor_phone.number)
            res.append((contractor_phone.id, name))
        return res

    _columns = {
        'type': fields.selection([('phone', 'Phone'), ('mobile', 'Mobile')], "Type"),
        'number': fields.char("Number", size=16),
        'contractor_id': fields.many2one("hr.contractor", "Contractor"),
    }

