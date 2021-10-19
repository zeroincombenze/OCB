# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Didotech SRL
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
import time
from tools.translate import _


class hr_engagement(orm.Model):
    _name = 'hr.engagement'
    _description = "Contractor Engagement"
    _rec_name = 'date'
    
    def _check_project_unique(self, cr, uid, ids, context=None):
        if not len(ids) == 1:
            return True
        engagement = self.browse(cr, uid, ids[0], context)
        engagement_ids = self.search(cr, uid, [
            ('contractor_id', '=', engagement.contractor_id.id),
            ('project_id', '=', engagement.project_id.id)
        ], context=context)
        if len(engagement_ids) > 1:
            return False
        else:
            return True
    
    _columns = {
        'contractor_id': fields.many2one('hr.contractor', 'Contractor Reference', ondelete='cascade', select=True, readonly=True),
        'date': fields.date('Date', required=True, readonly=True, select=True),
        'project_id': fields.many2one('project.project', 'Project', required=True, select=True),
        'user_id': fields.many2one('res.users', 'User', select=True),
        'not_interested': fields.boolean('Not Interested'),
        'waiting': fields.boolean('Waiting Replay'),
        'unsuitable': fields.boolean('Unsuitable'),
        'confermed': fields.boolean('Confirmed'),
        'cancelled': fields.boolean('Annullato'),
        'parttime_weekday': fields.float('Part Time', size=8),
        'fulltime_weekday': fields.float('Full Time', size=8),
        'parttime_holiday': fields.float('Part Time Holiday', size=8),
        'fulltime_holiday': fields.float('Full Time Holiday', size=8),
        'km_auto': fields.float('Km Auto', size=8),
        'km_auto_amount': fields.float('Rimborso Auto', size=8),
        'contract_type_id': fields.many2one('hr.contract.agreement.type', 'Tipo Contratto', required=True, select=True),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda obj, cr, uid, context: uid,
        'waiting': True,
    }
    _order = 'date desc'
    
    _constraints = [
        (_check_project_unique, _('Contractor is already assigned to this project'), ['contractor_id', 'project_id'])
    ]

    # def on_change_flag(self, cr, uid, ids, vals):
    #     print vals
    #     out_dict = {
    #         'not_interested': False,
    #         'waiting': False,
    #         'unsuitable': False,
    #         'confermed': False,
    #     }
    #     out_dict.update({vals: True})
    #     print out_dict
    #     return {
    #         'value': out_dict
    #     }
    #     return {'value': {}}

    def action_not_interested(self, cr, uid, ids, context):
        if not ids:
            return True
        for line in self.browse(cr, uid, ids, context):
            vals = {
                'not_interested': True,
                'waiting': False,
                'unsuitable': False,
                'confermed': False,
            }
            self.write(cr, uid, line.id, vals, context)
        return True

    def action_waiting(self, cr, uid, ids, context):
        if not ids:
            return True
        for line in self.browse(cr, uid, ids, context):
            vals = {
                'not_interested': False,
                'waiting': True,
                'unsuitable': False,
                'confermed': False,
            }
            self.write(cr, uid, line.id, vals, context)
        return True

    def action_unsuitable(self, cr, uid, ids, context):
        if not ids:
            return True
        for line in self.browse(cr, uid, ids, context):
            vals = {
                'not_interested': False,
                'waiting': False,
                'unsuitable': True,
                'confermed': False,
            }
            self.write(cr, uid, line.id, vals, context)
        return True

    def action_confermed(self, cr, uid, ids, context):
        if not ids:
            return True
        for line in self.browse(cr, uid, ids, context):
            vals = {
                'not_interested': False,
                'waiting': False,
                'unsuitable': False,
                'confermed': True,
            }
            self.write(cr, uid, line.id, vals, context)
        return True
        
    def on_change_project(self, cr, uid, ids, project_id):
        context = self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}

        contract_type_ids = self.pool['hr.contract.agreement.type'].search(cr, uid, [('default', '=', True)], limit=1, context=context)
        if contract_type_ids:
            contract_type_id = contract_type_ids[0]

        if project_id:
            project = self.pool['project.project'].browse(cr, uid, project_id, context)
            if project.contract_type_id:
                contract_type_id = project.contract_type_id.id

            res = {
                'value': {
                    'parttime_weekday': project.parttime_weekday,
                    'fulltime_weekday': project.fulltime_weekday,
                    'parttime_holiday': project.parttime_holiday,
                    'fulltime_holiday': project.fulltime_holiday,
                    'contract_type_id': contract_type_id,
                }
            }
        return res

    def action_assign_task(self, cr, uid, ids, context):
        for engagement_id in ids:
            if not isinstance(engagement_id, (float, int)):
                raise orm.except_orm(
                    _('Warning!'),
                    # _('Please save Contractor before activating a contract or press this button one more time.')
                    _("Per favore salva la scheda di Collaboratore o premi questo tasto un'altra volta")
                )

        model_obj = self.pool['ir.model.data']
        result = model_obj.get_object_reference(cr, uid, 'hr_contractor', 'action_hr_contractor_assign_task')
        act_window_id = result and result[1] or False
        result = self.pool['ir.actions.act_window'].read(cr, uid, [act_window_id], context=context)[0]
        return result
