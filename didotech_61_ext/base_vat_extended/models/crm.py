from openerp.osv import fields, orm
from tools.translate import _
from vat_vies import get_data
import logging
from openerp import SUPERUSER_ID
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class crm_lead_vat(orm.Model):
    _inherit = "crm.lead"

    def vat_change(self, cr, uid, ids, vat, context=None):
        context = self.pool['res.users'].context_get(cr, uid)
        partner_obj = self.pool['res.partner']

        if vat:
            partner_vat = partner_obj.search(cr, SUPERUSER_ID, [('vat', '=', vat)], context=context)

            if partner_vat:
                partner = partner_obj.browse(cr, SUPERUSER_ID, partner_vat, context)[0]
                if partner.user_id.id != uid:
                    message = _(u"Vat {vat} already exist on partner {partner} assigned to {user}!").format(
                        vat=vat,
                        partner=partner.name,
                        user=partner.user_id.name or '')
                    return {'warning': {'title': 'Warning', 'message': message}}
                else:
                    return {'value': {
                        'partner_name': partner.name,
                        'vat': partner.vat,
                        'partner_id': partner.id,
                        'street': partner.address and partner.address[0].street or '',
                        'zip': partner.address and partner.address[0].zip or '',
                        'city': partner.address and partner.address[0].city or '',
                        'province': partner.address and partner.address[0].province and partner.address[0].province.id or '',
                        'region': partner.address and partner.address[0].region and partner.address[0].region.id or '',
                        'country_id': partner.address and partner.address[0].country_id and partner.address[0].country_id.id or '',
                    }}

            elif ids:
                return {'value': {}}

            else:
                name_address = get_data(cr, uid, self.pool, vat, context)
                
                if name_address:

                    return {
                        'value': {
                            'partner_name': name_address['name'],
                            'street': name_address['address'].get('street', 'Not found'),
                            'zip': name_address['address'].get('zip', 'Not found'),
                            'city': name_address['address'].get('city', 'Not found'),
                            'province': name_address['address'].get('province', 0),
                            'region': name_address['address'].get('region', 0),
                            'country_id': name_address['address'].get('country_id', 0),
                        }
                    }
                else:
                    return {'value': {}}
        else:
            return {'value': {}}
