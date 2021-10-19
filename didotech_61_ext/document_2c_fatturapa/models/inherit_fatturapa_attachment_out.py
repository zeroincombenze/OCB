# -*- coding: utf-8 -*-
# © 2018 Nicola Gramola - Didotech srl (www.didotech.com)
# © 2019 Andrei Levin - Didotech srl (www.didotech.com)

import logging
from datetime import datetime
from io import BytesIO

import lxml.etree as ET
from openerp.modules.module import get_module_resource
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

from .document_2c_fatturapa import FatturaPA_2C

_logger = logging.getLogger(__name__)


# 24.01.2019
# TIME_FORMAT_2C = '%m/%d/%Y %I:%M:%S %p'
# 29.01.2019
# TIME_FORMAT_2C = '%d/%m/%Y %I:%M:%S %p'


class SimpleConfig:
    def __init__(self, company):
        self.document_username = company.fpa_2c_username
        self.document_password = company.fpa_2c_password or ''
        self.estrazione_da_p7m = True if company.fpa_2c_formato_storage == 'xml' else False
        self.node = company.fpa_2c_node
        self.my_node = company.node


class FatturaPAAttachment2C(orm.Model):
    _inherit = "fatturapa.attachment.out"

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for attachment in self.read(cr, uid, ids, ['id', 'ir_attachment_id', 'fpa_idsdi', 'state'], context=context):
            if attachment['fpa_idsdi'] and not attachment['state'] == 'NS':
                raise orm.except_orm(
                    _('Invalid action !'),
                    _('Non è possibile eliminare una Fattura Elettronica già inviata.')
                )
            else:
                return super(FatturaPAAttachment2C, self).unlink(cr, uid, attachment['id'], context=context)

    def _get_data(self, cr, uid, ids, name, arg, context=None):
        attachments_out = self.browse(cr, uid, ids, context)
        document_host = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fa_2c_host')
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        data = {}

        if document_host:
            config = SimpleConfig(company)
            config.document_host = document_host
            fpa = FatturaPA_2C(config)

            for attachment in attachments_out:
                if attachment.store_fname and attachment.store_fname[:5] == 'idsdi':
                    data[attachment.id] = fpa.get_fatturapa(idsdi=attachment.store_fname[6:],
                                                            estrazioneP7M=config.estrazione_da_p7m)
                else:
                    data[attachment.id] = attachment.ir_attachment_id.datas
        else:
            for attachment in attachments_out:
                data[attachment.id] = attachment.ir_attachment_id.datas
        return data

    @staticmethod
    def get_2c_date(date_str):
        TIME_FORMAT_2C_US = '%m/%d/%Y %I:%M:%S %p'
        TIME_FORMAT_2C_EUR = '%d/%m/%Y %I:%M:%S %p'
        now = datetime.now()
        try:
            date = datetime.strptime(date_str, TIME_FORMAT_2C_EUR)
            if date.month == now.month:
                return date
            else:
                raise Exception('Probably month and day are inverted')
        except:
            try:
                date = datetime.strptime(date_str, TIME_FORMAT_2C_US)
                if date.month == now.month:
                    return date
                else:
                    raise Exception('Probably month and day are inverted')
            except:
                return now

    def upload_invoice(self, cr, uid, invoice_out, document_host, context):
        """
        Attention! This function works only with Old APIs
        :param cr:
        :param uid:
        :param invoice_out:
        :param document_host:
        :param context:
        :return:
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        invoice_obj = self.pool['account.invoice']

        config = SimpleConfig(invoice_out.company_id)
        config.document_host = document_host
        fpa = FatturaPA_2C(config)

        # invoice_ids = invoice_obj.search(cr, uid, [('internal_number', '=', context['internal_number'])])
        invoice_id = invoice_out.out_invoice_ids[0].id

        remote_fname = fpa.upload_data(invoice_out.datas_fname, invoice_out.datas.decode("base64"))
        if remote_fname and remote_fname[-3:].lower() == 'zip':
            email = False
            ret_sdi = fpa.send_fatturapa(email=email)

            if len(ret_sdi) == 3 and ret_sdi[0].isdigit():
                sdi_date = self.get_2c_date(ret_sdi[1])

                context['fpa_2c_fname'] = remote_fname
                context['fpa_idsdi'] = ret_sdi[0]
                context['fpa_sdi_send_date'] = sdi_date

                invoice_out.write({
                    # 'index_content': invoice_out.datas.decode('base64').decode('latin-1').encode('utf-8'),
                    'store_fname': 'idsdi:%s' % ret_sdi[0],
                    'fpa_2c_fname': remote_fname,
                    'fpa_idsdi': ret_sdi[0],
                    'fpa_sdi_send_date': sdi_date,
                    'state': 'sent',
                })

                ret_sdi_text = "Identificativo SdI assegnato %s, data invio %s " % (
                    ret_sdi[0], sdi_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))

                invoice_obj.message_append(
                    cr, uid, [invoice_id], ret_sdi_text, body_text=ret_sdi_text, context=context)
                return True
            else:
                if 'active_id' in context:
                    invoice_obj.message_append(
                        cr, uid, [invoice_id], ret_sdi, body_text=ret_sdi, context=context)
                if ret_sdi and 'Errore' in ret_sdi[0]:
                    raise orm.except_orm(_('Error!'), '\n'.join(ret_sdi))
                return False
        else:
            return True

    def upload_invoice_new(self, cr, uid, invoice_out, document_host, context):
        """
        Attention! This function works only with New APIs
        :param cr:
        :param uid:
        :param invoice_out:
        :param document_host:
        :param context:
        :return:
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        invoice_obj = self.pool['account.invoice']

        config = SimpleConfig(invoice_out.company_id)
        config.document_host = document_host
        fpa = FatturaPA_2C(config)

        # invoice_ids = invoice_obj.search(cr, uid, [('internal_number', '=', context['internal_number'])])
        invoice_id = invoice_out.out_invoice_ids[0].id

        remote_fname = fpa.upload_data(invoice_out.datas_fname, invoice_out.datas.decode("base64"))
        if remote_fname and remote_fname[-3:].lower() == 'zip':
            invoice = invoice_obj.browse(cr, uid, invoice_id, context)
            email = invoice.partner_id.mail_invoice_id and invoice.partner_id.mail_invoice_id.email or False
            ret_sdi = fpa.send_fatturapa(email=email)

            if len(ret_sdi) == 3 and ret_sdi[0].isdigit():
                sdi_date = self.get_2c_date(ret_sdi[1])

                context['fpa_2c_fname'] = remote_fname
                context['fpa_idsdi'] = ret_sdi[0]
                context['fpa_sdi_send_date'] = sdi_date

                invoice_out.write({
                    # 'index_content': invoice_out.datas.decode('base64').decode('latin-1').encode('utf-8'),
                    'store_fname': 'idsdi:%s' % ret_sdi[0],
                    'fpa_2c_fname': remote_fname,
                    'fpa_idsdi': ret_sdi[0],
                    'fpa_sdi_send_date': sdi_date,
                    'state': 'sent',
                })

                ret_sdi_text = "Identificativo SdI assegnato %s, data invio %s " % (
                    ret_sdi[0], sdi_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))

                invoice_obj.message_append(
                    cr, uid, [invoice_id], ret_sdi_text, body_text=ret_sdi_text, context=context)
                return True
            else:
                if 'active_id' in context:
                    invoice_obj.message_append(
                        cr, uid, [invoice_id], ret_sdi, body_text=ret_sdi, context=context)
                if ret_sdi and 'Errore' in ret_sdi[0]:
                    raise orm.except_orm(_('Error!'), ret_sdi[0])
                return False
        else:
            return True

    def _set_data(self, cr, uid, attachment_id, name, value, arg, context=None):
        if value:
            attachment_out = self.browse(cr, uid, attachment_id, context)
            company = self.pool['res.users'].browse(cr, uid, uid, context).company_id

            document_host = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fa_2c_host')

            if attachment_out.datas_fname[-3:] == 'xml' and document_host and company.fpa_2c_sent_to_sdi:
                # Save XML on local server anyway
                attachment_out.ir_attachment_id.write({
                    'datas': value
                })
                # invoice_id = context['active_id']
                self.upload_invoice(cr, uid, attachment_out, document_host, context)

            elif not document_host and company.fpa_2c_sent_to_sdi:
                raise orm.except_orm(
                    _('Error!'),
                    # _('Please set credentials for 2C server access'))
                    _('Please set destination host (fa_2c_host) for active invoice'))
            else:
                # attachment_out.write({
                #     'index_content': value.decode('base64').decode('latin-1').encode('utf-8')
                # })
                attachment_out.ir_attachment_id.write({
                    'datas': value
                })
                return True
        else:
            return True

    def _hook_after_sent(self, cr, uid, fatturapa_attachment_out, context):
        return True

    def send_cron_invoice_sdi(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        attachment_obj = self.pool['fatturapa.attachment.out']
        if ids is None:
            ids = attachment_obj.search(cr, uid, [('state', '=', 'draft')], context=context)

        counter = 0
        for fatturapa_attachment_out in self.browse(cr, uid, ids, context):
            if fatturapa_attachment_out.xml_error:
                continue
            try:
                self.action_send_invoice(cr, uid, [fatturapa_attachment_out.id], context)
                self._hook_after_sent(cr, uid, fatturapa_attachment_out, context)
            except Exception as error:
                _logger.error(error)

            counter += 1
            if counter == 10:
                counter = 0
                _logger.info('Committing...')
                cr.commit()
        return True

    def update_status(self, cr, uid, ids, context=None):
        tipo_messaggio = dict(self.e_invoice_state)
        invoice_obj = self.pool['account.invoice']
        attachment_obj = self.pool['fatturapa.attachment.out']
        if ids is None:
            ids = attachment_obj.search(cr, uid, [('state', '=', 'sent'), ('fpa_idsdi', '!=', False)], context=context)

        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        config = SimpleConfig(company)
        config.document_host = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fa_2c_host')
        fpa = FatturaPA_2C(config)
        if fpa.node == fpa.my_node:
            for attachment_out in self.browse(cr, uid, ids, context):
                if attachment_out.fpa_idsdi:
                    ret = fpa.get_esito_invio(attachment_out.fpa_idsdi)
                    if ret and ret['ResultCode'] == 'Success' and ret['ElectronicInvoiceOutcomes']:
                        for message in ret['ElectronicInvoiceOutcomes']['ElectronicInvoiceOutcome']:
                            attachment_out.write({
                                'state': message['TipoMessaggio'],
                            })
                            messaggio_log = "Messaggi FatturaPA. %s" % (tipo_messaggio.get(message['TipoMessaggio']),)
                            if attachment_out.out_invoice_ids:
                                invoice_obj.message_append(
                                    cr, uid,
                                    [attachment_out.out_invoice_ids[0].id],
                                    messaggio_log,
                                    body_text=messaggio_log + ": " + message['DescrizioneMessaggio'] if message['DescrizioneMessaggio'] else '',
                                    context=context
                                )

    e_invoice_state = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('error', 'Error'),
        ('NS', 'Notifica di Scarto'),
        ('MC', 'Notifica di Mancata Consegna'),
        ('RC', 'Ricevuta di Consegna'),
        ('EC_ACCETTAZIONE', 'Notifica di Esito Committente: ACCETTATA'),
        ('EC_RIFIUTO', 'Notifica di Esito Committente: RIFIUTATA'),
        ('SE', 'Notifica di Scarto Esito Committente'),
        ('NE', 'Notifica di Esito'),
        ('NE_ACCETTAZIONE', 'Notifica di Esito: ACCETTATA'),
        ('NE_RIFIUTO', 'Notifica di Esito: RIFIUTATA'),
        ('DT', 'Notifica di decorrenza di Decorrenza Termini'),
        ('AT', 'Attestazione di avvenuta trasmissione con impossibilità di recapito'),
        ('MT', 'Metadati'),
        ('ED', 'ED'),
        ('EF', 'EF'),
        ('EL', 'EL'),
        ('NA', 'NA'),
        ('NONE', 'Nessuna notifica'),
    ]

    def _get_fattura_elettronica_preview(self, cr, uid, ids, name, unknow_none, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        style_sheet_mode = user.company_id.style_sheet_mode
        if style_sheet_mode == 'asso_software':
            xsl_path = get_module_resource('l10n_it_fatturapa', 'data', 'FoglioStileAssoSoftware.xsl')
        else:
            xsl_path = get_module_resource('l10n_it_fatturapa', 'data', 'fatturaordinaria_v1.2.1.xsl')
        xslt = ET.parse(xsl_path)
        context = context or {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = {}
        xml_strings = self._get_data(cr, uid, ids, False, False, context=context)
        for fatturapa_attachment_id in ids:
            try:
                xml_string = xml_strings[fatturapa_attachment_id]
                xml_file = BytesIO(xml_string)
                recovering_parser = ET.XMLParser(recover=True)
                dom = ET.parse(xml_file, parser=recovering_parser)
                transform = ET.XSLT(xslt)
                newdom = transform(dom)
                res[fatturapa_attachment_id] = ET.tostring(newdom, pretty_print=True)
            except Exception as e:
                res[fatturapa_attachment_id] = ''
        return res

    _columns = {
        'xml_preview': fields.function(_get_fattura_elettronica_preview, type="text", string="Preview", method=True),
        'datas': fields.function(_get_data, fnct_inv=_set_data, string='File Content', type="binary", nodrop=True),
        'fpa_2c_fname': fields.text('2C full file path'),
        'fpa_idsdi': fields.char('ID SdI', 12),
        'fpa_sdi_send_date': fields.datetime('SdI send date'),
        'state': fields.selection(e_invoice_state, 'State', readonly=True, required=False)
    }

    _defaults = {
        'state': 'draft',
    }

    def action_send_invoice(self, cr, uid, ids, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        document_host = self.pool.get('ir.config_parameter').get_param(cr, uid, 'fa_2c_host')

        if not ids and 'active_ids' in context:
            ids = context['active_ids']

        if isinstance(ids, (int, long)):
            ids = [ids]

        for attachment_out in self.browse(cr, uid, ids, context):
            if attachment_out.state == 'draft':
                self.upload_invoice(cr, uid, attachment_out, document_host, context)

        if len(ids) == 1:
            view_res = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'document_2c_fatturapa', 'view_fatturapa_out_state_form')
            view_id = view_res and view_res[1] or False

            return {
                'type': 'ir.actions.act_window',
                'name': _("Sent Invoices"),
                'res_model': 'fatturapa.attachment.out',
                'view_type': 'form',
                'view_mode': 'page',
                'view_id': view_id,
                'res_id': ids[0],
                'target': 'current'
            }
        elif len(ids) > 1:
            # Unfortunately this doesn't work like it should. Sorry.
            view_res = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'l10n_it_fatturapa_out', 'view_fatturapa_out_attachment_tree')
                # cr, uid, 'document_2c_fatturapa', 'view_fatturapa_out_state')
            view_id = view_res and view_res[1] or False

            return {
                'type': 'ir.actions.act_window',
                'name': _("Sent Invoices"),
                'res_model': 'fatturapa.attachment.out',
                'view_type': 'tree',
                'view_mode': 'tree',
                'view_id': [view_id],
                # 'res_id': ids,
                'target': 'current',
                # 'domain': "[('id', 'in', {ids})]".format(ids=ids)
                'domain': [('id', 'in', ids)]
            }
