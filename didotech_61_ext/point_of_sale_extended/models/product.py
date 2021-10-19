# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Didotech SRL. (<http://www.didotech.com>)
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
##############################################################################.

import re

from openerp.osv import orm


class product_category(orm.Model):
    _inherit = 'product.category'

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if uid != 1 and self.pool['sale.shop'].search(cr, uid, [('pos_user_id', '=', uid)], context=context):
            product_obj = self.pool['product.product']
            product_ids = product_obj.search(cr, uid, [('available_in_pos', '=', True)], context=context)
            if not product_ids:
                product_ids = []

            res = product_obj.read_group(cr, uid, [('id', 'in', product_ids)], ['categ_id'], ['categ_id'], offset=0, limit=None, context=context, orderby='name')
            ids = []
            # cr.execute("SELECT categ_id FROM product_template WHERE id IN ({product_ids}) GROUP BY categ_id".format(product_ids=', '.join([str(product_id) for product_id in product_ids])))
            # cr.fetchall()
            for category in res:
                ids.append(category['categ_id'][0])
            return ids
        return super(product_category, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)


class product_product(orm.Model):
    _inherit = 'product.product'

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        limit = 100
        if not args:
            args = []
        ids = []
        if name:
            name = name[0].replace('@', '') + name[1:len(name)]  # for same barcode reader that add @ on start
            ids = self.search(cr, user, [('default_code', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('ean13', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, user, [('name', '=', name)] + args, limit=limit, context=context)
            if not len(ids):

                if len(name) == 1 and operator == 'ilike':
                    operator = '=ilike'
                    name = name + '%'

                ids_1 = self.search(
                    cr, user, args + [('name', operator, name)], limit=limit, context=context)
                ids_2 = self.search(
                    cr, user, args + [('default_code', operator, name)], limit=limit, context=context)
                ids_3 = self.search(
                    cr, user, args + [('ean13', operator, name)], limit=limit, context=context)

                ids = ids_1 + ids_2 + ids_3
                ids = list(set(ids))
            if not len(ids):
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('default_code', '=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        new_args = []
        for arg in args:
            if len(arg) == 3 and arg[1] == 'ilike':
                new_args.append((arg[0], 'ilike', arg[2].replace(' ', '%')))
            else:
                new_args.append(arg)

        product_ids = super(product_product, self).search(cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
        if len(new_args) == 2:
            shop_ids = self.pool['sale.shop'].search(cr, uid, [('pos_user_id', '=', uid), (['transfert_product_id', '!=', False])])
            if shop_ids:
                sale_shop = self.pool['sale.shop'].browse(cr, uid, shop_ids, context)[0]
                transfert_product_id = sale_shop.transfert_product_id.id
                if transfert_product_id in product_ids:
                    product_ids.remove(transfert_product_id)
        return product_ids

    # # BIG FIX ON IPAD, in pratica da sbagliato i valori dei prezzi
    # def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     if context is None:
    #         context = {}
    #     product_datas = []
    #     if uid != 1 and self.pool['sale.shop'].search(cr, uid, [('pos_user_id', '=', uid)], context=context) and context.get('pricelist', False):
    #         fields_intersection = set(['name', 'price', 'standard_price', 'cost_price', 'list_price']).intersection(set(fields))
    #         if fields_intersection and not self.pool['product.pricelist'].browse(cr, uid, context.get('pricelist'), context).visible_discount:
    #             # fields_intersection = list(fields_intersection)
    #             for product_data in super(product_product, self).read(cr, uid, ids, fields=fields, context=context, load=load):
    #                 if isinstance(product_data, dict) and product_data.get('price', False):
    #                     product_data.update({
    #                         'name': product_data.get('name').replace('"', "''"),
    #                         'cost_price': product_data.get('price'),
    #                         'standard_price': product_data.get('price'),
    #                         'list_price': product_data.get('price'),
    #                     })
    #                 if isinstance(product_data, dict) and product_data.get('name', False):
    #                     product_data.update({
    #                         'name': product_data.get('name').replace('"', " ").replace("'", " "),
    #                     })
    #                 product_datas.append(product_data)
    #
    #     if not product_datas:
    #         # product_datas = super(product_product, self).read(cr, uid, ids, fields=fields, context=context, load=load)
    #         for product_data in super(product_product, self).read(cr, uid, ids, fields=fields, context=context, load=load):
    #             if isinstance(product_data, dict) and product_data.get('name', False):
    #                 product_data.update({
    #                     'name': product_data.get('name').replace('"', " ").replace("'", " "),
    #                 })
    #             product_datas.append(product_data)
    #
    #     return product_datas

