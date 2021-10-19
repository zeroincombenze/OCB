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


class Properties(orm.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    _columns = {
        'name': fields.char('Property name', size=256, required=True, help='Name of the property whom appear on the URL'),
        'value': fields.char('Property value', size=256, required=True, help='Value associate on the property for the URL'),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway'),
        'type': fields.selection([
            ('user', 'User'),
            ('password', 'Password'),
            ('sender', 'Sender Name'),
            ('to', 'Recipient No'),
            ('sms', 'SMS Message')
        ], 'API Method', select=True, help='If parameter concern a value to substitute, indicate it'),
    }
