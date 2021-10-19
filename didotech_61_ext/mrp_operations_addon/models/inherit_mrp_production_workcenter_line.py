# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Operations Enhancement
#    Copyright (C) 2016 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#    $Id$
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
from datetime import datetime

import netsvc
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _

PRIORITY_TYPE_SELECTION = [('0', 'Not urgent'), ('1', 'Normal'), ('2', 'Urgent'), ('3', 'Very Urgent')]


class mrp_production_workcenter_line(orm.Model):
    _inherit = "mrp.production.workcenter.line"
    _order = 'priority desc, production_id, sequence'

    def name_get(self, cr, uid, ids, context=None):

        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        if not len(ids):
            return []
        res = super(mrp_production_workcenter_line, self).name_get(cr, uid, ids, context)

        if context.get('view_full_name'):
            res = []
            for line in self.browse(cr, uid, ids, context):
                if line.production_id:
                    name = u'[{code}] {name}'.format(code=line.production_id.name, name=line.name)
                else:
                    name = line.name
                res.append((line.id, name))

        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context['view_full_name'] = True
        workcenter_lines = super(mrp_production_workcenter_line, self).name_search(cr, uid, name, args, operator, context=context, limit=limit)
        if name:
            production_ids = self.pool['mrp.production'].search(cr, uid, [('name', 'ilike', name)], context=context)
            if production_ids:
                if args:
                    relative_workcenter_lines = self.name_search(cr, uid, '', args + [('production_id', 'in', production_ids)], operator, context=context, limit=limit)
                else:
                    relative_workcenter_lines = self.name_search(cr, uid, '', [('production_id', 'in', production_ids)], operator, context=context, limit=limit)
                if relative_workcenter_lines:
                    workcenter_lines = list(set(workcenter_lines + relative_workcenter_lines))
        # Sort by
        return sorted(workcenter_lines, key=lambda x: x[1])

    #     def _get_newdate_end(self, cr, uid, ids, field_name, arg, context=None):
    #         """ Finds ending date.
    #         @return: Dictionary of values.
    #         """
    #         ops = self.browse(cr, uid, ids, context=context)
    #         date_and_hours_by_cal = [(op.date_planned, op.hour, op.workcenter_id.calendar_id.id) for op in ops if op.date_planned]
    #
    #         intervals = self.pool.get('resource.calendar').interval_get_multi(cr, uid, date_and_hours_by_cal)
    #
    #         res = {}
    #         for op in ops:
    #             res[op.id] = False
    #             if op.date_planned:
    #                 i = intervals.get((op.date_planned, op.hour, op.workcenter_id.calendar_id.id))
    #                 if i:
    #                     res[op.id] = i[-1][1].strftime('%Y-%m-%d %H:%M:%S')
    #                 else:
    #                     res[op.id] = op.date_planned

    def _get_mrp_production(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for production in self.pool['mrp.production'].browse(cr, uid, ids, context=context):
            mrp_production_workcenter_line_ids = self.pool['mrp.production.workcenter.line'].search(cr, uid, [('production_id', '=', production.id)], context=context)
            for workcenter_id in mrp_production_workcenter_line_ids:
                result[workcenter_id] = True
        return result.keys()

    def _get_delay_from_operation(self, cr, uid, ids, name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for work_order in self.browse(cr, uid, ids, context):
            delay = 0
            for operation in work_order.operation_fractions_ids:
                delay += operation.working_time
            result[work_order.id] = delay

        return result

    def _get_production_qty(self, cr, uid, ids, name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for work_order in self.browse(cr, uid, ids, context):
            production_qty = 0
            for operation in work_order.operation_fractions_ids:
                production_qty += operation.production_qty
            result[work_order.id] = production_qty

        return result

    _columns = {
        'name': fields.char('Work Order', size=256, required=True),
        #         'date_planned_end': fields.function(_get_newdate_end, string='End Date', type='datetime'),
        'product': fields.related('production_id', 'product_id', type='many2one', relation='product.product', string='Product', readonly=True, store=True),
        'cycle': fields.float('Nbr of cycles'),
        'hour': fields.float('Nbr of hours'),
        'operation_fractions_ids': fields.one2many('mrp.fraction_operations', 'order_id', 'Fractions of operation.'),
        'sale_id': fields.related('production_id', 'sale_id', type="many2one", relation='sale.order', string='Sale Order'),
        'partner_id': fields.related('production_id', 'sale_id', 'partner_id', type="many2one", relation='res.partner', string='Partner'),
        'user_id': fields.many2one('res.users', string="User"),
        'priority': fields.related('production_id', 'priority', type="selection", selection=PRIORITY_TYPE_SELECTION, string='Priority', store={
            'mrp.production.workcenter.line': (lambda self, cr, uid, ids, c={}: ids, ['production_id'], 20),
            'mrp.production': (_get_mrp_production, ['priority'], 20),
        }),
        'color': fields.integer('Color Index'),
        'kanban_state': fields.selection([('normal', 'Normal'), ('blocked', 'Blocked'), ('done', 'Ready To Pull')],
                                         'Kanban State',
                                         help="A task's kanban state indicates special situations affecting it:\n"
                                              " * Normal is the default situation\n"
                                              " * Blocked indicates something is preventing the progress of this task\n"
                                              " * Ready To Pull indicates the task is ready to be pulled to the next stage",
                                         readonly=True, required=False),
        'delay': fields.function(_get_delay_from_operation, string='Working Hours', type="float", help="The elapsed time between operation start and stop in this Work Center", readonly=True),
        'production_qty': fields.function(_get_production_qty, string="Production Qty", type="float")
    }

    _defaults = {
        'kanban_state': 'normal',
    }

    def write(self, cr, uid, ids, values, context=None, update=True):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if context.get('block_change', False) and values.get('workcenter_id', False):
            raise orm.except_orm(
                _(u'Invalid action !'),
                _(u'Is not possible to change the Work Center'))
        return super(mrp_production_workcenter_line, self).write(cr, uid, ids, values, context, update)

    def set_kanban_state_blocked(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'kanban_state': 'blocked', 'color': 2}, context=context)

    def set_kanban_state_normal(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'kanban_state': 'normal', 'color': 0}, context=context)

    def set_kanban_state_done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'kanban_state': 'done', 'color': 5}, context=context)

    def set_priority(self, cr, uid, ids, priority, context):
        """Set task priority
        """
        return self.write(cr, uid, ids, {'priority': priority}, context)

    def set_high_priority(self, cr, uid, ids, context):
        """Set task priority to high
        """
        return self.set_priority(cr, uid, ids, '1', context)

    def set_normal_priority(self, cr, uid, ids, context):
        """Set task priority to normal
        """
        return self.set_priority(cr, uid, ids, '2', context)

    def start_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # for production_order in self.browse(cr, uid, ids, context):
        #     if not production_order.user_id:
        #         production_order.write({'user_id': uid})
        return self.action_start_working(cr, uid, ids)

    def suspend_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        return self.action_pause(cr, uid, ids)

    def resume_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        return self.action_resume(cr, uid, ids)

    def stop_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        return self.action_done(cr, uid, ids)

    ##################################################################################################################
    #                   Overridden original functions and methods
    ##################################################################################################################

    def action_done(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        """ 
            Sets state to done, writes finish date and calculates delay.
        """
        delay = 0.0
        dt = datetime.now()
        date_now = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

        self.mark_operation(cr, uid, ids, True, context)  # Closes any opened pause
        pauses = self.get_operation_pauses(cr, uid, ids, context=context)  # Get all pauses
        self.set_kanban_state_normal(cr, uid, ids, context)
        for order_line in self.browse(cr, uid, ids, context):

            order_line_vals = {'state': 'done', 'date_finished': date_now}
            if order_line.date_start:
                date_start = datetime.strptime(order_line.date_start, DEFAULT_SERVER_DATETIME_FORMAT)
                date_finished = date_now
                delay = date_finished - date_start
                if pauses.get(order_line.id):
                    for pause in pauses[order_line.id]:
                        this_delay = pause['date_end'] - pause['date_start']
                        delay -= this_delay

                delay = delay.seconds / float(60 * 60)
                order_line_vals.update({'delay': delay})
            self.write(cr, uid, ids, order_line_vals, context)
            self.modify_production_order_state(cr, uid, [order_line.id], 'done')
        return True

    def action_start_working(self, cr, uid, ids, context=None):
        """ Sets state to pause.
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid )
        self.mark_operation(cr, uid, ids, False, context=context)
        self.set_kanban_state_done(cr, uid, ids, context)
        return super(mrp_production_workcenter_line, self).action_start_working(cr, uid, ids)

    def action_pause(self, cr, uid, ids, context=None):
        """ Sets state to pause.
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.mark_operation(cr, uid, ids, True, context=context)
        self.set_kanban_state_blocked(cr, uid, ids, context)
        return super(mrp_production_workcenter_line, self).action_pause(cr, uid, ids)

    def action_resume(self, cr, uid, ids, context=None):
        """ Sets state to startworking.
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.mark_operation(cr, uid, ids, False, context=context)
        self.set_kanban_state_done(cr, uid, ids, context)
        return super(mrp_production_workcenter_line, self).action_resume(cr, uid, ids)

    def action_start_working_rpc(self, cr, uid, operation_id, context=None):
        # Used by web app workorders
        context = context or self.pool['res.users'].context_get(cr, uid)
        operation_obj = self.pool['mrp.production.workcenter.line']
        try:
            operation = operation_obj.browse(cr, uid, operation_id, context)[0]
        except:
            return False
        if operation.production_id.state == 'draft':
            wf_service = netsvc.LocalService("workflow")
            mrp_production = operation.production_id
            wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_confirm', cr)
            wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'force_production', cr)
            wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_produce', cr)
        operation_obj.action_start_working(cr, uid, [operation.id], context)
        return True

    ##################################################################################################################
    #                   Overridden original functions and methods
    ##################################################################################################################

    def get_operation_pauses(self, cr, uid, ids, marker=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        """ 
            Mark fraction of operations.
            marker == False - Starts a new fraction
            marker == True  - Closes open fractions
        """
        order_lines = {}
        objFractions = self.pool['mrp.fraction_operations']

        for order in self.browse(cr, uid, ids, context):
            ret = []
            fraction_ids = objFractions.search(cr, uid, [('order_id', '=', order.id)], context=context)
            for fraction in objFractions.browse(cr, uid, fraction_ids, context):
                if not fraction.date_start or not fraction.date_end:
                    continue
                ret.append({
                    'user_id': uid,
                    'date_start': datetime.strptime(fraction.date_start, DEFAULT_SERVER_DATETIME_FORMAT),
                    'date_end': datetime.strptime(fraction.date_end, DEFAULT_SERVER_DATETIME_FORMAT)
                })
            order_lines[order.id] = ret
        return order_lines

    def mark_operation(self, cr, uid, ids, marker=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        """ 
            Mark fraction of operations.
            marker == False - Starts a new fraction
            marker == True  - Closes open fractions
        """
        objFractions = self.pool['mrp.fraction_operations']
        dt = datetime.now()
        # date_now = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        date_now = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_end = False  #  datetime(2099, 12, 31, 0, 0, 0)
        uid = context.get('user_id', uid)
        for order in self.browse(cr, uid, ids, context):
            if not marker:
                order_line = {
                    'user_id': uid,
                    'order_id': order.id,
                    'date_start': date_now,
                    'date_end': date_end,
                }
                objFractions.create(cr, uid, order_line, context)
            else:
                global_domain = [('order_id', '=', order.id), ('date_end', '=', date_end)]
                user_domain = [('user_id', '=', uid)]
                fraction_ids = objFractions.search(cr, uid, user_domain + global_domain, context=context, limit=1)
                if not fraction_ids:
                    fraction_ids = objFractions.search(cr, uid, global_domain, context=context, limit=1)
                objFractions.write(cr, uid, fraction_ids, {'date_end': date_now}, context)
        return False
