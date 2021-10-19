# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2017
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

class res_partner_attendence(orm.Model):
    _name = "res.partner.attendence"
    _rec_name = "dayofweek"
    _description = "Work Detail"
    _columns = {
        'dayofweek': fields.selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], 'Day of week'),
        'hour_from': fields.float('Work from', size=8, required=True, help="Working time will start from"),
        'hour_to': fields.float("Work to", size=8, required=True, help="Working time will end at"),
        'address_id': fields.many2one('res.partner.address', "Address"),
    }
    _order = 'dayofweek, hour_from'
