# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 AgileBG SAGL <http://www.agilebg.com>
#    Copyright (C) 2015 innoviu Srl <http://www.innoviu.com>
#    Copyright (C) 2018-2019 Didotech Srl <http://www.didotech.com>
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
import base64
import logging
import zipfile
from cStringIO import StringIO
from datetime import datetime
from io import BytesIO

import decimal_precision as dp
import lxml.etree as ET
from openerp.modules.module import get_module_resource
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class FatturaPAAttachmentIn(orm.Model):
    _name = "fatturapa.attachment.in"
    _description = "FatturaPA import File"
    _inherits = {'ir.attachment': 'ir_attachment_id'}
    _inherit = ['mail.thread']
    _order = 'id desc'

    def __init__(self, cr, uid):
        res = super(FatturaPAAttachmentIn, self).__init__(cr, uid)
        self.cache_compute_xml_data = {}
        self.cache_get_attachment_fields = {}
        return res

    def dummy_button(self, cr, uid, ids, context=None):
        for invoice_id in ids:
            if invoice_id in self.cache_compute_xml_data:
                del self.cache_compute_xml_data[invoice_id]
        self.write(cr, uid, ids, {}, context)
        return True

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
                res[fatturapa_attachment.id] = '<?xml version="1.0" encoding="UTF-8"?>'
        return res

    def _compute_xml_data(self, cr, uid, ids, name, unknow_none, context=None):
        context = context or {}
        ret = {}
        for att in self.browse(cr, uid, ids, context):
            if att.id in self.cache_compute_xml_data:
                ret[att.id] = self.cache_compute_xml_data[att.id]
                continue

            DDT_number = []
            supplier_invoice_numbers = []
            supplier_invoice_dates = []
            partner_id = False
            invoices_total = 0
            xml_invoice_type = 'TD01'
            invoices_number = 0
            xml_have_attachment = False
            xml_errors = ''
            try:
                fatt = self.pool.get('wizard.import.fatturapa').get_invoice_obj(cr, uid, att)
                cedentePrestatore = fatt.FatturaElettronicaHeader.CedentePrestatore
                partner_id = self.pool.get('wizard.import.fatturapa').getCedPrest(cr, uid, cedentePrestatore)
                invoices_number = len(fatt.FatturaElettronicaBody)
                for invoice_body in fatt.FatturaElettronicaBody:
                    docType = invoice_body.DatiGenerali.DatiGeneraliDocumento.TipoDocumento
                    supplier_invoice_numbers.append(invoice_body.DatiGenerali.DatiGeneraliDocumento.Numero)
                    if invoice_body.DatiGenerali.DatiGeneraliDocumento.Data:
                        data = datetime.strptime(str(invoice_body.DatiGenerali.DatiGeneraliDocumento.Data)[0:10], DEFAULT_SERVER_DATE_FORMAT)
                        supplier_invoice_dates.append(data.strftime("%d/%m/%Y"))
                    invoices_total += float(
                        invoice_body.DatiGenerali.DatiGeneraliDocumento.ImportoTotaleDocumento or 0
                    )
                    for DDT in invoice_body.DatiGenerali.DatiDDT:
                        DDT_number.append(DDT.NumeroDDT)
                    xml_have_attachment = invoice_body.Allegati

                try:
                    xml_invoice_type = str(docType)
                except Exception as e:
                    _logger.error(e)
                    xml_errors = str(e)

            except Exception as e:
                _logger.error(e)
                xml_errors = str(e)

            vals = {
                'xml_invoice_type': xml_invoice_type,
                'xml_supplier_id': partner_id,
                'invoices_number': invoices_number,
                'invoices_total': invoices_total,
                'ddt_number': ','.join(list(set(DDT_number))),
                'supplier_invoice_numbers': ','.join(list(set(supplier_invoice_numbers))),
                'invoices_date': ','.join(list(set(supplier_invoice_dates))),
                'xml_have_attachment': xml_have_attachment,
                'xml_errors': xml_errors
            }

            self.cache_compute_xml_data[att.id] = vals

            ret[att.id] = vals
        return ret

    def _compute_registered(self, cr, uid, ids, name, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ret = {}
        for att in self.browse(cr, uid, ids, context):
            if att.in_invoice_ids and len(att.in_invoice_ids) >= att.invoices_number:
                ret[att.id] = True
            else:
                ret[att.id] = False
        return ret

    def get_attachment(self, cr, uid, ids, context=None):
        # http://localhost:8069/web/webclient/model=ir.attachment&field=datas&id=3534&filename_field=datas_fname
        # http://localhost:8069/web/binary/saveas?session_id=cc586ccfd7394aa5958e49ec2a1d5950&model=ir.attachment&field=datas&id=3534&filename_field=datas_fname
        # http://localhost:8069/web/binary/saveas?session_id=cc586ccfd7394aa5958e49ec2a1d5950&model=ir.attachment&field=datas&id=3534&filename_field=datas_fname
        #openerp.connection.session_id
        return_vals = {
            'type': 'ir.actions.act_url',
            'url': "/web/binary/saveas?session_id=cc586ccfd7394aa5958e49ec2a1d5950&model=fatturapa.attachment.in&field=xml_attachment_datas&id={id}&filename_field=xml_attachment_filename".format(id=ids[0]),
            'target': 'self',
        }
        return return_vals

    def _get_attachment_fields(self, cr, uid, ids, name, unknow_none, context=None):

        res = {}
        for att in self.browse(cr, uid, ids, context):
            # if att.id in self.cache_get_attachment_fields:
            #     res[att.id] = self.cache_get_attachment_fields[att.id]
            #     continue

            res[att.id] = {
                'xml_attachment_datas': False,
                'xml_attachment_filename': '',
            }
            if att.xml_have_attachment:

                supplier_id = att.xml_supplier_id and att.xml_supplier_id.id or False
                name = 'Errore'
                if supplier_id:
                    supplier_ids = self.pool['res.partner'].search(cr, uid, [('id', '=', supplier_id)], context=context)
                    if supplier_ids:
                        name = att.xml_supplier_id.name

                res[att.id] = {
                    'xml_attachment_datas': False,
                    'xml_attachment_filename': u"{}.zip".format(name)
                }
                in_memory_zip = StringIO()
                zf = zipfile.ZipFile(in_memory_zip, "w", zipfile.ZIP_STORED, False)
                zf.debug = 3

                try:
                    fatt = self.pool.get('wizard.import.fatturapa').get_invoice_obj(cr, uid, att)
                except Exception as e:
                    continue

                attachments = False
                for invoice_body in fatt.FatturaElettronicaBody:
                    AttachmentsData = invoice_body.Allegati
                    if AttachmentsData:
                        for attach in AttachmentsData:
                            if not attach.NomeAttachment:
                                raise orm.except_orm(
                                    _('Error!'),
                                    _('Attachment Name is Required')
                                )
                            content = attach.Attachment
                            name = attach.NomeAttachment
                            _attach_dict = {
                                'name': name,
                                'datas': base64.b64encode(str(content)),
                                'datas_fname': name,
                                'description': attach.DescrizioneAttachment or '',
                                'compression': attach.AlgoritmoCompressione or '',
                                'format': attach.FormatoAttachment or '',
                            }
                            attachments = True
                            zf.writestr(_attach_dict['name'], _attach_dict['datas'].decode("base64"))
                if attachments:
                    for zfile in zf.filelist:
                        zfile.create_system = 0

                    if not zf.infolist():
                        zf.writestr('empty', 'empty')

                    for info in zf.infolist():
                        _logger.info(
                                    u"{0}, {1}, {2}, {3}".format(info.filename, info.date_time, info.file_size, info.compress_size))
                    zf.close()
                    in_memory_zip.seek(0)
                    out = in_memory_zip.getvalue()
                    out.encode("base64")
                    res[att.id]['xml_attachment_datas'] = out
                self.cache_get_attachment_fields[att.id] = res[att.id].copy()
        return res

    def _get_ddt_match(self, cr, uid, ids, name, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_picking_obj = self.pool['stock.picking']
        stock_move_obj = self.pool['stock.move']
        ret = {}
        for att in self.browse(cr, uid, ids, context):
            vals = {
                'ddt_match': '',
                'ddt_match_invoices_total': 0,
                'invoice_total_difference_ddt': 0
            }

            ddt_invoice = att.ddt_number
            partner_id = att.xml_supplier_id
            if ddt_invoice and partner_id:
                stock_picking_ids = stock_picking_obj.search(cr, uid, [('type', '=', 'in'), ('state', '=', 'done'), ('invoice_state', '=', '2binvoiced'), ('ddt_in_reference', 'ilike', ddt_invoice), ('partner_id', '=', partner_id.id)], context=context)
                vals['ddt_match'] = u'{0}/{1}'.format(len(stock_picking_ids), len(ddt_invoice.split(',')))
                if stock_picking_ids:
                    stock_move_ids = stock_move_obj.search(cr, uid, [('picking_id', 'in', stock_picking_ids)], context=context)
                    val = 0.0
                    for move in stock_move_obj.browse(cr, uid, stock_move_ids, context):
                        if move.purchase_line_id.taxes_id:
                            val += self.pool.get('account.tax').compute_all(cr, uid, move.purchase_line_id.taxes_id, move.price_unit,
                                                                          move.product_qty, move.picking_id.address_id.id,
                                                                          move.product_id.id, move.partner_id)['total_included']
                        else:
                            val += move.product_qty * move.price_unit

                    vals.update({
                        'ddt_match_invoices_total': val,
                        'invoice_total_difference_ddt': att.invoices_total - val
                    })

            ret[att.id] = vals
        return ret

    def action_create_delivery_invoice(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_picking_obj = self.pool['stock.picking']
        account_invoice_obj = self.pool['account.invoice']
        context = context or {}
        stock_invoice_onshipping_obj = self.pool['stock.invoice.onshipping']
        for att in self.browse(cr, uid, ids, context=context):
            ddt_invoice = att.ddt_number
            partner_id = att.xml_supplier_id
            if ddt_invoice and partner_id:
                stock_picking_ids = stock_picking_obj.search(cr, uid, [('type', '=', 'in'), ('state', '=', 'done'), ('invoice_state', '=', '2binvoiced'), ('ddt_in_reference', 'ilike', ddt_invoice),
                                                                   ('partner_id', '=', partner_id.id)], context=context)
                if stock_picking_ids:
                    ctx = context.copy()
                    ctx['active_ids'] = stock_picking_ids
                    ctx['active_id'] = stock_picking_ids[0]
                    ctx['active_model'] = 'stock.picking'
                    journal_id = stock_invoice_onshipping_obj._get_journal(cr, uid, context=ctx)
                    stock_invoice_onshipping_vals = {
                        'journal_id': journal_id,
                        'group': True,
                        'invoice_date': False
                    }
                    stock_invoice_onshipping_id = stock_invoice_onshipping_obj.create(cr, uid, stock_invoice_onshipping_vals, context=ctx)
                    res = stock_invoice_onshipping_obj.create_invoice(cr, uid, [stock_invoice_onshipping_id], context=ctx)
                    created_invoice_ids = list(set(res.values()))
                    account_invoice_obj.button_reset_taxes(cr, uid, created_invoice_ids, context=context)
                    if len(created_invoice_ids) > 2:
                        raise orm.except_orm(
                            u'Errore',
                            u'Si sono create più di 2 fatture')
                    link_ctx = context.copy()
                    link_ctx['invoice_id'] = created_invoice_ids[0]
                    link_ctx['active_ids'] = [att.id]
                    link_ctx['active_id'] = att.id
                    link_ctx['active_model'] = 'fatturapa.attachment.in'
                    return self.pool['wizard.import.fatturapa'].importFatturaPA(cr, uid, [att.id], link_ctx)

        return True

    def action_view_delivery(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''

        context = context or self.pool['res.users'].context_get(cr, uid)
        # dummy
        self.write(cr, uid, ids, {}, context)

        read = self.read(cr, uid, ids[0], ['ddt_number', 'xml_supplier_id'], context=context)
        context.update({
            'default_type': 'in',
            'contact_display': 'partner_address',
            'search_default_confirmed': 0,
            'search_default_available': 0,
            'search_default_ddt_in_reference': read['ddt_number'],
            'search_default_partner_id': read['xml_supplier_id'] and read['xml_supplier_id'][0]
        })

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree4')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        # compute the number of delivery orders to display
        pick_ids = self.pool['stock.picking'].search(cr, uid, [('type', '=', 'in'), ('state', '!=', 'draft')], context=context)

        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        result['context'] = context
        return result

    _columns = {
        # 'ir_attachment_id': fields.many2one(
        #     'ir.attachment', 'Attachment', required=True),
        'in_invoice_ids': fields.one2many(
            'account.invoice', 'fatturapa_attachment_in_id',
            string="In Invoices", readonly=True),
        # TODO: Imported fields
        'xml_preview': fields.function(_get_fattura_elettronica_preview, type="text", string="Preview", method=True),
        'xml_invoice_type': fields.function(_compute_xml_data, type='selection', multi='compute_xml_data',
                                            selection=[
                                                ('TD01', 'Fattura'),
                                                ('TD02', 'Acconto/Anticipo su fattura'),
                                                ('TD03', 'Acconto/Anticipo su parcella'),
                                                ('TD04', 'Nota di Credito'),
                                                ('TD05', 'Nota di Dedito'),
                                                ('TD06', 'Parcella')], method=True, store=True, string='Invoice Type'),
        'xml_supplier_id': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=False,
                                           string="Supplier", 
                                           relation="res.partner",
                                           type="many2one", store=True),
        'supplier_invoice_numbers': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=True,
                                           string="Invoices number",
                                           type="char", size=2048, store=True),
        'invoices_number': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=True,
                                           string="Invoices number", 
                                           type="integer", store=True),
        'invoices_date': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=True,
                                           string="Invoices Date",
                                           type="char", size=2048, store=True),
        'ddt_number': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=True,
                                           string="DDT number",
                                           type="text", store=True),
        'invoices_total': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=True,
                                           string="Invoices total", 
                                           type="float",
                                           help="Se indicato dal fornitore, Importo totale del documento al "
                 "netto dell'eventuale sconto e comprensivo di imposta a debito "
                 "del cessionario / committente",
                                           store=True,),
        'xml_have_attachment': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=True,
                                           string="Have Attachment",
                                           type="boolean", store=True),
        'xml_errors': fields.function(_compute_xml_data, multi='compute_xml_data',
                                           method=True,
                                           string="Errors",
                                           type="text", store=True),
        'ddt_match': fields.function(_get_ddt_match, multi='get_ddt', method=True,
                                           string="Match DDT",
                                           type="char", size=2048, store=False),
        'ddt_match_invoices_total': fields.function(_get_ddt_match, multi='get_ddt', method=True,
                                     string="Invoices total DDT", digits_compute=dp.get_precision('Account'),
                                     type="float", store=False),
        'invoice_total_difference_ddt': fields.function(_get_ddt_match, multi='get_ddt', method=True,
                                     string="Difference XML / DDT", digits_compute=dp.get_precision('Account'),
                                     type="float", store=False),
        'registered': fields.function(_compute_registered, store=False,
                                           string="Registered", 
                                           type="boolean"),
        'xml_attachment_datas': fields.function(_get_attachment_fields, multi='xml_attachment', method=True, string="XML File", type="binary"),
        'xml_attachment_filename': fields.function(_get_attachment_fields, multi='xml_attachment', method=True, string="XML File Name", type="char"),
        'sdi_id': fields.float('IdSdi', size=12, digits=(12, 0), readonly=True),
        'sdi_date': fields.datetime('DataSdi', readonly=True),
        'office_code': fields.char('Codice Ufficio'),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to")
    }

    def get_xml_string(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for fattAttInBrws in self.browse(cr, uid, ids, context):
            return fattAttInBrws.ir_attachment_id.get_xml_string()
        return ''

    def set_name(self, cr, uid, ids, datas_fname, context=None):
        return {'value': {'name': datas_fname}}

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        einvoice_attachment_ids = []
        for e_invoice in self.browse(cr, uid, ids, context):
            if e_invoice.sdi_id:
                raise orm.except_orm(
                    'Attenzione',
                    "Non è possibile cancellare un XML ricevuto da SDI")
            else:
                einvoice_attachment_ids.append(e_invoice.id)
                e_invoice.ir_attachment_id.unlink()

        return super(FatturaPAAttachmentIn, self).unlink(cr, uid, einvoice_attachment_ids, context)

    def create(self, cr, uid, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if self.search(cr, uid, [('name', '=', values['name'])], context=context):
            raise orm.except_orm(
                'Errore',
                _('Invoice already imported')
            )
        elif self.search(cr, uid, [('name', 'ilike', values['name'][:-4])], context=context):
            raise orm.except_orm(
                'Errore',
                _('Invoice already imported')
            )
        return super(FatturaPAAttachmentIn, self).create(cr, uid, values, context)
