# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Operations Wizard
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

import netsvc
from openerp import SUPERUSER_ID
from openerp.osv import fields, orm
from tools.translate import _


class wizard_mrp_operations(orm.TransientModel):
    _name = "wizard.mrp.operations"
    _description = "MRP Operations"

    _columns = {
        'state': fields.selection(
            [('draft', 'Draft'), ('startworking', 'In Progress'), ('pause', 'Pending'), ('cancel', 'Cancelled'),
             ('done', 'Finished')], 'State'),
        'operation_barcode': fields.char('Barcode'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'production_id': fields.many2one('mrp.production', 'Manufacturing',
                                         domain=[('state', 'in', ('draft', 'ready', 'confirmed', 'in_production'))]),
        'operation_id': fields.many2one('mrp.production.workcenter.line', 'Operation'),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter'),
        'message': fields.char('Message'),
    }

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(wizard_mrp_operations, self).default_get(cr, uid, fields, context=context)
        res['user_id'] = uid
        return res

    def get_workcenters_list(self, cr, uid, ids, production_id, operation_id, workcenter_id, signal, context=None):
        """
            Retrieve workcenters ids in list format ready for domain
            ids : production_id
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        wcs = []
        uID = SUPERUSER_ID
        value = {'operation_id': operation_id, 'workcenter_id': workcenter_id}
        domain = {'operation_id': [('id', '=', '0')], 'workcenter_id': [('id', '=', '0')], }
        wcline_obj = self.pool['mrp.production.workcenter.line']
        criteria = [('production_id', '=', production_id)]
        if signal == 'start':
            criteria.extend([('state', '!=', 'done'), ('state', '!=', 'cancel')])
        elif signal == 'suspend':
            criteria.extend([('state', '=', 'startworking')])
        elif signal == 'resume':
            criteria.extend([('state', '=', 'pause')])
        elif signal == 'end':
            criteria.extend([('state', 'in', ['startworking', 'pause'])])
        wcline_ids = wcline_obj.search(cr, uID, criteria, context=context)
        if wcline_ids and not operation_id and not workcenter_id:
            for mrp_wc in wcline_obj.browse(cr, uID, wcline_ids, context):
                res.append(mrp_wc.workcenter_id.id)
            if len(wcline_ids) == 1:
                value = {'operation_id': wcline_ids[0], 'workcenter_id': res[0]}
            domain = {'operation_id': [('id', 'in', wcline_ids)], 'workcenter_id': [('id', 'in', res)], }

        return {'value': value, 'domain': domain}

    def get_workcenters_id(self, cr, uid, ids, operation_id, user_id, signal, context=None):
        """
            Retrieve workcenter id of operation            
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        value = {}
        warning = {}
        uID = SUPERUSER_ID
        if operation_id:
            mrp_wc_line_obj = self.pool['mrp.production.workcenter.line']
            wrk_line = mrp_wc_line_obj.browse(cr, uID, operation_id, context)
            if wrk_line.workcenter_id:
                value.update({
                    'workcenter_id': wrk_line.workcenter_id.id,
                    'production_id': wrk_line.production_id.id
                })

        return {'value': value, 'warning': warning}

    def getUserName(self, cr, uid, userId, context=None):
        """
            Gets the user name
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        userType = self.pool['res.users']
        uiUser = userType.browse(cr, uid, userId, context=context)
        return uiUser.name

    def onchange_user_id(self, cr, uid, ids, user_id=False, context=None):
        ret = {}
        uID = SUPERUSER_ID
        context = context or self.pool['res.users'].context_get(cr, uid)
        wc_obj = self.pool['mrp.workcenter']
        res_obj = self.pool['resource.resource']
        res_id = res_obj.search(cr, uID, [('user_id', '=', user_id)], context=context)
        if res_id:
            wc_id = wc_obj.search(cr, uID, [('resource_id', '=', res_id[0])], context=context)
            if wc_id:
                return {'value': {'workcenter_id': wc_id[0]}}
        return ret

    def onchange_operation_barcode(self, cr, uid, ids, barcode, context):
        value = {}
        warning = {}
        uID = SUPERUSER_ID
        if barcode:
            barcode = barcode.upper()
            mrp_wc_line_obj = self.pool['mrp.production.workcenter.line']
            mrp_wc_line_ids = mrp_wc_line_obj.search(cr, uID, [('opbcode', '=', barcode)], context=context)
            if not mrp_wc_line_ids:
                mrp_wc_line_ids = mrp_wc_line_obj.search(cr, uID, [('opbcode', '=', barcode.replace('-', '/'))], context=context)
            if mrp_wc_line_ids:
                operation = mrp_wc_line_obj.browse(cr, uid, mrp_wc_line_ids[0], context)
                value.update({
                    'operation_id': mrp_wc_line_ids[0],
                    'operation_barcode': False,
                    'state': operation.state,
                    'user_id': operation.user_id and operation.user_id.id or operation.production_id.user_id and operation.production_id.user_id.id or uid
                })

        return {'value': value, 'warning': warning}

    def onchange_start_operation_id(self, cr, uid, ids, operation_id=False,
                                    user_id=False, workcenter_id=False,
                                    context=None):
        ret = False
        context = context or self.pool['res.users'].context_get(cr, uid)
        uID = SUPERUSER_ID
        wc_obj = self.pool['mrp.workcenter']
        res_obj = self.pool['resource.resource']
        operation_obj = self.pool['mrp.production.workcenter.line']
        res_id = res_obj.search(cr, uid, [('user_id', '=', user_id)], context=context)
        if res_id:
            wc_id = wc_obj.search(cr, uID, [('resource_id', '=', res_id[0])], context=context)
            if wc_id:
                operation_ids = operation_obj.search(cr, uID, [('workcenter_id', '=', wc_id[0])], context=context)
            if operation_id:
                for operation in operation_obj.browse(cr, uID, operation_ids, context=context):
                    if operation.state.toLower() == 'startworking':
                        userName = self.getUserName(cr, uID, user_id, context=context)
                        ret = {
                            'value': {
                                'message': _(u'User {user} is already working on operation {operation}.').format(user=userName, operation=operation.name)
                            }
                        }
                        break
        return ret

    def start_task(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        view_rec = self.pool['ir.model.data'].get_object_reference(cr, uid, 'mrp_operations_wizard',
                                                                   'wizard_mrp_operations_start')
        view_id = view_rec and view_rec[1] or False
        return {
            'view_type': 'form',
            'name': "MRP Operations - Start Operation",
            'view_id': [view_id],
            'res_id': wizard.id,
            'view_mode': 'form',
            'domain': "[('user_id','=', %d)]" % uid,
            'res_model': 'wizard.mrp.operations',
            'type': 'ir.actions.act_window',
            'context': context,
        }

    def start_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        uID = wizard.user_id.id
        operation_obj = self.pool['mrp.production.workcenter.line']
        if not wizard.operation_id.state == 'startworking':
            if wizard.operation_id.production_id.state == 'draft':
                wf_service = netsvc.LocalService("workflow")
                mrp_production = wizard.operation_id.production_id
                wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_confirm', cr)
                wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'force_production', cr)
                wf_service.trg_validate(uid, 'mrp.production', mrp_production.id, 'button_produce', cr)
            operation_obj.action_start_working(cr, uID, [wizard.operation_id.id])
        return {'type': 'ir.actions.act_window_close'}

    def suspend_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        uID = wizard.user_id.id
        operation_obj = self.pool['mrp.production.workcenter.line']
        operation_obj.action_pause(cr, uID, [wizard.operation_id.id])
        return {'type': 'ir.actions.act_window_close'}

    def resume_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        uID = wizard.user_id.id
        operation_obj = self.pool['mrp.production.workcenter.line']
        operation_obj.action_resume(cr, uID, [wizard.operation_id.id])
        return {'type': 'ir.actions.act_window_close'}

    def stop_operation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        wizard = self.browse(cr, uid, ids, context=context)[0]
        operation_obj = self.pool['mrp.production.workcenter.line']
        uID = wizard.user_id.id
        if wizard.operation_id.state == 'draft':
            operation_obj.action_start_working(cr, uid, [wizard.operation_id.id])
        operation_obj.action_done(cr, uID, [wizard.operation_id.id])
        return {'type': 'ir.actions.act_window_close'}
