# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
#    Copyright (C) 2020 Didotech srl
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

from openerp.osv import fields
from openerp.osv import orm


RELATED_DOCUMENT_TYPES = {
    'order': 'DatiOrdineAcquisto',
    'contract': 'DatiContratto',
    'agreement': 'DatiConvenzione',
    'reception': 'DatiRicezione',
    'invoice': 'DatiFattureCollegate',
}


class AccountJournal(orm.Model):
    _inherit = 'account.journal'

    _columns = {
        'fattura_pa': fields.boolean('Fattura PA'),
        'doc_type_id': fields.many2one(
            'fatturapa.document_type', string="Document Type")
    }


class fatturapa_format(orm.Model):
    # _position = ['1.1.3']
    _name = "fatturapa.format"
    _description = 'FatturaPA Format'

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=5),
    }


class fatturapa_document_type(orm.Model):
    # _position = ['2.1.1.1']
    _name = "fatturapa.document_type"
    _description = 'FatturaPA Document Type'

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=4),
        'active': fields.boolean(string='Active', default=True)
    }

    def get_document_type(self, cr, uid, context=None):
        type_ids = self.search(cr, uid, [('active', '=', True)], context=context)
        return [
            (docu_type.code, docu_type.name)
            for docu_type in self.browse(cr, uid, type_ids, context=context)
        ]


class fatturapa_payment_term(orm.Model):
    # _position = ['2.4.1']
    _name = "fatturapa.payment_term"
    _description = 'FatturaPA Payment Term'

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=4),
    }

    _order = "code"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        result = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.code:
                result.append((line.id, u'[{0}] {1}'.format(line.code, line.name)))
            else:
                result.append((line.id, line.name))
        return result


class fatturapa_payment_method(orm.Model):
    # _position = ['2.4.2.2']
    _name = "fatturapa.payment_method"
    _description = 'FatturaPA Payment Method'

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=4),
    }

    _order = "code"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        result = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.code:
                result.append((line.id, u'[{0}] {1}'.format(line.code, line.name)))
            else:
                result.append((line.id, line.name))
        return result


#  used in fatturaPa import
class fatturapa_payment_data(orm.Model):
    # _position = ['2.4.2.2']
    _name = "fatturapa.payment.data"
    _description = 'FatturaPA Payment Data'

    _columns = {
        #  2.4.1
        'payment_terms': fields.many2one(
            'fatturapa.payment_term', string="FatturaPA Payment Method"),
        #  2.4.2
        'payment_methods': fields.one2many(
            'fatturapa.payment.detail', 'payment_data_id',
            'Payments Details'
        ),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True),
    }


class fatturapa_payment_detail(orm.Model):
    # _position = ['2.4.2']
    _name = "fatturapa.payment.detail"
    _columns = {
        'recipient': fields.char('Recipient', size=200),
        'fatturapa_pm_id': fields.many2one(
            'fatturapa.payment_method', string="FatturaPA Payment Method"),
        'payment_term_start': fields.date('Payment Term Start'),
        'payment_days': fields.integer('Payment Term Days'),
        'payment_due_date': fields.date('Payment due Date'),
        'payment_amount': fields.float('Payment Amount'),
        'post_office_code': fields.char('Post Office Code', size=20),
        'recepit_name': fields.char("Recepit payment partner contact", size=64),
        'recepit_surname': fields.char("Recepit payment partner contact", size=64),
        'recepit_cf': fields.char("Recepit payment partner contact", size=64),
        'recepit_title': fields.char("Recepit payment partner contact", size=64),
        'payment_bank_name': fields.char("Bank name", size=64),
        'payment_bank_iban': fields.char("IBAN", size=64),
        'payment_bank_abi': fields.char("ABI", size=64),
        'payment_bank_cab': fields.char("CAB", size=64),
        'payment_bank_bic': fields.char("BIC", size=64),
        'payment_bank': fields.many2one(
            'res.partner.bank', string="Payment Bank"),
        'prepayment_discount': fields.float('Prepayment Discount'),
        'max_payment_date': fields.date('Maximum date for Payment'),
        'penalty_amount': fields.float('Amount of Penality'),
        'penalty_date': fields.date('Effective date of Penality'),
        'payment_code': fields.char('Payment code', size=64),
        'account_move_line_id': fields.many2one(
            'account.move.line', string="Payment Line"),
        'payment_data_id': fields.many2one(
            'fatturapa.payment.data', 'Related payments Data',
            ondelete='cascade', select=True),
    }


#  used in fatturaPa export
class account_payment_term(orm.Model):
    # _position = ['2.4.2.2']
    _inherit = 'account.payment.term'

    _columns = {
        'fatturapa_pt_id': fields.many2one(
            'fatturapa.payment_term', string="FatturaPA Payment Term"),
        'fatturapa_pm_id': fields.many2one(
            'fatturapa.payment_method', string="FatturaPA Payment Method"),
    }


class fatturapa_fiscal_position(orm.Model):
    # _position = ['2.1.1.7.7', '2.2.1.14']
    _name = "fatturapa.fiscal_position"
    _description = 'FatturaPA Fiscal Position'

    _columns = {
        'name': fields.char('Description', size=128),
        'code': fields.char('Code', size=4)
    }


class welfare_fund_type(orm.Model):
    # _position = ['2.1.1.7.1']
    _name = "welfare.fund.type"
    _description = 'welfare fund type'

    _columns = {
        'name': fields.char('name', size=64),
        'description': fields.char('description', size=128),
    }


class welfare_fund_data_line(orm.Model):
    # _position = ['2.1.1.7']
    _name = "welfare.fund.data.line"
    _description = 'FatturaPA Welfare Fund Data'

    def _non_taxable_nature(self, cr, uid, context=None):
        return self.pool['italy.ade.tax.nature'].get_non_taxable_nature(cr, uid, context=context)


    _columns = {
        'name': fields.many2one(
            'welfare.fund.type', string="Welfare Fund Type"),
        'fund_nature': fields.selection(_non_taxable_nature, string="Non taxable nature"),
        'welfare_rate_tax': fields.float('Welfare Rate tax'),
        'welfare_amount_tax': fields.float('Welfare Amount tax'),
        'welfare_taxable': fields.float('Welfare Taxable'),
        'welfare_Iva_tax': fields.float('Welfare  tax'),
        'subjected_withholding': fields.char(
            'Subjected at Withholding', size=2),
        'pa_line_code': fields.char('PA Code for this record', size=20),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True
        ),
    }


class discount_rise_price(orm.Model):
    # _position = ['2.1.1.8', '2.2.1.10']
    _name = "discount.rise.price"
    _description = 'FatturaPA Discount Rise Price Data'

    _columns = {
        'name': fields.selection(
            [('SC', 'Discount'), ('MG', 'Rise Price')], 'Type'),
        'percentage': fields.float('Percentage'),
        'amount': fields.float('Amount'),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True
        ),
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Related Invoice line',
            ondelete='cascade', select=True
        ),
    }


class fatturapa_related_document_type(orm.Model):
    # _position = ['2.1.2', '2.2.3', '2.1.4', '2.1.5', '2.1.6']
    _name = 'fatturapa.related_document_type'
    _description = 'FatturaPA Related Document Type'

    _columns = {
        'type': fields.selection(
            [
                ('order', 'Order'),
                ('contract', 'Contract'),
                ('agreement', 'Agreement'),
                ('reception', 'Reception'),
                ('invoice', 'Related Invoice')
            ],
            'Document Type', required=True
        ),
        'name': fields.char('DocumentID', size=20, required=True),
        'lineRef': fields.integer('LineRef'),
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Related Invoice Line',
            ondelete='cascade', select=True),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True),
        'date': fields.date('Date'),
        'numitem': fields.char('NumItem', size=20),
        'code': fields.char('Order Agreement Code', size=100),
        'cig': fields.char('CIG Code', size=15),
        'cup': fields.char('CUP Code', size=15),
    }

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        if vals.get('invoice_line_id'):
            line_obj = self.pool.get('account.invoice.line')
            line = line_obj.browse(
                cr, uid, vals['invoice_line_id'], context=context)
            vals['lineRef'] = line.sequence
        return super(fatturapa_related_document_type, self).\
            create(cr, uid, vals, context)


class faturapa_activity_progress(orm.Model):
    # _position = ['2.1.7']
    _name = "faturapa.activity.progress"

    _columns = {
        'fatturapa_activity_progress': fields.integer('Activity Progress'),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True)
    }


class fattura_attachments(orm.Model):
    # _position = ['2.5']
    _name = "fatturapa.attachments"
    _description = "FatturaPA attachments"
    _inherits = {'ir.attachment': 'ir_attachment_id'}

    _columns = {
        'ir_attachment_id': fields.many2one(
            'ir.attachment', 'Attachment', required=True, ondelete="cascade"),
        'compression': fields.char('Compression', size=10),
        'format': fields.char('Format', size=10),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True),
        'company_id': fields.many2one(
            'res.company', 'Related Company',
            ondelete='cascade', select=True)
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('invoice_id', False):
            vals.update({
                'res_id': vals.get('invoice_id', False),
                'res_model': 'account.invoice'
            })
        elif vals.get('company_id', False):
            vals.update({
                'res_id': vals.get('company_id', False),
                'res_model': 'res.company'
            })
        result = super(fattura_attachments, self).create(cr, uid, vals, context)
        return result


class fatturapa_related_ddt(orm.Model):
    # _position = ['2.1.2', '2.2.3', '2.1.4', '2.1.5', '2.1.6']
    _name = 'fatturapa.related_ddt'
    _description = 'FatturaPA Related DdT'

    _columns = {
        'name': fields.char('DocumentID', size=20, required=True),
        'date': fields.date('Date'),
        'lineRef': fields.integer('LineRef'),
        'invoice_line_id': fields.many2one(
            'account.invoice.line', 'Related Invoice Line',
            ondelete='cascade', select=True),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True),
    }

    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        if vals.get('invoice_line_id'):
            line_obj = self.pool.get('account.invoice.line')
            line = line_obj.browse(
                cr, uid, vals['invoice_line_id'], context=context)
            vals['lineRef'] = line.sequence
        return super(fatturapa_related_ddt, self).\
            create(cr, uid, vals, context)


class account_invoice_line(orm.Model):
    # _position = ['2.2.1']
    _inherit = "account.invoice.line"

    _columns = {
        'related_documents': fields.one2many(
            'fatturapa.related_document_type', 'invoice_line_id',
            'Related Documents Type'
        ),
        'ftpa_related_ddts': fields.one2many(
            'fatturapa.related_ddt', 'invoice_line_id',
            'Related DdT'
        ),
        'admin_ref': fields.char('Administration ref.', size=20),
        'discount_rise_price_ids': fields.one2many(
            'discount.rise.price', 'invoice_line_id',
            'Discount and Rise Price Details', copy=False
        ),
        'ftpa_line_number': fields.integer("Line number", readonly=True, copy=False),
    }


class faturapa_summary_data(orm.Model):
    # _position = ['2.2.2']
    _name = "faturapa.summary.data"

    def _non_taxable_nature(self, cr, uid, context=None):
        return self.pool['italy.ade.tax.nature'].get_non_taxable_nature(cr, uid, context=context)

    _columns = {
        'tax_rate': fields.float('Tax Rate'),
        'non_taxable_nature': fields.selection(_non_taxable_nature, string="Non taxable nature"),
        'incidental charges': fields.float('Incidental Charges'),
        'rounding': fields.float('Rounding'),
        'amount_untaxed': fields.float('Amount untaxed'),
        'amount_tax': fields.float('Amount tax'),
        'payability': fields.selection([
            ('I', 'Immediate payability'),
            ('D', 'Deferred payability'),
            ('S', 'Split payment'),
        ], string="VAT payability"),
        'law_reference': fields.char(
            'Law reference', size=100),
        'invoice_id': fields.many2one(
            'account.invoice', 'Related Invoice',
            ondelete='cascade', select=True)
    }


class account_invoice(orm.Model):
    # _position = ['2.1', '2.2', '2.3', '2.4', '2.5']
    _inherit = "account.invoice"
    _columns = {
        'protocol_number': fields.char('Protocol Number', size=64),
        # 1.2 -- partner_id
        #  1.3
        'tax_representative_id': fields.many2one(
            'res.partner', string="Tax Rapresentative"),
        #  1.4 company_id
        #  1.5
        'intermediary': fields.many2one(
            'res.partner', string="Intermediary"),
        #  1.6
        'sender': fields.selection(
            [('CC', 'assignee / partner'), ('TZ', 'third person')], 'Sender'),
        #  2.1.1.1
        'doc_type': fields.many2one(
            'fatturapa.document_type', string="Document Type"),
        #  2.1.1.5
        #  2.1.1.5.1
        'ftpa_withholding_type': fields.selection(
            [('RT01', 'Natural Person'), ('RT02', 'Legal Person')],
            'Withholding type'
        ),
        #  2.1.1.5.2 withholding_amount in module
        #  2.1.1.5.3
        'ftpa_withholding_rate': fields.float('Withholding rate'),
        #  2.1.1.5.4
        'ftpa_withholding_payment_reason': fields.char(
            'Withholding reason', size=2),
        #  2.1.1.6
        'virtual_stamp': fields.boolean('Virtual Stamp'),
        'stamp_amount': fields.float('Stamp Amount'),
        #  2.1.1.7
        'welfare_fund_ids': fields.one2many(
            'welfare.fund.data.line', 'invoice_id',
            'Welfare Fund'
        ),
        #  2.1.1.8
        'discount_rise_price_ids': fields.one2many(
            'discount.rise.price', 'invoice_id',
            'Discount and Rise Price Details'
        ),
        #  2.1.2 - 2.1.6
        'related_documents': fields.one2many(
            'fatturapa.related_document_type', 'invoice_id',
            'Related Documents'
        ),
        #  2.1.7
        'activity_progress_ids': fields.one2many(
            'faturapa.activity.progress', 'invoice_id',
            'Fase of Activity Progress'
        ),
        #  2.1.8
        'ftpa_related_ddts': fields.one2many(
            'fatturapa.related_ddt', 'invoice_id',
            'Related DdT'
        ),
        #  2.1.9
        'carrier_id': fields.many2one(
            'res.partner', string="Carrier"),
        'transport_vehicle': fields.char('Vehicle', size=80),
        'transport_reason': fields.char('Reason', size=80),
        'number_items': fields.integer('number of items'),
        'description': fields.char('Description', size=100),
        'unit_weight': fields.char('Weight unit', size=10),
        'gross_weight': fields.float('Gross Weight'),
        'net_weight': fields.float('Net Weight'),
        'pickup_datetime': fields.datetime('Pick up'),
        'transport_date': fields.date('Transport Date'),
        'delivery_address': fields.text('Delivery Address'),
        'delivery_datetime': fields.datetime('Delivery Date Time'),
        
        
        'ftpa_incoterms': fields.char(string="Incoterms", copy=False),
        'incoterm': fields.many2one(
            'stock.incoterms',
            'Incoterm',
            help="International Commercial Terms are a series of predefined "
                 "commercial terms used in international transactions."
        ),

        #  2.1.10
        'related_invoice_code': fields.char('Related invoice code', size=64),
        'related_invoice_date': fields.date('Related invoice date'),
        #  2.2.1 invoice lines
        #  2.2.2
        'fatturapa_summary_ids': fields.one2many(
            'faturapa.summary.data', 'invoice_id',
            'FatturaPA Summary   Datas'
        ),
        #  2.3
        'Vehicle_registration': fields.date('Veicole Registration'),
        'total_travel': fields.char('Travel in hours or Km', size=15),
        #  2.4
        'fatturapa_payments': fields.one2many(
            'fatturapa.payment.data', 'invoice_id',
            'FatturaPA Payment Datas'
        ),
        #  2.5
        'fatturapa_doc_attachments': fields.one2many(
            'fatturapa.attachments', 'invoice_id',
            'FatturaPA attachments'
        ),
        
        'efatt_stabile_organizzazione_indirizzo': fields.char(
            string="Indirizzo Organizzazione",
            help="Blocco da valorizzare nei casi di cedente / prestatore non "
                 "residente, con stabile organizzazione in Italia. Indirizzo "
                 "della stabile organizzazione in Italia (nome della via, piazza "
                 "etc.)",
            readonly=True, copy=False),
        'efatt_stabile_organizzazione_civico': fields.char(
            string="Civico Organizzazione",
            help="Numero civico riferito all'indirizzo (non indicare se gia' "
                 "presente nell'elemento informativo indirizzo)",
            readonly=True, copy=False),
        'efatt_stabile_organizzazione_cap': fields.char(
            string="CAP Organizzazione",
            help="Codice Avviamento Postale",
            readonly=True, copy=False),
        'efatt_stabile_organizzazione_comune': fields.char(
            string="Comune Organizzazione",
            help="Comune relativo alla stabile organizzazione in Italia",
            readonly=True, copy=False),
        'efatt_stabile_organizzazione_provincia': fields.char(
            string="Provincia Organizzazione",
            help="Sigla della provincia di appartenenza del comune indicato "
                 "nell'elemento informativo 1.2.3.4 <Comune>. Da valorizzare se "
                 "l'elemento informativo 1.2.3.6 <Nazione> e' uguale a IT",
            readonly=True, copy=False),
        'efatt_stabile_organizzazione_nazione': fields.char(
            string="Nazione Organizzazione",
            help="Codice della nazione espresso secondo lo standard "
                 "ISO 3166-1 alpha-2 code",
            readonly=True, copy=False),
        # 2.1.1.10
        'efatt_rounding': fields.float(
            "Arrotondamento", readonly=True,
            help="Eventuale arrotondamento sul totale documento (ammette anche il "
                 "segno negativo)", copy=False
        ),
        'art73': fields.boolean(
            'Art73', readonly=True,
            help="Indica se il documento e' stato emesso secondo modalita' e "
                 "termini stabiliti con decreto ministeriale ai sensi "
                 "dell'articolo 73 del DPR 633/72 (cio' consente al "
                 "cedente/prestatore l'emissione nello stesso anno di piu' "
                 "documenti aventi stesso numero)", copy=False),
        'electronic_invoice_subjected': fields.related('partner_id', 'electronic_invoice_subjected',
                                                type='boolean', relation='res.partner',
                                                string='Subjected to electronic invoice', readonly=True),
    
    }

    _defaults = {
        'virtual_stamp': False
    }

    def copy(self, cr, uid, ids, defaults, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        defaults.update(efatt_stabile_organizzazione_indirizzo=False, related_documents=False, ftpa_incoterms=False, fatturapa_doc_attachments=False)
        return super(account_invoice, self).copy(cr, uid, ids, defaults, context)
    
    # def onchange_fiscal_position(self, cr, uid, ids, journal_id, fiscal_position, ttype, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     res = super(account_invoice, self).onchange_fiscal_position(cr, uid, ids, journal_id, fiscal_position, ttype, context)
    #
    #     if not fiscal_position:
    #         return res
    #
    #     fpos_obj = self.pool['account.fiscal.position']
    #     fiscal_position = fpos_obj.browse(cr, uid, fiscal_position, context)
    #     if ttype in ['out_invoice'] and fiscal_position.virtual_stamp:
    #         res['value'].update(virtual_stamp=fiscal_position.virtual_stamp, stamp_amount=fiscal_position.stamp_amount)
    #     return res

    def default_get(self, cr, uid, fields, context=None):
        defaults = super(account_invoice, self).default_get(cr, uid, fields, context=context)
        if defaults.get('journal_id'):
            journal = self.pool['account.journal'].browse(cr, uid, defaults['journal_id'])
            defaults['doc_type'] = journal.doc_type_id and journal.doc_type_id.id or False
        return defaults

    def onchange_journal_id(self, cr, uid, ids, journal_id, context=None):
        result = super(account_invoice, self).onchange_journal_id(cr, uid, ids, journal_id, context)
        if journal_id:
            journal = self.pool['account.journal'].browse(cr, uid, journal_id)
            result['value']['doc_type'] = journal.doc_type_id and journal.doc_type_id.id or False
        return result
