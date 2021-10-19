# -*- coding: utf-8 -*-
# © 2017 Didotech srl (www.didotech.com)

from openerp.osv import fields, orm
import decimal_precision as dp

import logging
import os
from collections import OrderedDict

import netsvc
import xmltodict
from openerp.osv import orm

import base64
_logger = logging.getLogger(__name__)


wf_service = netsvc.LocalService("workflow")


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    _columns = {
        'inconsistencies': fields.text('Import Inconsistencies'),
    }

    def load_orders(self, cr, uid, path=False, context=None):
        processed_dir_name = 'processed'
        black_list = (
            '.DS_Store',
            processed_dir_name
        )
        context = context or self.pool['res.users'].context_get(cr, uid)
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        context['invoice_import_price'] = company.invoice_import_price

        path = path or company.invoice_import_path
        if not path:
            return False
        processed_dir = os.path.join(path, processed_dir_name)
        if not os.path.isdir(processed_dir):
            os.mkdir(processed_dir)
        created_invoice_ids = []
        for xml_order_file_name in os.listdir(path):
            context['inconsistencies'] = ''
            if xml_order_file_name not in black_list:
                xml_order_file = os.path.join(path, xml_order_file_name)
                if os.path.isfile(xml_order_file):
                    new_invoice_id = False
                    with open(xml_order_file) as xml_order:
                        _logger.info(u"Import file {file}".format(file=xml_order_file_name))
                        try:
                            new_invoice_id = self.create_external(cr, uid, xmltodict.parse(xml_order, process_namespaces=True), company, context)
                        except Exception as error:
                            _logger.error(
                                u"Error on Import/Creation: {0}".format(error)
                            )
                    os.rename(xml_order_file, os.path.join(processed_dir, xml_order_file_name))
                    _logger.info(u"Moved file: {file} to directory {dir}".format(file=xml_order_file_name, dir=processed_dir))
                    if new_invoice_id:
                        cr.commit()
                        _logger.info(u"Moved file: {file} created Invoice {invoice_id}".format(file=xml_order_file_name,
                                                                                     invoice_id=new_invoice_id))
                        created_invoice_ids.append(new_invoice_id)
                        if company.invoice_import_auto_confirm:
                            try:
                                wf_service.trg_validate(uid, 'account.invoice', new_invoice_id, 'invoice_open', cr)
                            except Exception as error:
                                _logger.error(
                                    u"Error: {0}".format(error)
                                )
        if created_invoice_ids:
            created_invoice_draft_ids = self.search(cr, uid, [('id', 'in', created_invoice_ids), ('state', '=', 'draft')], context=context)
            self.button_reset_taxes(cr, uid, created_invoice_draft_ids, context=context)
        return True

    def import_xml_invoice(self, cr, uid, ids, context=None):
        self.load_orders(cr, uid, path=False, context=context)
        return True

    def partner_from_address_data(self, cr, uid, addresses, context):

        def get_address_values(cr, uid, address_values, context):
            context = context or self.pool['res.users'].context_get(cr, uid)
            context.update({'lang': 'it_IT'})

            province_ids = self.pool['res.province'].search(cr, uid, [
                ('code', '=', address_values['Provincia'])
            ], context=context)

            country_ids = self.pool['res.country'].search(cr, uid, [
                ('name', '=', address_values['Nazione'])
            ], context=context)

            return {
                'type': 'default',
                'street': address_values['Indirizzo'],
                'zip': address_values['CAP'],
                'city': address_values['Comune'],
                'province': province_ids and province_ids[0] or False,
                'country_id': country_ids and country_ids[0] or False,
                'active': True,
            }

        partner_model = self.pool['res.partner']
        vat = False
        if addresses['DatiAnagrafici'].get('IdFiscaleIVA', False):
            vat = addresses['DatiAnagrafici']['IdFiscaleIVA']['IdCodice']
        cf = addresses['DatiAnagrafici'].get('CodiceFiscale', False)
        if not (vat or cf):
            if context.get('inconsistencies'):
                context['inconsistencies'] += '\n'
                context['inconsistencies'] += "Manca la P.IVA"
            _logger.error("Missing VAT")
            return False
        if vat:
            partner_ids = partner_model.search(cr, uid, [('vat', '=', vat)], context=context)
            if not partner_ids:
                if not addresses['DatiAnagrafici']['IdFiscaleIVA']['IdPaese']:
                    raise orm.orm_exception('Manda ID Paese nella partita iva')
                if addresses['DatiAnagrafici']['IdFiscaleIVA']['IdPaese'][0:2] != \
                        addresses['DatiAnagrafici']['IdFiscaleIVA']['IdCodice'][0:2]:
                    vat = addresses['DatiAnagrafici']['IdFiscaleIVA']['IdPaese'] + \
                          addresses['DatiAnagrafici']['IdFiscaleIVA']['IdCodice']
                partner_ids = partner_model.search(cr, uid, [('vat', '=', vat)], context=context)
        else:
            partner_ids = partner_model.search(cr, uid, [('fiscalcode', '=', cf)], context=context)
        if not partner_ids and vat:
            partner_ids = partner_model.search(cr, uid, [('property_customer_ref', '=', vat)], context=context)

        if partner_ids:
            return partner_ids[0]
        else:
            address_values = [(0, False, get_address_values(cr, uid, addresses['Sede'], context))]

            partner_values = {
                'name': addresses['DatiAnagrafici']['Anagrafica']['Denominazione'] or addresses[0]['Name'] + ' ' + addresses[0]['Surname'],
                'address': address_values,
                'external_id': False,
                'property_customer_ref': False,
                'customer': True
            }

        if vat:
            country_code, vat_number = partner_model._split_vat(vat)
            if partner_model.simple_vat_check(cr, uid, country_code, vat_number, context=context):
                partner_values.update({'vat': vat})
            else:
                partner_values.update({'property_customer_ref': vat})
        if cf:
            partner_values.update({
                'fiscalcode': cf,
                'individual': True
            })

        try:
            partner_id = partner_model.create(cr, uid, partner_values, context)
        except Exception as error:
            partner_id = 1  # force creation of invoice
            if context.get('inconsistencies'):
                context['inconsistencies'] += '\n'
                context['inconsistencies'] += "Non si è riusciti al creare il cliente"
                context['inconsistencies'] += '\n'
                context['inconsistencies'] += u"{} per l'errore: '{}'".format(partner_values['name'], error)

            _logger.error(
                u"Error on Import/Creation: {0}".format(error)
            )
        return partner_id

    def order_lines_from_line_data(self, cr, uid, partner_id, invoice_data, order_line_values, context):
        context = context or self.pool['res.users'].context_get(cr, uid)
        account_analytic_account_obj = self.pool['account.analytic.account']
        product_model = self.pool['product.product']
        account_tax_model = self.pool['account.tax']
        fiscal_position_model = self.pool['account.fiscal.position']
        account_invoice_line_model = self.pool['account.invoice.line']

        order_lines = []

        if isinstance(order_line_values, (dict, OrderedDict)):
            order_line_values = [order_line_values]

        invoice_import_autocreate_product = context.get('invoice_import_autocreate_product', False)

        for line_values in order_line_values:
            # product_id = product_model.get_create(cr, uid, line_values, context)
            # product = product_model.browse(cr, uid, product_id, context)
            quantity = float(line_values.get('Quantita', 0.0))
            name = line_values['Descrizione'] or False
            price_unit = 0

            if context.get('invoice_import_price', 'normal') == 'normal':
                price_unit = line_values['PrezzoUnitario']
            elif quantity != 0:
                price_unit = float(line_values['PrezzoTotale']) / quantity
            product_id = False
            new_line_value = account_invoice_line_model.default_get(cr, uid, ['account_id', 'invoice_line_tax_id'], context)

            invoice_line_tax_id = []
            if line_values['AliquotaIVA']:
                account_tax_ids = account_tax_model.search(
                    cr, uid,
                    [
                        ('type_tax_use', 'in', ('sale', 'all')),
                        ('amount', '=', float(line_values['AliquotaIVA']) / 100),
                    ], context=context)
                if len(account_tax_ids) == 1:
                    invoice_line_tax_id = [(6, 0, [account_tax_ids[0]])]

            if line_values.get('CodiceArticolo', False):
                default_code = line_values['CodiceArticolo']['CodiceValore']
                product_ids = self.pool['product.product'].search(cr, uid, [('default_code', '=', default_code)], context=context)
                if product_ids:
                    product_id = product_ids[0]
                elif invoice_import_autocreate_product:
                    product_vals = {
                        'default_code': default_code,
                        'name': name
                    }
                    if invoice_line_tax_id:
                        product_vals.update({'taxes_id': invoice_line_tax_id})
                    product_id = product_model.create(cr, uid, product_vals, context)
                else:
                    product_id = False

                new_line_value.update(account_invoice_line_model.product_id_change(cr, uid, [], product_id, False, quantity, name, invoice_data['type'], partner_id,
                                          invoice_data['fiscal_position'], price_unit, invoice_data['address_invoice_id'],
                                          invoice_data['currency_id'], context, invoice_data['company_id']).get('value'))
                new_line_value['product_id'] = product_id

            if line_values.get('AltriDatiGestionali', False):
                datos = line_values['AltriDatiGestionali']
                if isinstance(datos, (dict, OrderedDict)):
                    datos = [datos]
                description = []
                IdPratica = False
                IdSplit = False
                note = False
                for dato in datos:
                    TipoDato = dato.get('TipoDato', '')
                    RiferimentoTesto = dato.get('RiferimentoTesto', '')
                    if not RiferimentoTesto:
                        continue
                    if TipoDato == 'DettaglioDescrizione':
                        note = True
                        description.append(RiferimentoTesto)
                    elif TipoDato == 'DettaglioDescrizioneAltraLingua' and not note:
                        description.append(RiferimentoTesto)
                    elif TipoDato == 'VsRiferimento':
                        description.append(u'Vs Riferimento {0}'.format(RiferimentoTesto))
                    elif TipoDato == 'IdPratica':
                        IdPratica = RiferimentoTesto
                    elif TipoDato == 'IdSplit':
                        IdSplit = RiferimentoTesto
                if IdPratica:
                    project_name = IdPratica
                    if IdSplit:
                        project_name += u'/{0}'.format(IdSplit)
                    analytic_account_ids = account_analytic_account_obj.search(cr, uid, [('name', '=', project_name)], limit=1, context=context)
                    new_line_value['account_analytic_id'] = analytic_account_ids and analytic_account_ids[0]
                if description:
                    new_line_value['note'] = '\n'.join(description)

            if name:
                new_line_value['name'] = name
            new_line_value.update({
                'quantity': quantity,
                'price_unit': price_unit,
            })

            if product_id and new_line_value.get('invoice_line_tax_id', False) and not invoice_line_tax_id:
                new_line_value['invoice_line_tax_id'] = [(6, 0, new_line_value.get('invoice_line_tax_id'))]
            else:
                new_line_value['invoice_line_tax_id'] = invoice_line_tax_id

            # if product_id and new_line_value.get('invoice_line_tax_id', False):
            #     # [(6, 0, [1L])]
            #     # [(6, 0, [16])]
            #     new_line_value['invoice_line_tax_id'] = [(6, 0, new_line_value.get('invoice_line_tax_id'))]
            # else:
            #     account_tax_ids = account_tax_model.search(
            #         cr, uid,
            #         [
            #             ('type_tax_use', 'in', ('sale', 'all')),
            #             ('amount', '=', float(line_values['AliquotaIVA']) / 100),
            #         ], context=context)
            #     if account_tax_ids:
            #         new_line_value['invoice_line_tax_id'] = [(6, 0, [account_tax_ids[0]])]

            order_lines.append(new_line_value)

        return order_lines

    def create_external_hook(self, cr, uid, values, FatturaElettronicaBody, context=None):
        return values

    def get_payment_term(self, cr, uid, payment_type, payment_mode, context):
        payment_term_ids = self.pool['account.payment.term'].search(
            cr, uid, [('fatturapa_pt_id', '=', payment_type), ('fatturapa_pm_id', '=', payment_mode)], context=context)

        if payment_term_ids:
            return payment_term_ids[0]
        else:
            if context.get('inconsistencies'):
                context['inconsistencies'] += '\n'
                context['inconsistencies'] += "Non son riuscito a creare il termine di pagamento"
                context['inconsistencies'] += '\n'
                context['inconsistencies'] += u"{} '{}'".format(payment_type, payment_mode)
            return False

    def create_external(self, cr, uid, values, company, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        FatturaElettronicaBody = values[values.keys()[0]]['FatturaElettronicaBody']
        document_type = FatturaElettronicaBody['DatiGenerali']['DatiGeneraliDocumento']['TipoDocumento']
        internal_number = FatturaElettronicaBody['DatiGenerali']['DatiGeneraliDocumento']['Numero']

        invoice_import_autocreate_product = company.invoice_import_autocreate_product
        context['invoice_import_autocreate_product'] = invoice_import_autocreate_product
        if document_type == 'TD01':
            context.update({
                'default_type': 'out_invoice',
                'type': 'out_invoice',
                'journal_type': 'sale'
            })
        else:
            context.update({
                'default_type': 'out_refund',
                'type': 'out_refund',
                'journal_type': 'sale_refund'
            })

        if internal_number:
            invoice_ids = self.search(cr, uid, ['|', '|', ('internal_number', '=', internal_number), ('number', '=', internal_number), ('origin', '=', internal_number)], context=context)
            invoice_ids = self.search(cr, uid, [('id', 'in', invoice_ids), ('type', '=', context['type'])])
            if invoice_ids:
                _logger.error(
                    u"Error: Exist just an invoice {0}, skipped".format(internal_number)
                )
                return False

        partner_id = self.partner_from_address_data(cr, uid, values[values.keys()[0]]['FatturaElettronicaHeader']['CessionarioCommittente'], context)
        if not partner_id:
            return False
        account_invoice_values = self.default_get(cr, uid, ['type', 'journal_id', 'currency_id', 'company_id'], context=context)
        date_invoice = FatturaElettronicaBody['DatiGenerali']['DatiGeneraliDocumento']['Data'][0:10]

        note = FatturaElettronicaBody['DatiGenerali']['DatiGeneraliDocumento'].get('Causale', '')

        payment_type = False
        if FatturaElettronicaBody['DatiPagamento']:
            payment_type = self.get_payment_term(cr, uid, FatturaElettronicaBody['DatiPagamento']['CondizioniPagamento'], FatturaElettronicaBody['DatiPagamento']['DettaglioPagamento']['ModalitaPagamento'], context)

        account_invoice_values.update(self.onchange_partner_id(cr, uid, [], 'out_invoice', partner_id, date_invoice, False, False, 1)['value'])
        account_invoice_values['partner_id'] = partner_id
        account_invoice_values['comment'] = ''

        if internal_number:
            account_invoice_values['comment'] += u"Riferimento interno {0} \n".format(internal_number)
            account_invoice_values['origin'] = internal_number
            if company.invoice_set_number:
                account_invoice_values['internal_number'] = internal_number

        if note:
            account_invoice_values['comment'] += note
        if payment_type:
            account_invoice_values['payment_type'] = payment_type
        if date_invoice:
            account_invoice_values['date_invoice'] = date_invoice

        context.update({'type': account_invoice_values['type']})
        invoice_lines = self.order_lines_from_line_data(cr, uid, partner_id, account_invoice_values, FatturaElettronicaBody['DatiBeniServizi']['DettaglioLinee'], context)

        account_invoice_values.update({
            'invoice_line': [(0, False, line) for line in invoice_lines],

        })

        account_invoice_values = self.create_external_hook(cr, uid, account_invoice_values, FatturaElettronicaBody, context)  # hook function for possible extention

        if FatturaElettronicaBody.get('Allegati', False):
            # AttachModel = self.pool['fatturapa.attachments']
            AttachDoc = FatturaElettronicaBody['Allegati']

            Attachment = AttachDoc['Attachment']
            NomeAttachment = AttachDoc['NomeAttachment']
            if '.pdf' not in NomeAttachment:
                NomeAttachment = NomeAttachment + '.pdf'
            fatturapa_attachments_vals = {
                'name': NomeAttachment,
                'datas': base64.b64decode(str(Attachment)),
                'datas_fname': NomeAttachment,
                'description': AttachDoc.get('DescrizioneAttachment', ''),
                'compression': AttachDoc.get('AlgoritmoCompressione', ''),
                'format': AttachDoc.get('FormatoAttachment', ''),
                'is_pdf_invoice_print': True
                # 'invoice_id': invoice_id,
            }
            account_invoice_values.update({
                'fatturapa_doc_attachments': [(0, False, fatturapa_attachments_vals)]
            })
            if context.get('inconsistencies'):
                account_invoice_values.update({'inconsistencies': context['inconsistencies']})
            # AttachModel.create(cr, uid, fatturapa_attachments_vals, context=context)

        invoice_id = self.create(cr, uid, account_invoice_values, context)
        return invoice_id

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if 'fiscal_position' in vals:
            fiscal_position_id = vals['fiscal_position']
            for invoice in self.browse(cr, uid, ids, context):
                if invoice.partner_id.property_account_position.id != fiscal_position_id:
                    invoice.partner_id.write({'property_account_position': fiscal_position_id})
        return super(AccountInvoice, self).write(cr, uid, ids, vals, context=context)