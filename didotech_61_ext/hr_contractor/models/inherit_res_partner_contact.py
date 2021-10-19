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


class res_partner_contact(orm.Model):
    _inherit = 'res.partner.contact'
    _columns = {
        'destination': fields.char('Street', size=128),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'phone': fields.char('Phone', size=128),
        'fax': fields.char('Fax', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'province': fields.many2one('res.province', string='Province'),
        'region': fields.many2one('res.region', string='Region'),
        'country_id': fields.many2one('res.country', 'Country'),
        'user_django': fields.char('Utente', size=16),
        'password_django': fields.char('Password', size=16),
    }
    
    _sql_constraints = [
        ('user_django_uniq', 'unique(user_django)', 'Django username must be unique!')
    ]
    
    def on_change_city(self, cr, uid, ids, city, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if city:
            city_id = self.pool['res.city'].search(cr, uid, [('name', '=', city.title())], limit=1, context=context)
            if city_id:
                city_obj = self.pool['res.city'].browse(cr, uid, city_id[0], context)
                res = {
                    'value': {
                        'province': city_obj.province_id.id,
                        'region': city_obj.region.id,
                        'zip': city_obj.zip,
                        'country_id': city_obj.region.country_id.id,
                        'city': city.title(),
                    }
                }
        return res
