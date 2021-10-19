##############################################################################
#
#    Author: Didotech SRL
#    Copyright 2016 Didotech SRL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from tools.translate import _
from openerp import SUPERUSER_ID
from vat_vies import get_data
import re
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class res_partner(orm.Model):
    _inherit = 'res.partner'

    def vat_change(self, cr, uid, ids, vat, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if vat:
            partner_vat = self.search(cr, uid, [('vat', '=', vat)], context=context)
            if partner_vat and not context.get('force_search', False):
                partner = self.browse(cr, SUPERUSER_ID, partner_vat, context)[0]
                message = _(u"Vat {vat} just exist on partner {partner} assigned to {user}!").format(
                    vat=vat,
                    partner=partner.name,
                    user=partner.user_id.name or '')
                return {'warning': {'title': 'Warning', 'message': message}}
            elif ids:
                return {'value': {}}
            else:
                name_address = get_data(cr, uid, self.pool, vat, context)
                if name_address:
                    return {
                        'value': {
                            'name': name_address['name'],
                            'vat_subjected': True,
                            'address': [(0, 0, name_address['address'])]
                        }
                    }
                else:
                    return {'value': {}}
        else:
            return {'value': {'vat_subjected': False}}

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        limit = limit

        if not args:
            args = []
        ids = []

        if name:
            ids = self.search(cr, uid, [('name', 'ilike', name)] + args, limit=limit, context=context)

            if not len(ids):
                if len(name) == 11:
                    name = 'IT' + name
                ids = self.search(cr, uid, [('vat', '=', name)] + args, limit=limit, context=context)
                if ids:
                    context.update({'find_vat': True})

                if not len(ids) and len(name) == 13:
                    # i search if exist VAT
                    value = self.vat_change(cr, uid, [], name, context) or {}

                    if value.get('value', False):
                        value['value'].update({'vat': name})
                        ids = [self.create(cr, uid, value.get('value'), context)]
                        _logger.info(
                            u'VAT {vat}: Create Partner {name}'.format(vat=name, name=value.get('value')['name']))

            if not len(ids):
                ids = self.search(cr, uid, [('property_customer_ref', '=', name)] + args, limit=limit, context=context)

            if not len(ids):
                ids = self.search(cr, uid, [('property_supplier_ref', '=', name)] + args, limit=limit, context=context)

            if not len(ids):
                if len(name) == 1 and operator == 'ilike':
                    operator = '=ilike'
                    name = name + '%'

                ids_1 = self.search(
                    cr, uid, args + [('name', operator, name)], limit=limit, context=context)
                ids_2 = self.search(
                    cr, uid, args + [('vat', operator, name)], limit=limit, context=context)
                ids_3 = self.search(
                    cr, uid, args + [('property_customer_ref', operator, name)], limit=limit, context=context)
                ids_4 = self.search(
                    cr, uid, args + [('property_supplier_ref', operator, name)], limit=limit, context=context)

                ids = ids_1 + ids_2 + ids_3 + ids_4
                ids = list(set(ids))

            if not len(ids):
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)

                if res:
                    ids = self.search(
                        cr, uid, [('name', '=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        result = self.name_get(cr, uid, ids, context=context)
        return result

    @staticmethod
    def remove_spaces_from_vat(vat):
        if vat and vat[:2] == 'IT':  # Normalize for italian VAT
            vat = vat.replace(" ", "")
        return vat

    def create(self, cr, uid, vals, context=None):
        if vals.get('vat', False):
            vals['vat'] = self.remove_spaces_from_vat(vals['vat'])
        return super(res_partner, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('vat', False):
            vals['vat'] = self.remove_spaces_from_vat(vals['vat'])
        return super(res_partner, self).write(cr, uid, ids, vals, context)
