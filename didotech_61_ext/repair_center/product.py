# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech Inc. (<http://www.didotech.com>)
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


class product_product(orm.Model):
    _inherit = 'product.product'
    
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        if context and (context.get('model', False) == 'repair.order' and not context.get('all_products', True) and context.get('customer_id', False)):
            product_ids = self.pool['repair.order'].get_customer_products(cr, uid, context['customer_id'], context)
            product_ids += self.pool['stock.move'].get_customer_products(cr, uid, context['customer_id'], context)
            product_ids += self.pool['account.invoice.line'].get_customer_products(cr, uid, context['customer_id'], context)

            if product_ids:
                product_ids = list(set(product_ids))
                args.append(['id', 'in', product_ids])
        
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)


class product_accessory(orm.Model):
    _name = 'product.accessory'
    _description = 'Product Accessory'
    _columns = {
        'name': fields.char("Accessory", size=64, required=True),
    }

    _order = "name"


class product_condition(orm.Model):
    _name = 'product.condition'
    _description = 'Product Condition'
    _columns = {
        'name': fields.char("Name", size=64, required=True),
    }
    _order = "name"

