# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2013 Didotech srl (<http://www.didotech.com>)
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
from tools.translate import _


class hr_contractor_assign_task(orm.TransientModel):

    _name = "hr.contractor.assign.task"
    _description = "Assign task at Contractor"

    def _get_task_id(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        obj_task = self.pool['project.task']

        vals = []

        model = context.get('active_model', False)
        if model != 'hr.engagement':
            return vals

        obj_model = self.pool.get(model)
        res_ids = context and context.get('active_ids', [])
        engagement_data = obj_model.browse(cr, uid, res_ids, context=context)
        for engagement in engagement_data:

            if engagement.project_id:
                tasks_ids = [engagement.project_id.id]
                value = obj_task.search(cr, uid, [('project_id', 'in', tasks_ids), ('state', '=', 'draft')], context=context)

            for single_task in obj_task.browse(cr, uid, value, context=context):
                readable_field_name_task = ''
                if not single_task.name:
                    readable_field_name_task = single_task.name
                    
                # readable_field_name = ''
                if not single_task.pos_id.banner_id.name:
                    readable_field_name = single_task.pos_id.partner_id.name
                else:
                    readable_field_name = single_task.pos_id.banner_id.name
                    
                readable_field_city = ''
                if not single_task.pos_id.city:
                    readable_field_city = single_task.pos_id.city
                    
                readable_field_street = ''
                if not single_task.pos_id.street:
                    readable_field_street = single_task.pos_id.street

                readable_field = '{0} {1}, {2} {3}'.format(readable_field_name_task, readable_field_name, readable_field_city, readable_field_street)
                tsk1 = single_task.id, readable_field
                if tsk1 not in vals:
                    vals.append(tsk1)
        if not vals:
            raise orm.except_orm(_('Warning !'), _('Control your Activity task and/or not specific project for resource!'))

        return vals

    def _get_project(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        engagement_obj = self.pool['hr.engagement']
        # project_obj = self.pool['project.project')
        active_ids = context.get('active_ids', [])
        project_id = False
        for engagement in engagement_obj.browse(cr, uid, active_ids, context=context):
            if not engagement.project_id:
                raise orm.except_orm(_('Warning !'), _('Control Contractor. Project not declared.'))
            else:
                project_id = engagement.project_id.id
        return project_id
    
    _columns = {
        'project_id': fields.many2one('project.project', 'Project'),
        'tasks_ids': fields.many2many('project.task', 'rel_wizard_tasks', 'wiz_id', 'task_id', 'Tasks', required=True),
    }
    _defaults = {
        'project_id': _get_project,
    }

    def assign_task(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        task_obj = self.pool['project.task']

        tasks = self.browse(cr, uid, ids, context=context)
        list_task_ids = []
        for task in tasks:
            for id_task in task.tasks_ids:
                list_task_ids.append(id_task.id)
        if not list_task_ids:
            return True

        model = context.get('active_model', False)
        if model != 'hr.engagement':
            return True
        
        obj_model = self.pool.get(model)
        res_ids = context and context.get('active_ids', [])
        ctx = context.copy()
        for engagement in obj_model.browse(cr, uid, res_ids, context=context):
            contractor_id = engagement.contractor_id.id
            ctx.update({'engagement_id': engagement.id})
            task_obj.write(cr, uid, list_task_ids, {'contractor_id': contractor_id}, context=ctx)
            task_obj.set_assigned(cr, uid, list_task_ids, context)
            engagement_dict = self.on_change_flag()
            obj_model.write(cr, uid, res_ids, engagement_dict, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def on_change_flag(self):
        out_dict = {
            'not_interested': False,
            'waiting': False,
            'unsuitable': False,
            'confermed': True,
        }

        return out_dict
