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


class hr_analytic_timesheet(orm.Model):
    #_name = 'hr.analytic.timesheet'
    _inherit = 'hr.analytic.timesheet'

    _columns = {
        'repair_order_id': fields.many2one('repair.order', 'Repair Order'),
        'is_free': fields.boolean("No Invoice"),
    }

    _defaults = {
        'account_id': lambda self, cr, uid, context: context.get('account_id', False),
    }

    def on_change_repair_order(self, cr, uid, ids, repair_order_id):
        res = {'value': {}}
        if repair_order_id:
            vals = {}
            repair_order = self.pool['repair.order'].browse(cr, uid, repair_order_id)
            vals.update({
                'account_id': repair_order.account_id and repair_order.account_id.id or False
            })
            res.update({'value': vals})
        return res

    def unlink(self, cr, uid, ids, context=None):
        result = super(hr_analytic_timesheet, self).unlink(cr, uid, ids, context)
        if context.get('update_repair_order', False):
            update_service = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.update_service
            for analytic in self.browse(cr, uid, ids, context):
                if analytic.repair_order_id and update_service:
                    self.pool['repair.order'].write(cr, uid, [analytic.repair_order_id.id], {}, context)
        return result

    def write(self, cr, uid, ids, values, context=None):
        result = super(hr_analytic_timesheet, self).write(cr, uid, ids, values, context)
        if context.get('update_repair_order', False): # done for increase speed, now check is call only if need
            update_service = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.update_service
            repair_order_id = values.get('repair_order_id', False)
            if repair_order_id and update_service:
                self.pool['repair.order'].write(cr, uid, [repair_order_id], {}, context)
        return result

    def create(self, cr, uid, values, context=None):
        result = super(hr_analytic_timesheet, self).create(cr, uid, values, context)
        if context.get('update_repair_order', False):
            update_service = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.update_service
            repair_order_id = values.get('repair_order_id', False)
            if repair_order_id and update_service:
                self.pool['repair.order'].write(cr, uid, [repair_order_id], {})
        return result