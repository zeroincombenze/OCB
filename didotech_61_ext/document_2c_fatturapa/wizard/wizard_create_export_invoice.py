# -*- coding: utf-8 -*-
# © 2018-2019 Andrei Levin - Didotech srl (www.didotech.com)

import logging

from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class wizard_create_export_invoice(orm.TransientModel):
    _name = "wizard.create.export.invoice"

    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_obj = self.pool['account.journal']
        vals = []
        value = journal_obj.search(cr, uid, ['|', ('type', '=', 'sale'), ('type', '=', 'sale_refund')], context=context)
        for jr_type in journal_obj.browse(cr, uid, value, context=context):
            t1 = jr_type.id, jr_type.name
            if t1 not in vals:
                vals.append(t1)
        return vals

    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal', required=True),
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
        'auto_approve': fields.boolean('Group by Partner'),
    }

    def create_export_invoice_invoice_2c(self, cr, uid, ids, context):
        invoice_obj = self.pool['account.invoice']
        export_pa_obj = self.pool['wizard.export.fatturapa']
        wizard = self.browse(cr, uid, ids, context)[0]

        invoice_ids = invoice_obj.search(cr, uid, [
            ('journal_id', '=', int(wizard.journal_id)),
            ('fatturapa_attachment_out_id', '=', False),
            ('state', 'in',  ('open', 'paid')),
            ('date_invoice', '>=', wizard.date_from),
            ('date_invoice', '<=', wizard.date_to)
        ], context=context)
        if invoice_ids:
            if wizard.auto_approve:
                context['active_ids'] = invoice_ids
                try:
                    export_pa_obj.exportFatturaPA(cr, uid, [], context=context)
                except Exception as e:
                    _logger.error(e)
            else:
                total_length = len(invoice_ids)
                for count, invoice_id in enumerate(invoice_ids, start=1):
                    _logger.info('{} / {}'.format(count, total_length))
                    if count / 100 * 100 == count:
                        _logger.info('Committing...')
                        cr.commit()
                    context['active_ids'] = [invoice_id]
                    try:
                        export_pa_obj.exportFatturaPA(cr, uid, [], context=context)
                    except Exception as e:
                        _logger.error(e)

        return {
            'type': 'ir.actions.act_window_close',
        }
