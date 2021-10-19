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


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if not args:
            args = []
        args = args[:]
        if context.get('search_product_id', False):
            sql = """
                select sp.id as supplier from product_product as p
                inner join product_template as t on t.id = p.product_tmpl_id
                left join product_supplierinfo as ps on ps.product_id = t.id
                left join res_partner as sp on sp.id = ps.name
                where p.id = %s
            """ % (str(context.get('search_product_id', 0)))
            cr.execute(sql)
            data = cr.fetchall()
            if data:
                domain = ('id', 'in', [x[0] for x in data])
                args.append(domain)
        return super(res_partner, self).search(
            cr, user, args, offset=offset, limit=limit, order=order, context=context, count=count)

    _defaults = {
        'date': fields.date.context_today,
        'opt_out': True,
    }
