# -*- coding: utf-8 -*-
# © 2018-2019 Andrei Levin - Didotech srl (www.didotech.com)

import datetime

from openerp.addons.document_2c_fatturapa.models.document_2c_fatturapa import PassiveInvoice_2C
from openerp.addons.document_2c_fatturapa.models.inherit_fatturapa_attachment_out import SimpleConfig
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
import logging

logger = logging.getLogger(__name__)


class wizard_import_invoice(orm.TransientModel):
    _name = "wizard.import.passive.invoice"

    def get_default(self, cr, uid, context=None):
        if context is None:
            context = {}

        invoice_in_obj = self.pool['fatturapa.attachment.in']
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        config = SimpleConfig(company)
        config.document_host = self.pool['ir.config_parameter'].get_param(cr, uid, 'fp_2c_host')

        if config.document_host:
            # try to set as default last date
            last_xml_ids = invoice_in_obj.search(
                cr, uid, [('sdi_date', '!=', False)], context=context, order='sdi_date desc', limit=1)

            if last_xml_ids:
                last_xml = invoice_in_obj.browse(cr, uid, last_xml_ids[0], context)
                last_xml_date = datetime.datetime.strptime(last_xml.sdi_date, DEFAULT_SERVER_DATETIME_FORMAT)
                last_xml_date_date = last_xml_date.date().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                last_xml_date_date = datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            raise orm.except_orm(
                _('Error'),
                _('Please set destination host (fp_2c_host) for passive invoice')
            )

        return last_xml_date_date

    _defaults = {
        'start_import_date': get_default
    }

    _columns = {
        'start_import_date': fields.date('Data inizio importazione', required=True)
    }

    def import_invoice_2c(self, cr, uid, ids, context):
        invoice_in_obj = self.pool['fatturapa.attachment.in']
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        config = SimpleConfig(company)
        config.document_host = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fp_2c_host')

        invoice_to_recalculate_ids = invoice_in_obj.search(cr, uid, [('xml_supplier_id', '=', False)], context=context)
        if invoice_to_recalculate_ids:
            invoice_in_obj.dummy_button(cr, uid, invoice_to_recalculate_ids, context)

        if config.document_host:
            invoice = PassiveInvoice_2C(config)
            # i should set last xml date here from view
            date_from_wizard = self.browse(cr, uid, ids[0], context).start_import_date

            if date_from_wizard:
                invoices = invoice.get_invoices({
                    'DataInizio': datetime.datetime.strptime(date_from_wizard, DEFAULT_SERVER_DATE_FORMAT).date()
                })
            else:
                invoices = invoice.get_invoices()

            xml_ids = []

            for invoice in invoices:
                values = {
                    'datas': invoice.FileFattura.encode('base64'),
                    'datas_fname': invoice.DatiFattura.NomeFile,
                    'name': invoice.DatiFattura.NomeFile,
                    'sdi_id': invoice.DatiFattura.IdSdi,
                    'sdi_date': "{date.year}-{date.month}-{date.day} {date.hour}:{date.minute}:{date.second}".format(
                        date=invoice.DatiFattura.DataSdi),
                    'office_code': invoice.DatiFattura.CodiceUfficio
                }

                if self.pool["fatturapa.attachment.in"].search(cr, uid, [('name', '=', values['name'])]):
                    logger.info(u'{}: Invoice already imported'.format(values['name']))
                elif self.pool["fatturapa.attachment.in"].search(
                        cr, uid, [('name', '=', str(values['sdi_id']) + '_' + values['name'])]):
                    logger.info(u'{}: Invoice already imported'.format(str(values['sdi_id']) + '_' + values['name']))
                elif self.pool["fatturapa.attachment.in"].search(cr, uid, [('name', 'ilike', values['name'][:-4])]):
                    logger.info(u'{}: Invoice already imported'.format(values['name']))
                else:
                    logger.info('Importing {} ...'.format(values['name']))
                    xml_id = self.pool["fatturapa.attachment.in"].create(cr, uid, values, context)
                    xml_ids.append(xml_id)

            return {
                'type': 'ir.actions.act_window',
                'name': _('Supplier Invoices'),
                'res_model': 'fatturapa.attachment.in',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
                'domain': [('id', 'in', xml_ids)]
            }
        else:
            raise orm.except_orm(
                _('Error'),
                _('Please set destination host (fp_2c_host) for passive invoice')
            )
