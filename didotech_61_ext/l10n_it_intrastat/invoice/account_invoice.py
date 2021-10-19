# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp.osv import orm
from openerp.tools.translate import _


class account_invoice(orm.Model):

    _inherit = 'account.invoice'

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        if vals.get('fiscal_position', False) and vals.get('invoice_line', False) \
            and self.pool['account.fiscal.position'].browse(cr, uid, vals['fiscal_position'], context=context).intrastat:

            product_obj = self.pool.get('product.product')
            invoice_line_ids = vals['invoice_line']

            for invoice_line in invoice_line_ids:
                if invoice_line[2] and 'product_id' in invoice_line[2]:
                    product_id = invoice_line[2]['product_id']

                    product_data = product_obj.browse(cr, uid, product_id, context=context)
                    if product_id and product_data:
                        t_type = product_data.type
                        if (t_type != 'service'
                            and not product_data.combined_nomenclature):
                            raise orm.except_orm(_('Error!'),
                                                 _('Combined Nomenclature not defined for the product!'))
                        if (t_type == 'service'
                            and not product_data.service_codes):
                            raise orm.except_orm(_('Error!'),
                                                 _('Combined Nomenclature Service Code not defined for the product!'))
                        if (t_type != 'service' and product_data.net_mass is None):
                            raise orm.except_orm(_('Error!'),
                                                 _('Net mass not defined for the product!'))
                        if (t_type != 'service' and product_data.statistical_value is None):
                            raise orm.except_orm(_('Error!'),
                                                 _('Statistical Value not defined for the product!'))
#                         if (t_type != 'service' and not product_data.uom_secondary):
#                             raise orm.except_orm(_('Error!'),
#                                                  _('Secondary Unit of Measure not defined for the product!'))

        res = super(account_invoice, self).create(cr, uid, vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids] 
        for invoice in self.browse(cr, uid, ids, context=context):
            if (invoice.fiscal_position
                 and invoice.fiscal_position.intrastat
                 and 'invoice_line' in vals):

                product_obj = self.pool.get('product.product')
                invoice_line_ids = vals['invoice_line']

                for invoice_line in invoice_line_ids:
                    if invoice_line[2] and 'product_id' in invoice_line[2]:
                        product_id = invoice_line[2]['product_id']
                        product_data = product_obj.browse(cr, uid, product_id, context=context)
                        if product_data:
                            if not product_data.combined_nomenclature:
                                raise orm.except_orm(_('Error!'),
                                                     _('Combined Nomenclature not defined for the product!'))
                            if product_data.type == 'service' and not product_data.service_codes:
                                raise orm.except_orm(_('Error!'),
                                                     _('Combined Nomenclature Service Code not defined for the product!'))
                            if (product_data.net_mass == None):
                                raise orm.except_orm(_('Error!'),
                                                     _('Net mass not defined for the product!'))
                            if (product_data.statistical_value == None):
                                raise orm.except_orm(_('Error!'),
                                                     _('Statistical Value not defined for the product!'))
#                             if not product_data.uom_secondary:
#                                 raise orm.except_orm(_('Error!'),
#                                                      _('Secondary Unit of Measure not defined for the product!'))

        res = super(account_invoice, self).write(cr, uid, ids, vals, context)
        return res
