# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
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


class res_partner_brand(orm.Model):    
    _name = "res.partner.brand"
    _columns = { 
        'name': fields.char('Name', size=64),
        'owner_id': fields.many2one('res.partner', "Owner"),
        'product_ids': fields.one2many("product.product", "brand_id", "Products")
    }
    _order = 'name asc'


