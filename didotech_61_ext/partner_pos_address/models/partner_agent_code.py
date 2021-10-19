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


class partner_agent_code(orm.Model):
    _name = "partner.agent.code"
    _columns = {
        'agent_id': fields.many2one('res.partner.address', "Agent", required=True),
        'partner_id': fields.many2one('res.partner', "Customer", required=True, domain=[('customer', '=', True)]),
        'brand_id': fields.many2one("res.partner.brand", "Brand", domain="[('owner_id','=', partner_id)]"),
        #'partner_agent_id' : fields.many2one('res.partner',"Agent", required=True),
        'partner_agent_id': fields.many2one("res.partner.contact", "Agente", domain="[('partner_id', '=', partner_id)]"),
    }
