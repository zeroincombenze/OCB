# -*- coding: utf-8 -*-
# © 2019 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import fields
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.osv.osv import except_osv


class WizardLinkToInvoice(orm.TransientModel):
    _name = "wizard.link.to.invoice"
    _description = "Link to Supplier Invoice"
    
    _columns = {
        'invoice_id': fields.many2one(
            'account.invoice', string="Invoice", required=True),
        'supplier_id': fields.many2one('res.partner', string="Partner", required=True),
        'type': fields.selection([
            ('in_invoice', 'Supplier Invoice'),
            ('in_refund', 'Supplier Refund'),
        ], 'Type', readonly=True, select=True, change_default=True),
        'source_invoice_total': fields.float(string="Source Invoice Total Amount"),
        'dest_invoice_total': fields.float(string="Destination Invoice Total Amount"),
        'difference_total': fields.float(string="Difference"),
        'show_idiot_proof_button': fields.boolean("Show Idiot Proof")
    }

    def onchange_invoice_id(self, cr, uid, ids, invoice_id, source_invoice_total, context):
        res = {
            'value': {}
        }
        if invoice_id:
            invoice = self.pool['account.invoice'].browse(cr, uid, invoice_id, context)
            difference = invoice.amount_total - source_invoice_total
            res['value'] = {
                'dest_invoice_total': invoice.amount_total,
                'difference_total': difference,
                'show_idiot_proof_button': abs(difference) > 100
            }

        return res

    def default_get(self, cr, uid, default, context):
        if 'xml_supplier_id' in context:
            context['default_supplier_id'] = context['xml_supplier_id']
        if context.get('active_ids', False):
            active_ids = context.get('active_ids')
            if len(active_ids) != 1:
                raise except_osv(
                    _('Error'),
                    _("You can select only 1 XML file to link")
                )
            att = self.pool['fatturapa.attachment.in'].browse(cr, uid, active_ids[0], context)
            if att.xml_supplier_id:
                context['default_supplier_id'] = att.xml_supplier_id.id
            if att.invoices_total:
                context['default_source_invoice_total'] = att.invoices_total
            if att.xml_invoice_type:
                if att.xml_invoice_type == 'TD04':
                    context['default_type'] = 'in_refund'
                else:
                    context['default_type'] = 'in_invoice'

        return super(WizardLinkToInvoice, self).default_get(cr, uid, default, context)

    def link(self, cr, uid, ids, context=None):
        context = context or {}
        active_ids = context.get('active_ids')
        if len(active_ids) != 1:
            raise except_osv(
                _('Error'),
                _("You can select only 1 XML file to link")
            )

        wizard = self.browse(cr, uid, ids[0], context)
        # invoice_model = self.pool['account.invoice']
        # invoice_model.write(
        #     cr, uid, [wizard.invoice_id.id], {
        #         'fatturapa_attachment_in_id': active_ids[0]
        #     }, context
        # )

        context['invoice_id'] = wizard.invoice_id.id
        return self.pool['wizard.import.fatturapa'].importFatturaPA(cr, uid, [], context)
