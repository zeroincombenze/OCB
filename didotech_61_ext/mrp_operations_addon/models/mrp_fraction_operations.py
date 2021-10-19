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
from openerp.osv import orm, fields
import time
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class MrpFractionOperations(orm.Model):
    _name = 'mrp.fraction_operations'
    _description = 'Operations as saved'

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        working_time = False
        if vals.get('working_time'):
            working_time = vals.get('working_time', 0)

        vals['hr_analytic_timesheet_id'] = self.create_update_analytic(cr, uid, vals, working_time, timeline_id=False, context=context)
        return super(MrpFractionOperations, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if isinstance(ids, (long, int)):
            ids = [ids]
        res = super(MrpFractionOperations, self).write(cr, uid, ids, vals, context)

        for task in self.browse(cr, uid, ids, context=context):
            line_id = task.hr_analytic_timesheet_id
            if line_id:
                if vals.get('working_time'):
                    working_time = vals['working_time']
                else:
                    date_start = task.date_start or vals.get('date_start', False)
                    date_end = task.date_end or vals.get('date_end', False)
                    working_time = self._get_working_time(date_start, date_end)['working_time']

                self.create_update_analytic(cr, uid, vals, working_time, timeline_id=line_id.id, context=context)

        return res

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        hat_obj = self.pool['hr.analytic.timesheet']
        hat_ids = []
        for task in self.browse(cr, uid, ids, context):
            if task.hr_analytic_timesheet_id:
                hat_ids.append(task.hr_analytic_timesheet_id.id)
            # delete entry from timesheet too while deleting entry to task.
        if hat_ids:
            hat_obj.unlink(cr, uid, hat_ids, context)
        return super(MrpFractionOperations, self).unlink(cr, uid, ids, context)

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(MrpFractionOperations, self).default_get(cr, uid, fields, context)
        users_obj = self.pool['res.users']
        if users_obj.has_group(cr, uid, 'mrp.group_mrp_user') and not users_obj.has_group(cr, uid, 'mrp.group_mrp_manager'):
            res.update({
                'user_id': uid
            })
        return res

    @staticmethod
    def _get_working_time(date_start=False, date_end=False):
        date_start = date_start or datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_end = date_end or date_start
        start_datetime = datetime.strptime(date_start, DEFAULT_SERVER_DATETIME_FORMAT)
        end_datetime = datetime.strptime(date_end, DEFAULT_SERVER_DATETIME_FORMAT)
        end_seconds = time.mktime(end_datetime.timetuple())
        start_seconds = time.mktime(start_datetime.timetuple())
        diff_hours = (end_seconds - start_seconds) / 60 / 60
        return {
            'working_time': diff_hours,
            'date': date_start
        }

    def _working_time(self, cr, uid, ids, name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for user_task in self.browse(cr, uid, ids, context):
            result[user_task.id] = self._get_working_time(user_task.date_start, user_task.date_end)

        return result

    def _set_data(self, cr, uid, id, name, value, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if name == 'date':
            start_datetime = datetime.strptime(value, DEFAULT_SERVER_DATE_FORMAT)
            date_start = datetime.strftime(start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
            self.write(cr, uid, [id], {'date_start': date_start}, context=context)
        elif name == 'working_time':
            date_start = self.read(cr, uid, id, ['date_start'], context=context)['date_start'] or datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            start_datetime = datetime.strptime(date_start, DEFAULT_SERVER_DATETIME_FORMAT)
            delta = value * 60 * 60
            end_time = start_datetime + timedelta(seconds=delta)
            end_datetime = datetime.strftime(end_time, DEFAULT_SERVER_DATETIME_FORMAT)
            self.write(cr, uid, [id], {'date_end': end_datetime}, context=context)
        return True

    _columns = {
        'user_id': fields.many2one('res.users', string="User"),
        'order_id': fields.many2one('mrp.production.workcenter.line', 'WorkCenter Operation', ondelete='cascade', select="1", required=True),
        'date': fields.function(_working_time, string='Date', type='date', fnct_inv=_set_data, multi='working_time'),
        'date_start': fields.datetime('Start Date'),
        'date_end': fields.datetime('End Date'),
        'working_time': fields.function(_working_time, type='float', string='Working Time', multi='working_time', fnct_inv=_set_data),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'production_qty': fields.integer('Production Qty'),
        'hr_analytic_timesheet_id': fields.many2one('hr.analytic.timesheet', 'Related Timeline Id',
                                                    ondelete='set null'),

        'line_id': fields.many2one('account.analytic.line', 'Analytic Line', ondelete='cascade', required=False),
    }

    _order = 'date_start desc'

    def create_update_analytic(self, cr, uid, vals, working_time=0, timeline_id=False, context=False):
        context = context or self.pool['res.users'].context_get(cr, uid)
        timesheet_obj = self.pool['hr.analytic.timesheet']
        uom_obj = self.pool['product.uom']

        vals_line = {}
        # obj_task = task_obj.browse(cr, uid, vals['task_id'])
        result = self.pool['project.task.work'].get_user_related_details(cr, uid, vals.get('user_id', uid))

        name = ''
        mrp_production_workcenter_line = False
        if vals.get('order_id'):
            ctx = context.copy()
            ctx['view_full_name'] = True
            mrp_production_workcenter_line = self.pool['mrp.production.workcenter.line'].browse(cr, uid, vals['order_id'], ctx)
            name = mrp_production_workcenter_line.name_get()[0][1]

        vals_line.update({
            'name': name,
            'user_id': vals.get('user_id', uid),
            'product_id': result['product_id'],
            'unit_amount': working_time,
            'general_account_id': result['general_account_id'],
            'journal_id': result['journal_id']
        })

        date = vals.get('date_start', False) or vals.get('date_stop', False) or vals.get('date', False)
        if date:
            vals_line.update({
                'date': date[:10],
            })

        # calculate quantity based on employee's product's uom
        default_uom = self.pool['res.users'].browse(cr, uid, uid, context).company_id.project_time_mode_id.id

        if result['product_uom_id'] != default_uom:
            vals_line['unit_amount'] = uom_obj._compute_qty(cr, uid, default_uom, working_time,
                                                            result['product_uom_id'])

        acc_id = mrp_production_workcenter_line and mrp_production_workcenter_line.production_id.analytic_account_id and mrp_production_workcenter_line.production_id.analytic_account_id.id or False
        if acc_id:
            vals_line['account_id'] = acc_id
            res = timesheet_obj.on_change_account_id(cr, uid, False, acc_id)
            if res.get('value'):
                vals_line.update(res['value'])

            vals_line['amount'] = 0.0
            vals_line['product_uom_id'] = result['product_uom_id']
            if timeline_id:
                timesheet_obj.write(cr, uid, [timeline_id], vals_line, context)
            else:
                timeline_id = timesheet_obj.create(cr, uid, vals_line, context)

        if timeline_id:
            # Compute based on pricetype
            amount_unit = timesheet_obj.on_change_unit_amount(cr, uid, timeline_id,
                                                              vals_line['product_id'], vals_line['unit_amount'], False, False, vals_line['journal_id'],
                                                              context=context)
            if amount_unit and 'amount' in amount_unit.get('value', {}):
                timesheet_vals = {
                    'amount': amount_unit['value']['amount'],
                    'unit_amount': working_time,
                }
                timesheet_obj.write(cr, uid, [timeline_id], timesheet_vals, context=context)
            return timeline_id


