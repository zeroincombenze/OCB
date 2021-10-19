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


class res_partner(orm.Model):    
    _inherit = "res.partner"
    _columns = { 
        'banner_ids': fields.many2many('res.partner.banner', 'res_partner_res_parner_banner_rel', 'banner_id', 'group_id', 'Banners'),
        'competitor_ids': fields.many2many('res.partner.competitor', 'res_partner_res_partner_cometitor_rel', 'partner_id', 'competitor_id', 'Competitors'),
        'brand_ids': fields.one2many("res.partner.brand", "owner_id", "Product Brands"),
        'address': fields.one2many('res.partner.address', 'partner_id', 'Contacts', domain=[('type', '!=', 'pos')]),
        'pos_address': fields.one2many('res.partner.address', 'partner_id', 'POS Address', domain=[('type', '=', 'pos')]),
        'pos_codes': fields.one2many('partner.pos.code', 'partner_id', 'POS Codes'),
        'agent_codes': fields.one2many('partner.agent.code', 'partner_id', 'Partner')
    }
