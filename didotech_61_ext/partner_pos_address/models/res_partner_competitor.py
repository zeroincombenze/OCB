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


class res_partner_competitor(orm.Model):
    _name = "res.partner.competitor"
    
    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        if not len(ids):
            return []
        res = []
        for competitor in self.browse(cr, uid, ids, context=context):
            res.append((competitor.id, competitor.partner_id.name))
        return res

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Parnter', required=True),
        'brand_id': fields.many2one('res.partner.brand', 'Brand', required=True),
        'product_category_ids': fields.many2many('product.category', 'res_partner_cometitor_product_category_rel', 'competitor_id', 'category_id', 'Product Categories'),
    }

