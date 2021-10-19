# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools.translate import _

class repair_order_invoice(orm.TransientModel):

    def _get_journal(self, cr, uid, context=None):
        res = self._get_journal_id(cr, uid, context=context)
        if res:
            return res[0][0]
        return False

    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        vals = []
        journal_type = 'sale'
        value = journal_obj.search(cr, uid, [('type', '=',journal_type )])
        for jr_type in journal_obj.browse(cr, uid, value, context=context):
            t1 = jr_type.id,jr_type.name
            if t1 not in vals:
                vals.append(t1)
        return vals

    _name = "repair.order.invoice"
    _description = "Repair Order Invoice"

    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal',required=True),
        'group': fields.boolean("Group by partner"),
        'invoice_date': fields.date('Invoiced date'),
    }

    _defaults = {
        'journal_id' : _get_journal,
    }

    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(repair_order_invoice, self).view_init(cr, uid, fields_list, context=context)
        repair_obj = self.pool['repair.order']
        count = 0
        active_ids = context.get('active_ids',[])
        for repair in repair_obj.browse(cr, uid, active_ids, context=context):
            if repair.state != '2binvoiced':
                count += 1
        if len(active_ids) == 1 and count:
            raise orm.except_orm(_('Warning !'), _('This repair order list does not require invoicing.'))
        if len(active_ids) == count:
            raise orm.except_orm(_('Warning !'), _('None of these repair orders require invoicing.'))
        return res

    def open_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_ids = []
        data_pool = self.pool.get('ir.model.data')
        res = self.create_invoice(cr, uid, ids, context=context)
        invoice_ids += res.values()
        if not invoice_ids:
            raise orm.except_orm(_('Error'), _('No Invoices were created'))
        action_model = False
        action = {}
        action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree1")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
        return action

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        repair_order_obj = self.pool.get('repair.order')
        onshipdata_obj = self.read(cr, uid, ids, ['journal_id', 'group', 'invoice_date'])
        context['date_invoice'] = onshipdata_obj[0]['invoice_date']
#         if context.get('new_picking', False):
#             onshipdata_obj['id'] = onshipdata_obj.new_picking
#             onshipdata_obj[ids] = onshipdata_obj.new_picking
        active_ids = context.get('active_ids', [])
        #active_repair_order = repair_order_obj.browse(cr, uid, context.get('active_id',False), context=context)
        #inv_type = repair_order_obj._get_invoice_type(active_repair_order)
        #context['inv_type'] = inv_type
        #if isinstance(onshipdata_obj[0]['journal_id'], tuple):
        #    onshipdata_obj[0]['journal_id'] = onshipdata_obj[0]['journal_id'][0]
        res = repair_order_obj.action_invoice_create(cr, uid, active_ids,
              #journal_id = onshipdata_obj[0]['journal_id'], #TODO da implementare per miglioramento?
              group = onshipdata_obj[0]['group'],
              context=context)
        return res
