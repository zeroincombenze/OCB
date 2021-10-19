# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields


class stock_invoice_onshipping(orm.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    def _get_journal_id(self, cr, uid, context=None):
        selection = super(stock_invoice_onshipping, self)._get_journal_id(cr, uid, context=context)
        if context is None:
            context = {}

        model = context.get('active_model')
        if not model or model != 'stock.picking':
            return []

        journal_obj = self.pool['account.journal']

        res_ids = context and context.get('active_ids', [])
        for pick in self.pool['stock.picking'].browse(cr, uid, res_ids, context=context):
            if not pick.move_lines:
                continue
            src_usage = pick.move_lines[0].location_id.usage
            dest_usage = pick.move_lines[0].location_dest_id.usage

            if pick.type == 'in' and src_usage == 'customer' and dest_usage == 'assets':
                for move_line in pick.move_lines:
                    if move_line.sale_line_id.rentable:
                        rentable = True
                        break
                else:
                    rentable = False
                i = 0
                if rentable:
                    value = journal_obj.search(cr, uid, [('type', '=', 'sale')])
                    for jr_type in journal_obj.browse(cr, uid, value, context=context):
                        rent_journal = jr_type.id, jr_type.name
                        if rent_journal not in selection:
                            # Prepending journal, so it will be first in a list:
                            selection.insert(i, rent_journal)
                            i += 1

        return selection

    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal', required=True)
    }
