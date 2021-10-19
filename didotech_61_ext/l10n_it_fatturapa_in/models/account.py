# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
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
import decimal_precision as dp


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'fatturapa_attachment_in_id': fields.many2one(
            'fatturapa.attachment.in', 'FatturaPA Import File',
            ondelete='restrict'),
        'inconsistencies': fields.text('Import Inconsistencies'),
        
        #TODO: Fields imported
        'e_invoice_line_ids': fields.one2many(
            "einvoice.line", "invoice_id", string="Dettaglio Linee",
            readonly=True, copy=False),
        'einvoice_withholding_data_ids': fields.one2many(
            'einvoice.withholding.data', 'invoice_id',
            string='Withholding Datas', readonly=True, copy=False
        )
    }

    def copy(self, cr, uid, ids, value, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        value.update({
            'fatturapa_attachment_in_id': False,
            'inconsistencies': False,
            'e_invoice_line_ids': [],
            'fatturapa_summary_ids': []
        })
        return super(account_invoice, self).copy(cr, uid, ids, value, context)

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if context.get('name_extended_for_xml_invoice_in', False):
            res = []
            for invoice in self.browse(cr, uid, ids, context):
                if invoice.type in ('in_invoice', 'in_refund'):
                    name = u"%s di € %s" % (invoice.partner_id.name, invoice.amount_total)
                    # if invoice.origin:
                    #     name += ', %s' % invoice.origin
                    res.append((invoice.id, name))
            return res

        return super(account_invoice, self).name_get(cr, uid, ids, context)

    def remove_attachment_link(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'fatturapa_attachment_in_id': False}, context)
        return {'type': 'ir.actions.client', 'tag': 'reload'}


class fatturapa_article_code(orm.Model):
    # _position = ['2.2.1.3']
    _name = "fatturapa.article.code"
    _description = 'FatturaPA Article Code'

    _columns = {
        'name': fields.char('Cod Type', size=35),
        'code_val': fields.char('Code Value', size=35),
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Related Invoice line',
            ondelete='cascade', select=True
        ),


        # TODO: This field in V10 has changes it's name
        'e_invoice_line_id': fields.many2one(
            'einvoice.line', 'Related E-Invoice line', readonly=True
        )
    }


class account_invoice_line(orm.Model):
    # _position = [
    #     '2.2.1.3', '2.2.1.6', '2.2.1.7',
    #     '2.2.1.8', '2.1.1.10'
    # ]
    _inherit = "account.invoice.line"

    _columns = {
        'cod_article_ids': fields.one2many(
            'fatturapa.article.code', 'invoice_line_id',
            'Cod. Articles'
        ),
        'service_type': fields.selection([
            ('SC', 'sconto'),
            ('PR', 'premio'),
            ('AB', 'abbuono'),
            ('AC', 'spesa accessoria'),
            ], string="Service Type"),
        'ftpa_uom': fields.char('Fattura Pa Unit of Measure', size=10),
        'service_start': fields.date('Service start at'),
        'service_end': fields.date('Service end at'),
        'discount_rise_price_ids': fields.one2many(
            'discount.rise.price', 'invoice_line_id',
            'Discount and Rise Price Details'
        ),
        
        #TODO: Migrated field
        'fatturapa_attachment_in_id': fields.related(
            'invoice_id', 'fatturapa_attachment_in_id', type='many2one',
            relation='fatturapa.attachment.in', string='E-Invoice Import File'),
    }


class DiscountRisePrice(orm.Model):
    _inherit = "discount.rise.price"
    
    _columns = {
        'e_invoice_line_id': fields.many2one(
            'einvoice.line', 'Related E-Invoice line', readonly=True
        )
    }


class EInvoiceLine(orm.Model):
    _name = 'einvoice.line'

    def _get_line_color(self, cr, uid, ids, name, unknown, context=None):
        context = context or {}
        result = {}

        supplierinfo_model = self.pool['product.supplierinfo']

        for xml_line in self.browse(cr, uid, ids, context):
            product_codes = [article.code_val for article in xml_line.cod_article_ids if len(article.code_val) > 2]
            if product_codes:
                if 'product_ean13' in supplierinfo_model._columns:
                    info_ids = supplierinfo_model.search(cr, uid, [
                        ('name', '=', xml_line.invoice_id.partner_id.id),
                        '|',
                        ('product_code', 'in', product_codes),
                        ('product_ean13', 'in', product_codes)
                    ])
                else:
                    info_ids = supplierinfo_model.search(cr, uid, [
                        ('name', '=', xml_line.invoice_id.partner_id.id),
                        ('product_code', 'in', product_codes)
                    ])

                if info_ids:
                    info = supplierinfo_model.browse(cr, uid, info_ids[0], context)
                    product_tmpl_id = info.product_id.id
                    invoice_line_ids = self.pool['account.invoice.line'].search(cr, uid, [
                        ('product_id.product_tmpl_id', '=', product_tmpl_id),
                        ('invoice_id', '=', xml_line.invoice_id.id)
                    ])
                else:
                    product_ids = self.pool['product.product'].search(cr, uid, [
                        # ('supplier_id', '=', xml_line.invoice_id.partner_id.id),
                        # '|', '|',
                        # ('supplier_code', 'in', product_codes),
                        ('default_code', 'in', product_codes),
                        ('ean13', 'in', product_codes)
                    ])

                    if product_ids:
                        invoice_line_ids = self.pool['account.invoice.line'].search(cr, uid, [
                            ('product_id.id', 'in', product_ids),
                            ('invoice_id', '=', xml_line.invoice_id.id)
                        ])
                    else:
                        invoice_line_ids = []

                if len(invoice_line_ids) == 1:
                    result[xml_line.id] = 'green'
                    continue
                elif len(invoice_line_ids) > 1:
                    result[xml_line.id] = 'brown'
                    continue

            result[xml_line.id] = 'no_color'

        return result

    _columns = {
        'invoice_id': fields.many2one(
            "account.invoice", "Invoice", readonly=True),
        'line_number': fields.integer('Numero Linea', readonly=True),
        'service_type': fields.char('Tipo Cessione Prestazione', readonly=True),
        'cod_article_ids': fields.one2many(
            'fatturapa.article.code', 'e_invoice_line_id',
            'Cod. Articles', readonly=True
        ),
        'name': fields.char("Descrizione", readonly=True),
        'qty': fields.float(
            "Quantita'", readonly=True,
            digits_compute=dp.get_precision('Product UoM')
        ),
        'uom': fields.char("Unita' di misura", readonly=True),
        'period_start_date': fields.date("Data Inizio Periodo", readonly=True),
        'period_end_date': fields.date("Data Fine Periodo", readonly=True),
        'unit_price': fields.float(
            "Prezzo unitario", readonly=True,
            digits_compute=dp.get_precision('Account')
        ),
        'discount_rise_price_ids': fields.one2many(
            'discount.rise.price', 'e_invoice_line_id',
            'Discount and Rise Price Details', readonly=True
        ),
        'total_price': fields.float("Prezzo Totale", readonly=True, digits_compute= dp.get_precision('Account')),
        'tax_amount': fields.float("Aliquota IVA", readonly=True),
        'wt_amount': fields.char("Ritenuta", readonly=True),
        'tax_kind': fields.char("Natura", readonly=True),
        'admin_ref': fields.char("Riferimento amministrazione", readonly=True),
        'other_data_ids': fields.one2many(
            "einvoice.line.other.data", "e_invoice_line_id",
            string="Altri dati gestionali", readonly=True),
        'xml_line_color': fields.function(
            _get_line_color,
            method=True,
            string="Invoice Line",
            type="selection",
            selection=[
                ('no_color', 'None'),
                ('green', 'Green'),
                ('orange', 'Orange'),
                ('brown', 'Brown')
            ],
            store=False
        )
    }


class EInvoiceLineOtherData(orm.Model):
    _name = 'einvoice.line.other.data'

    _columns = {
        'e_invoice_line_id': fields.many2one(
            'einvoice.line', 'Related E-Invoice line', readonly=True
        ),
        'name': fields.char("Tipo Dato", readonly=True),
        'text_ref': fields.char("Riferimento Testo", readonly=True),
        'num_ref': fields.float("Riferimento Numero", readonly=True),
        'date_ref': fields.char("Riferimento Data", readonly=True),
    }


class EInvoiceWithholdingData(orm.Model):
    _name = 'einvoice.withholding.data'

    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice', readonly=True
        ),
        'type': fields.char('Tipo Ritenuta'),
        'amount': fields.float('Importo Ritenuta'),
        'rate': fields.float('Aliquota Ritenuta'),
        'causal': fields.char('Causale Pagamento')
    }
