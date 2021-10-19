# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 DeneroTeam. (<http://www.deneroteam.com>)
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
from openerp.tools.translate import _


class res_partner_banner(orm.Model):    
    _name = "res.partner.banner"
    _columns = { 
        'name': fields.char('Name', size=64, required=True),
        'group_ids': fields.many2many('res.partner', 'res_partner_res_parner_banner_rel','group_id','banner_id','Groups'),
    }
    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Banner Name must be unique !'),
    ]

    def create(self, cr, uid, value, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        # if context.get('block_creation', False):
        #     raise orm.except_orm(_('Error !'), _(context.get('block_creation')))
        value['name'] = value['name'].upper()

        already_banner_ids = self.search(cr, uid, [('name', '=', value['name'])], context=context)
        if already_banner_ids:
            group_ids = []
            for group in value.get('group_ids', []):
                if group[0] == 6:
                    group_ids.append([4, group[2][0]])
            if context.get('partner_id', False):
                group_ids.append([4, context['partner_id']])
            value['group_ids'] = group_ids
            self.write(cr, uid, already_banner_ids[0], value, context)
            return already_banner_ids[0]
        if context.get('partner_id', False):
            value['group_ids'] = [[6, False, [context['partner_id']]]]
        res = super(res_partner_banner, self).create(cr, uid, value, context)
        return res
