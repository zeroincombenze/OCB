# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import re

from openerp.osv import orm


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def search(self, cr, uid, domain, offset=0, limit=0, order=None, context=None, count=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if uid != 1 and self.pool['sale.shop'].search(cr, uid, [('pos_user_id', '=', uid)], context=context) and domain and domain[0][0] == 'supplier' and domain[0][1] == '=' and domain[0][2] == 't':
            supplierinfo_obj = self.pool['product.supplierinfo']
            supplierinfo_ids = supplierinfo_obj.search(cr, uid, [], context=context)
            res = supplierinfo_obj.read_group(cr, uid, [('id', 'in', supplierinfo_ids)], ['name'], ['name'], offset=0, limit=None, context=context, orderby='name')
            ids = []
            for supplier in res:
                ids.append(supplier['name'][0])
            return ids
        return super(res_partner, self).search(cr, uid, domain, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = []

        if name:
            ids = self.search(cr, uid, [('name', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                if len(name) == 11:
                    name = 'IT' + name
                ids = self.search(cr, uid, [('vat', '=', name)] + args, limit=limit, context=context)
                if ids:
                    context.update({'find_vat': True})
                if not len(ids) and len(name) == 13:
                    # i search if exist VAT
                    value = self.vat_change(cr, uid, [], name, context) or {}
                    if value.get('value', False):
                        value['value'].update({
                            'vat': name,
                        })
                        if not value.get('value').get('customer', False):
                            value['value'].update({
                                'customer': False,
                            })
                        if context.get('search_default_customer'):
                            value['value'].update({
                                'conto_terzi': True,
                            })

                        ids = [self.create(cr, uid, value.get('value'), context)]
                        # print name
                        # name = self.browse(cr, uid, ids[0], context).name
                        # print name

            if not len(ids):
                ids = self.search(cr, uid, [('property_customer_ref', '=', name)] + args, limit=limit, context=context)
            if not len(ids):
                ids = self.search(cr, uid, [('property_supplier_ref', '=', name)] + args, limit=limit, context=context)

            if not len(ids):

                if len(name) == 1 and operator == 'ilike':
                    operator = '=ilike'
                    name = name + '%'

                ids_1 = self.search(
                    cr, uid, args + [('name', operator, name)], limit=limit, context=context)
                ids_2 = self.search(
                    cr, uid, args + [('vat', operator, name)], limit=limit, context=context)
                ids_3 = self.search(
                    cr, uid, args + [('property_customer_ref', operator, name)], limit=limit, context=context)
                ids_4 = self.search(
                    cr, uid, args + [('property_supplier_ref', operator, name)], limit=limit, context=context)

                ids = ids_1 + ids_2 + ids_3 + ids_4
                ids = list(set(ids))

            if not len(ids):
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(
                        cr, uid, [('name', '=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)

        result = self.name_get(cr, uid, ids, context=context)
        return result
