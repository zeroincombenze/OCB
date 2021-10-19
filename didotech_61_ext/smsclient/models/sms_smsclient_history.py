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


class HistoryLine(orm.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    _columns = {
        'name': fields.char('Description', size=160, required=True, readonly=True),
        'create_date': fields.datetime('Creation Date', readonly=True, select=True),
        # 'date_create': fields.datetime('Date', readonly=True),
        'user_id': fields.many2one('res.users', 'Username', readonly=True, select=True),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway', ondelete='set null', required=True),
        'to': fields.char('Mobile No', size=15, readonly=True),
        'sms': fields.text('SMS', size=160, readonly=True),
    }

    # _defaults = {
    #     'date_create': lambda *a: fields.date.context_today,
    #     'user_id': lambda obj, cr, uid, context: uid,
    # }

    # def create(self, cr, uid, vals, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #
    #     res = super(HistoryLine, self).create(cr, uid, vals, context=context)
    #     cr.commit()
    #     return res

