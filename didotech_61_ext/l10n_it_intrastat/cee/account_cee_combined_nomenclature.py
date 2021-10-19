# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, orm

class account_cee_combined_nomenclature(orm.Model):

    _name = "account.cee.combined.nomenclature"

    _columns = {
        'code_number': fields.integer('Code Number',
                                    required=True),
        'add_entry': fields.char('Additional Entry', size=64),
        'description': fields.text('Description',
                                    required=True),
        }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for item in self.browse(cr, uid, ids, context=context):
            item_desc = (str(item.code_number) or '') + ' - ' + (item.description or '')
            res.append((item.id, item_desc))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                                                context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}

        # Cast name into an integer and search against one code
        # use the standard string otherwise
        try:
            code = int(name)
            req_ids = self.search(cr, uid, args + 
                                  [('code_number', '=', code),],
                                  limit=limit,
                                  context=context)
        except ValueError:
            req_ids = self.search(cr, uid, args + 
                                  [('description', operator, name),],
                                  limit=limit,
                                  context=context)

        return self.name_get(cr, uid, req_ids, context=context)
