# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
#    Copyright (C) 2019 Didotech srl <info@didotech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from io import BytesIO
import logging
import lxml.etree as ET
from openerp.addons.l10n_it_ade.bindings import fatturapa_v_1_2 as fatturapa
from openerp.modules.module import get_module_resource
from openerp.osv import fields, orm
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class FatturaPAAttachment(orm.Model):
    _name = "fatturapa.attachment.out"
    _description = "E-invoice Export File"
    _inherits = {'ir.attachment': 'ir_attachment_id'}
    _inherit = ['mail.thread']

    def _compute_has_pdf_invoice_print(self, cr, uid, ids, name, unknow_none, context=None):
        context = context or {}
        ret = {}
        for attachment_out in self.browse(cr, uid, ids, context):
            for invoice in attachment_out.out_invoice_ids:
                invoice_attachments = invoice.fatturapa_doc_attachments
                if any([ia.is_pdf_invoice_print
                        for ia in invoice_attachments]):
                    continue
                else:
                    ret[attachment_out.id] = False
                    break
            else:
                ret[attachment_out.id] = True
        return ret

    def _compute_invoice_partner_id(self, cr, uid, ids, name, unknow_none, context=None):
        ret = {}
        for att in self.browse(cr, uid, ids):
            partners = []
            for invBrws in att.out_invoice_ids:
                invPartner = invBrws.partner_id.id
                if invPartner not in partners:
                    partners.append(invPartner)
            if len(partners) == 1:
                ret[att.id] = partners[0]
        return ret

    def _check_datas_fname(self, cr, uid, ids, context=None):
        context = context or {}
        for att in self.browse(cr, uid, ids, context):
            res = self.search(cr, uid, [('datas_fname', '=', att.datas_fname)])
            if len(res) > 1:
                return False
        return True

    def get_xml_string(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for fattAttInBrws in self.browse(cr, uid, ids, context):
            return fattAttInBrws.ir_attachment_id.get_xml_string()
        return ''

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
        for fatturapa_attachment in self.browse(cr, uid, ids, context):
            try:
                xml_string = self.get_xml_string(cr, uid, [fatturapa_attachment.id])
                xml_file = BytesIO(xml_string)
                recovering_parser = ET.XMLParser(recover=True)
                dom = ET.parse(xml_file, parser=recovering_parser)
                transform = ET.XSLT(xslt)
                newdom = transform(dom)
                res[fatturapa_attachment.id] = ET.tostring(newdom, pretty_print=True)
            except Exception as e:
                _logger.error(e)
                res[fatturapa_attachment.id] = ''
        return res

    def _get_xml_explosion(self, cr, uid, ids, name, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for fatturapa_attachment in self.browse(cr, uid, ids, context):
            attachment_name = []
            customer_invoice_numbers = []
            invoices_total = 0
            invoices_number = 0
            if fatturapa_attachment.ir_attachment_id.datas_fname.lower().endswith('.xml'):
                try:
                    xml_string = self.get_xml_string(cr, uid, [fatturapa_attachment.id])
                    fatt_xml = fatturapa.CreateFromDocument(xml_string)
                    invoices_number = len(fatt_xml.FatturaElettronicaBody)
                    for invoice in fatt_xml.FatturaElettronicaBody:
                        for attach in invoice.Allegati:
                            attachment_name.append(attach.NomeAttachment)
                        customer_invoice_numbers.append(invoice.DatiGenerali.DatiGeneraliDocumento.Numero)
                        invoices_total += float(invoice.DatiGenerali.DatiGeneraliDocumento.ImportoTotaleDocumento)
                except Exception as e:
                    _logger.error(u'{id} Error on {name}: {error}'.format(id=fatturapa_attachment.id, name=fatturapa_attachment.ir_attachment_id.datas_fname, error=e))
            res[fatturapa_attachment.id] = {
                'attachment_list': '\n'.join(attachment_name),
                'customer_invoice_numbers': '\n'.join(customer_invoice_numbers),
                'invoices_total': invoices_total,
                'invoices_number': invoices_number
            }

        return res

    def _get_xml_out_error(self, cr, uid, ids, name, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for att in self.browse(cr, uid, ids, context):
            attachment_list = [attch for attch in att.attachment_list.split('/n')]
            customer_invoice_numbers = [inv for inv in att.customer_invoice_numbers.split('/n')]
            warning = False
            for attachment in attachment_list:
                if '.' in attachment:
                    attachment_name = attachment.split('.')[0]
                    if attachment_name not in customer_invoice_numbers:
                        warning = True

            res[att.id] = warning
        return res

    def show_error(self, cr, uid, ids, context=None):
        raise orm.except_orm(
            "Verificare",
            "Bene il numero di allegati e/o l'importo della fattura")

    _columns = {
        'xml_preview': fields.function(_get_fattura_elettronica_preview, type="text", string="Preview", method=True),
        'ir_attachment_id': fields.many2one(
            'ir.attachment', 'Attachment', required=True, ondelete="cascade"),
        'out_invoice_ids': fields.one2many(
            'account.invoice', 'fatturapa_attachment_out_id',
            string="Out Invoices", readonly=True
        ),
        'has_pdf_invoice_print': fields.function(
            _compute_has_pdf_invoice_print,
            type='boolean',
            string='Has PDF Invoice Print',
            help="True if all the invoices have a printed "
            "report attached in the XML, False otherwise.",
            store=True
        ),
        'invoice_partner_id': fields.function(
            _compute_invoice_partner_id,
            type='many2one',
            string='Customer',
            store=True,
            relation='res.partner'
        ),
        'attachment_list': fields.function(_get_xml_explosion, string="Allegati", type="text", multi='get_xml_explosion', store={
                                    'fatturapa.attachment.out': (lambda self, cr, uid, ids, c={}: ids, ['ir_attachment_id'], 1000),
                                },),
        'customer_invoice_numbers': fields.function(_get_xml_explosion, multi='get_xml_explosion', string="Numero Fatture", type="text", store={
                                    'fatturapa.attachment.out': (lambda self, cr, uid, ids, c={}: ids, ['ir_attachment_id'], 1000),
                                }),
        'invoices_total': fields.function(_get_xml_explosion, multi='get_xml_explosion', string="Totale Fatturato", type="float", store={
                                    'fatturapa.attachment.out': (lambda self, cr, uid, ids, c={}: ids, ['ir_attachment_id'], 1000),
                                }),
        'invoices_number': fields.function(_get_xml_explosion, multi='get_xml_explosion', string="Totale Fatture", type="integer", store={
                                    'fatturapa.attachment.out': (lambda self, cr, uid, ids, c={}: ids, ['ir_attachment_id'], 1000),
                                }),
        'xml_error': fields.function(_get_xml_out_error, 'Possibile anomalia XML', type='boolean', method=True)
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        res = super(FatturaPAAttachment, self).write(cr, uid, ids, vals, context=context)
        userRead = self.pool.get('res.users').read(cr, uid, uid, ['display_name'], context=context)
        user_name = userRead.get('display_name', str(uid))
        if 'datas' in vals and 'message_ids' not in vals:
            for attachment in self.browse(cr, uid, ids):
                attachment.message_post(cr, uid, [attachment.id],
                    subject=_("E-invoice attachment changed"),
                    body=_("User %s uploaded a new e-invoice file") % user_name
                )
        return res

    _constraints = [
        (_check_datas_fname, 'File Already Present.', ['datas_fname']),
    ]


class FatturaAttachments(orm.Model):
    _inherit = "fatturapa.attachments"

    _columns = {
        'is_pdf_invoice_print': fields.boolean(
            help="This attachment contains the PDF report of the linked invoice")
    }
