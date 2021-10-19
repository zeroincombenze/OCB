# -*- coding: utf-8 -*-
#    Copyright (C) 2010-2017 Associazione Odoo Italia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#


from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def set_default_value(cr, pool):

    uid = SUPERUSER_ID
    context = pool['res.users'].context_get(cr, uid)
    res_partner_obj = pool['res.partner']
    res_partner_address_obj = pool['res.partner.address']

    # fix PEC
    res_partner_address_ids = res_partner_address_obj.search(cr, uid, [('pec', '!=', False)], context=context)
    _logger.info("Start Update {0} address PEC".format(len(res_partner_address_ids)))
    for address in res_partner_address_obj.browse(cr, uid, res_partner_address_ids, context):
        pec = address.pec
        if not address.partner_id.pec_destinatario and address.partner_id:
            res_partner_obj.write(cr, uid, address.partner_id.id, {'pec_destinatario': pec, 'electronic_invoice_subjected': True}, context)

    res_partner_ids = res_partner_obj.search(cr, uid, [('unique_office_code', '!=', False)], context=context)
    _logger.info("Start Update {0} Partner codice_destinatario".format(len(res_partner_ids)))
    for partner in res_partner_obj.browse(cr, uid, res_partner_ids, context):
        if not partner.codice_destinatario or partner.codice_destinatario == '0000000':
            res_partner_obj.write(cr, uid, partner.id, {'codice_destinatario': partner.unique_office_code, 'electronic_invoice_subjected': True})

    return True
