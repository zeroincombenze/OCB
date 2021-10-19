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


class SMSQueue(orm.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    _columns = {
        'name': fields.text('SMS Request', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'msg': fields.text('SMS Text', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'mobile': fields.char('Mobile No', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Queued'),
            ('sending', 'Waiting'),
            ('send', 'Sent'),
            ('error', 'Error'),
        ], 'Message Status', select=True, readonly=True),
        'error': fields.text('Last Error', size=256, readonly=True, states={'draft': [('readonly', False)]}),
        'create_date': fields.datetime('Date', readonly=True),
    }

    _defaults = {
        # 'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
    }
    
    _order = 'create_date desc'
