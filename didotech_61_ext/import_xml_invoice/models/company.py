# -*- coding: utf-8 -*-
# © 2019 Didotech srl (www.didotech.com)

from openerp.osv import orm, fields


class Company(orm.Model):
    _inherit = 'res.company'

    _columns = {
        'invoice_import_auto_confirm': fields.boolean('Confirm automatically imported invoice'),
        'invoice_import_autocreate_product': fields.boolean('Auto Create Product from XML'),
        'invoice_import_path': fields.char('Path to Invoice XMLs', size=256),
        'invoice_import_price': fields.selection([('normal', 'Normal'), ('sub_total', 'Sub Total')], 'Type of Unit Price'),
        'invoice_set_number': fields.boolean('Set Number From Origin')
    }

    _defaults = {
        'invoice_import_price': 'normal'
    }
