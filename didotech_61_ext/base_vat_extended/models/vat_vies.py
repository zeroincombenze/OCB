from tools.translate import _
import pyvies
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def get_data(cr, uid, pool, vat, context=None):
    partner_obj = pool['res.partner']
    address_obj = pool['res.partner.address']
    vat_country, vat_number = partner_obj._split_vat(vat)

    if partner_obj.simple_vat_check(cr, uid, vat_country, vat_number, context):
        v = pyvies.Vies("", '')
        try:
            result = v.validate(vat_country, vat_number)
        except Exception, e:
            error = _(e)
            _logger.error(_(u'Error on {vat}: {error}').format(vat=vat, error=error))
            return False

        _logger.info(_(u'VAT {vat}: Find VIES result {vies}').format(vat=vat, vies=result))

        if result.get('Name', False):
            address_values = result.get('Address', '').split('\n')
            address = {}
            if len(address_values) >= 2:
                # address_values = [u'VIA DOSSETI 1', u'38057 PERGINE VALSUGANA TN', u'']
                address = {
                    'type': 'default',
                    'street': address_values[0].title(),
                    'zip': address_values[1].split(' ')[0].title(),
                    'city': address_values[1][len(address_values[1].split(' ')[0]) + 1:len(address_values[1]) - 3].title()
                }
                city_value = address_obj.on_change_city(
                    cr,
                    uid,
                    address['zip'],
                    address['city']
                )
                address.update(city_value.get('value', {}))
            return {
                'name': result['Name'].title().replace('!', ' '),
                'address': address
            }
    else:
        return False
