# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011-2012 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011-2013 Didotech Inc. (<http://www.didotech.com>)
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


from openerp.osv import orm, fields
import re


class product_template(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'name': fields.char('Name', size=128, required=True, translate=False, select=True),
        'description': fields.text('Description', translate=False),
        'description_purchase': fields.text('Purchase Description', translate=False),
        'description_sale': fields.text('Sale Description', translate=False),
    }


class product_product(orm.Model):
    _inherit = 'product.product'

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        limit = 100
        if not args:
            args = []

        if name:
            for column in ('default_code', 'ean13', 'manufacturer_pref'):
                ids = self.search(cr, user, [(column, '=', name)] + args, limit=limit, context=context)
                if ids:
                    break

            if not len(ids):
                if len(name) == 1 and operator == 'ilike':
                    operator = '=ilike'
                    name = name + '%'

                domain = [
                        '|', '|', '|',
                        ('default_code', operator, name),
                        ('name', operator, name),
                        ('manufacturer_pref', operator, name),
                        ('manufacturer_pname', operator, name)
                    ]

                if 'supplier_code' in self._columns:
                    domain = ['|'] + domain + [('supplier_code', operator, name)]

                ids = self.search(cr, user, args + domain, limit=limit, context=context)

            if not len(ids):
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(
                        cr, user, [('default_code', '=', res.group(2))] + args, limit=limit, context=context)
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

        return super(product_product, self).search(
            cr, uid, new_args, offset=offset, limit=limit, order=order, context=context, count=count)
