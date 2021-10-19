# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
#    © 2018-2019 Didotech srl (www.didotech.com)
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
from openerp.osv import fields, orm
from validate_email import validate_email


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    def action_cancel(self, cr, uid, ids, context=None):
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.fatturapa_attachment_out_id:
                raise orm.except_orm(
                    'Errore!',
                    'La fattura è già stata esportata cancellare export XML'
                )
        return super(account_invoice, self).action_cancel(cr, uid, ids, context)

    def _dummy_cig(self, cr, uid, ids, fields, args, context=None):
        result = dict.fromkeys(ids, '')
        return result

    def _search_dummy_cig(self, cr, uid, obj, name, domain, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        if domain:
            field = domain[0][0]
            if field == 'cig_function':
                search_key = domain[0][2]
                domain = [('cig', domain[0][1], domain[0][2])]
                related_document_obj = self.pool['fatturapa.related_document_type']
                invoice_ids = self.search(cr, uid, domain, context=context)
                related_document_ids = related_document_obj.search(cr, uid, domain, context=context)
                if related_document_ids:
                    for document in related_document_obj.browse(cr, uid, related_document_ids, context):
                        if document.invoice_id:
                            invoice_ids.append(document.invoice_id.id)
                        if document.invoice_line_id:
                            invoice_ids.append(document.invoice_line_id.invoice_id.id)
                if invoice_ids:
                    res = [('id', 'in', list(set(invoice_ids)))]
        return res

    _columns = {
        'fatturapa_attachment_out_id': fields.many2one(
            'fatturapa.attachment.out', 'E-invoice Export File',
            readonly=True),
        'has_pdf_invoice_print': fields.related('fatturapa_attachment_out_id', 'has_pdf_invoice_print',
                                                type='boolean', relation='fatturapa.attachment.out',
                                                string='Has PDF invoice', readonly=True),
        'xml_preview': fields.related('fatturapa_attachment_out_id', 'xml_preview', type="text", string="Preview", readonly=True),
        'cig_function': fields.function(_dummy_cig, type='char', string='CIG', readonly=True, method=True, fnct_search=_search_dummy_cig),

    }

    def check_stamp(self, cr, uid, invoice, context):
        product_ids = []
        for stamp in invoice.company_id.product_stamp_ids:
            product_ids.append(stamp.id)

        if product_ids:
            account_invoice_line_obj = self.pool['account.invoice.line']
            account_invoice_line_ids = account_invoice_line_obj.search(cr, uid, [('product_id', 'in', product_ids), ('invoice_id', '=', invoice.id)], context=context)
            if account_invoice_line_ids:
                return False
        return not invoice.virtual_stamp

    def invoice_need_stamp(self, cr, uid, invoice, context):
        need_stamp = False
        if invoice.fiscal_position and invoice.fiscal_position.virtual_stamp:
            for tax_line in invoice.tax_line:
                if tax_line.base > 77.47 and tax_line.amount == 0.0:
                    need_stamp = True
        return need_stamp

    def invoice_validate_check(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(account_invoice, self).invoice_validate_check(cr, uid, ids, context)
        show_except = not context.get('no_except', False)
        if not res:
            return res
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.type in ['out_invoice', 'out_refund']:
                e_invoice_check = False

                # check bollo in fattura
                need_stamp = self.invoice_need_stamp(cr, uid, invoice, context)

                if need_stamp:
                    # here need to check
                    if self.check_stamp(cr, uid, invoice, context):
                        if show_except:
                            raise orm.except_orm(
                                u'Errore',
                                u'Manca Marca da Bollo')
                        else:
                            return False

                if not invoice.partner_id.electronic_invoice_subjected:
                    return True
                if invoice.partner_id.vat and invoice.partner_id.vat[0:2] == 'IT':
                    partner = invoice.partner_id
                    if partner.ipa_code or partner.codice_destinatario or partner.pec_destinatario:
                        if partner.codice_destinatario and len(partner.codice_destinatario) not in [6, 7]:
                            if show_except:
                                raise orm.except_orm(
                                    u'Errore',
                                    u'Codice Destinatatio di lunghezza errata')
                            else:
                                return False
                        if partner.pec_destinatario and not validate_email(partner.pec_destinatario):
                            if show_except:
                                raise orm.except_orm(
                                    u'Errore',
                                    u'Email Non in formato valido')
                            else:
                                return False
                        e_invoice_check = True
                    else:
                        if show_except:
                            raise orm.except_orm(
                                u'Errore',
                                u'Mancano i Dati per Invio Fattura Elettronica')
                        else:
                            return False
                    if ' ' in invoice.partner_id.vat:
                        if show_except:
                            raise orm.except_orm(
                                u'Errore',
                                u'Spazi Nella Partita Iva')
                        else:
                            return False
                if invoice.payment_term:
                    if invoice.payment_term.fatturapa_pt_id and invoice.payment_term.fatturapa_pm_id:
                        e_invoice_check = True
                    else:
                        if show_except:
                            raise orm.except_orm(
                                u'Errore',
                                u'Mancano i Dati per Sulla Modalità di pagamento')
                        e_invoice_check = False
                if e_invoice_check:
                    return res
                return False

        return res

    # def preventive_checks(self, cr, uid, ids, context={}):
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     for invoiceBrws in self.browse(cr, uid, ids, context):
    #         for line in invoiceBrws.invoice_line:
    #             if '\n' in line.name:
    #                 raise except_osv(
    #                     _('Error'),
    #                     _("Invoice line [%s] must not contain new line character") % line.name
    #                 )

    def copy(self, cr, uid, ids, defaults, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        defaults['fatturapa_attachment_out_id'] = False
        return super(account_invoice, self).copy(cr, uid, ids, defaults, context)

    def action_move_force_recreate(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        account_move_obj = self.pool['account.move']
        move_ids = []  # ones that we will need to remove
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.move_id:
                move_ids.append(invoice.move_id.id)
                self.write(cr, uid, invoice.id, {'move_id': False, 'internal_number': invoice.number}, context)
        if move_ids:
            account_move_obj.button_cancel(cr, uid, move_ids, context=context)
            account_move_obj.unlink(cr, uid, move_ids, context=context)

        self.button_reset_taxes(cr, uid, ids, context)
        for invoice_id in ids:
            context['force_invoice_recreate'] = True
            self.action_move_create(cr, uid, [invoice_id], context)
            self.action_number(cr, uid, [invoice_id], context)
        return True

    # def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
    #     new_args = []
    #     for arg in args:
    #         new_args.append(arg)
    #     res = super(account_invoice, self).search(cr, uid, new_args, offset, limit, order, context, count)
    #
    #     return res
