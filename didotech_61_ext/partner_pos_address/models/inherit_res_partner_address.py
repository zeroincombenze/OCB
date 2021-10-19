# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2017
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


class partner_pos_address(orm.Model):    
    _inherit = "res.partner.address"
    _order = "complete_name, partner_id, banner_id, province, city"
    
    def get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not ids:
            return {}
        res = {}
        for partner_address in self.browse(cr, uid, ids, context=context):
            addr = ''
            if partner_address.type == 'pos':
                addr = partner_address.banner_id and partner_address.banner_id.name or ''
            else:
                addr = partner_address.name or ''

            addr += u', ' + (partner_address.city or '') + ' ' + (partner_address.street or '')
            if partner_address.partner_id:
                addr = u"{0}: {1}".format(partner_address.partner_id.name, addr.strip())
            else:
                addr = addr.strip()
            if partner_address.tag:
                addr += ', ' + partner_address.tag
            res[partner_address.id] = addr or ''
        return res

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not len(ids):
            return []
        res = []

        for address in self.browse(cr, uid, ids, context=context):
            if context.get('contact_display', 'contact') == 'partner' and address['partner_id']:
                res.append((address.id, address.partner_id.name))
            else:
                addr = ''
                if address.type == 'pos':
                    addr = (address.banner_id and address.banner_id.name or '').upper()
                else:
                    addr = (address.name or '').upper()
                # if r['name'] and (r['city'] or r['country_id']):
                #    addr += ', '
                addr += u', ' + (address.city or '').title() + ' ' + (address.street or '').title()
                if (context.get('contact_display', 'contact') == 'partner_address') and address.partner_id:
                    res.append(address.id, u"{0}: {1}".format(address.partner_id.name, addr.strip() or '/'))
                else:
                    res.append((address.id, addr.strip() or '/'))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        name_array = name.split()
        search_domain = []
        for n in name_array:
            search_domain.append('|')
            search_domain.append(('name', operator, n))
            search_domain.append(('complete_name', operator, n))
        ids = self.search(cr, user, search_domain + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)

    def _get_partner_code(self, cr, uid, ids, name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        if context is None:
            return res

        partner_id = context.get('partner_id', False)
        if partner_id:
            sql = """
                select pos.id,pcode.code
                from res_partner_address as pos left join partner_pos_code as pcode on pcode.pos_id = pos.id
                where pos.id in %s and pcode.partner_id = %s
            """
            cr.execute(sql, (tuple(ids), partner_id,))
            res = dict(cr.fetchall())
        for id in ids:
            if not res.has_key(id):
                res[id] = False
        return res

    _columns = {
        "is_pos": fields.boolean("Is Pos?"),
        'close': fields.boolean("Chiuso", help="Definisco se il negozio è chiuso"),
        "banner_id": fields.many2one("res.partner.banner", "Banner"),
        'tag': fields.char("Tag", size=32),
        'director_ids': fields.one2many('res.partner.director', "address_id", "Director"),
        'hour_from': fields.float('Work from', size=8, required=True, help="Working time will start from"),
        'hour_to': fields.float("Work to", size=8, required=True, help="Working time will end at"),
        'working_day_ids': fields.one2many("res.partner.attendence", "address_id", "Working Day"),
        'type': fields.selection([('default', 'Default'), ('invoice', 'Invoice'), ('delivery', 'Delivery'), ('contact', 'Contact'), ('other', 'Other'), ('pos', 'POS')], 'Address Type', help="Used to select automatically the right address according to the context in sales and purchases documents."),
        'complete_name': fields.function(get_full_name, string="Complete Name", method=True, type='char', size=1024, readonly=True, store=True),
        'user_django': fields.char('Utente', size=16, ),
        'password_django': fields.char('Password', size=16, ),
        'partner_codes': fields.one2many('partner.pos.code', 'pos_id', 'Customer Codes'),
        'partner_agent': fields.one2many('partner.agent.code', 'agent_id', 'Customer Agent'),
        'partner_pos_code': fields.function(_get_partner_code, method=True, type="char", string='Code', size=64)
    }

    _defaults = {
        'hour_from': 8.5,
        'hour_to': 20.0
    }

    _sql_constraints = [
        ('user_django_uniq', 'unique(user_django)', 'Django username must be unique!')
    ]

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        address_type = context.get('default_type', False)
        res = super(partner_pos_address, self).default_get(cr, uid, fields, context)
        if address_type:
            res.update({'type': address_type})
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        return {'value': {'banner_id': False}}

    def get_work_time(self, cr, uid, ids, day=0, work_time='full', context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not ids:
            return {}
        res = {}
        for pos in self.browse(cr, uid, ids, context=context):
            if len(pos.working_day_ids) > 0:
                working_day_ids = self.pool['res.partner.attendence'].search(cr, uid, [('address_id', '=', pos.id), ('dayofweek', '=', day)], context=context)
                if len(working_day_ids) == 0:
                    if work_time == 'full':
                        res[pos.id] = {
                            'hour_from': pos.hour_from,
                            'hour_to': pos.hour_to,
                        }
                        continue
                    middle_time = (pos.hour_from + pos.hour_to) / 2
                    if work_time == 'half':
                        res[pos.id] = {
                            'hour_from': pos.hour_from,
                            'hour_to': middle_time,
                        }
                    else:
                        res[pos.id] = {
                            'hour_from': middle_time,
                            'hour_to': pos.hour_to,
                        }
                    continue
                elif len(working_day_ids) == 1:
                    work_day = self.pool['res.partner.attendence'].browse(cr, uid, working_day_ids[0], context=context)
                    if work_time == 'full':
                        res[pos.id] = {
                            'hour_from': work_day.hour_from,
                            'hour_to': work_day.hour_to,
                        }
                        continue
                    middle_time = (work_day.hour_from + work_day.hour_to) / 2
                    if work_time == 'half':
                        res[pos.id] = {
                            'hour_from': work_day.hour_from,
                            'hour_to': middle_time,
                        }
                    else:
                        res[pos.id] = {
                            'hour_from': middle_time,
                            'hour_to': work_day.hour_to,
                        }
                    continue
                elif len(working_day_ids) > 1:
                    work_days = self.pool['res.partner.attendence'].browse(cr, uid, working_day_ids, context=context)
                    time1 = work_days[0]
                    time2 = work_days[1]
                    if work_time == 'full':
                        res[pos.id] = {
                            'hour_from': time1.hour_from,
                            'hour_to': time2.hour_to,
                        }
                        continue
                    middle_time = (time1.hour_from + time2.hour_to) / 2
                    if work_time == 'half':
                        res[pos.id] = {
                            'hour_from': work_day.hour_from,
                            'hour_to': middle_time,
                        }
                    else:
                        res[pos.id] = {
                            'hour_from': middle_time,
                            'hour_to': work_day.hour_to,
                        }
                    continue
            else:
                if work_time == 'full':
                    res[pos.id] = {
                        'hour_from': pos.hour_from,
                        'hour_to': pos.hour_to,
                    }
                    continue
                middle_time = (pos.hour_from + pos.hour_to)/ 2
                if work_time == 'half':
                    res[pos.id] = {
                        'hour_from': pos.hour_from,
                        'hour_to': middle_time,
                    }
                else :
                    res[pos.id] = {
                        'hour_from': middle_time,
                        'hour_to': pos.hour_to,
                    }
                continue
        return res
