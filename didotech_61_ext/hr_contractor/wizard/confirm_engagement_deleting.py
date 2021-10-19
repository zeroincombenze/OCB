# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Didotech (<http://www.didotech.com>)
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


class confirm_engagement_deleting(orm.TransientModel):
    _name = 'confirm.engagement.deleting'
    _description = 'Yes/No dialog'
    
    _columns = {
        'reply': fields.boolean(_('Confirm'), required=False),
    }
    
    def confirmation(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        engagement_id = context.get('active_id', False)
        if engagement_id:
            engagement_obj = self.pool['hr.engagement']
            engagement = engagement_obj.browse(cr, uid, engagement_id, context)
            task_obj = self.pool['project.task']
            task_ids = task_obj.search(cr, uid, [
                ('contractor_id', '=', engagement.contractor_id.id),
                ('project_id', '=', engagement.project_id.id),
                ('state', 'in', ('draft', 'assigned'))
            ], context=context)
            task_obj.write(cr, uid, task_ids, {'contractor_id': None, 'contractor_phone': None, 'state': 'draft'}, context)
            task_names = [task.name for task in task_obj.browse(cr, uid, task_ids, context)]
            if len(task_ids) == 1:
                message = _("Task {task} is set to state 'draft'").format(task=task_names[0])
            elif len(task_ids) > 1:
                message = _("Tasks {tasks} are set to state 'draft'").format(tasks=', '.join(task_names))
            else:
                message = _("No tasks connected with this engagement")
            self.log(cr, uid, engagement_id, message)
            
            values = {'cancelled': True}
            
            engagement_obj.write(cr, uid, engagement_id, values, context)
        
        return {'type': 'ir.actions.act_window_close'}

