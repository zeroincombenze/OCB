# -*- coding: utf-8 -*-
# © 2019 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import fields, orm

from inherit_fatturapa_attachment_out import FatturaPAAttachment2C


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'state_2c': fields.related(
            'fatturapa_attachment_out_id', 'state', relation='fatturapa.attachment.out',
            string='Stato invio', type='selection', selection=FatturaPAAttachment2C.e_invoice_state, readonly=True),
        'sdi_id':  fields.related('fatturapa_attachment_in_id', 'sdi_id',  string='IdSdi', type='float'),
        'sdi_date': fields.related('fatturapa_attachment_in_id', 'sdi_date', string='DataSdi', type='datetime'),
    }
