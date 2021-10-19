# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#    Copyright (C) 2011 - TODAY Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = 'sale.order'
    _columns = {
        'repair_order_id': fields.many2one("repair.order", "Repair Order"),
    }
    
    def advance_invoice_create(self, cr, uid, order_id, context=None):
        """
             To create invoices.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs if we want more than one
             @param context: A standard dictionary

             @return:
        """
        
        if context is None:
            context = {}
        
        sale_obj = self.pool['sale.order']
        account_invoice_line_obj = self.pool['account.invoice.line']
        account_invoice_obj = self.pool['account.invoice']
        cur_obj = self.pool['res.currency']
        
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        if company.advance_product_id:
            advance_product = self.pool['product.product'].browse(cr, uid, company.advance_product_id.id, context)
        else:
            raise orm.except_orm(_('Warning'), _('Please set advance repair product'))
        
        amount = 0
        advance_qty = 1
        
        sale = sale_obj.browse(cr, uid, order_id, context=context)
        
        create_ids = []
        ids_inv = []
        notes = []
        
        if sale.order_policy == 'postpaid':
            raise orm.except_orm(
                _('Error'),
                _("You cannot make an advance on a sales order \
                     that is defined as 'Automatic Invoice after delivery'."))
        val = account_invoice_line_obj.product_id_change(cr, uid, [], advance_product.id,
                                                         uom=False, partner_id=sale.partner_id.id, fposition_id=sale.fiscal_position.id)
        res = val['value']
        if not res.get('account_id'):
            raise orm.except_orm(_('Configuration Error!'),
                                 _('There is no income account defined '
                                 'for this product: "%s" (id:%d)') %
                                 (advance_product.name, advance_product.id))
        
        for sale_order_line in sale.order_line:
            amount += sale_order_line.price_subtotal
            notes.append('{name: <30s}  {qty: >3}'.format(name=sale_order_line.product_id.name, qty=sale_order_line.product_uom_qty))
        
        cur = sale.pricelist_id.currency_id
        
        account_invoice_line_id = account_invoice_line_obj.create(cr, uid, {
            'name': res.get('name'),
            'account_id': res['account_id'],
            'price_unit': cur_obj.round(cr, uid, cur, amount),
            'quantity': advance_qty,
            'discount': False,
            'uos_id': res.get('uos_id'),
            'product_id': advance_product.id,
            'invoice_line_tax_id': [(6, 0, res.get('invoice_line_tax_id'))],
            'account_analytic_id': sale.project_id.id or False,
            'note': '\n'.join(notes),
        })
        create_ids.append(account_invoice_line_id)

        invoice_id = account_invoice_obj.create(cr, uid, {
            'name': sale.client_order_ref or sale.name,
            'origin': sale.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': sale.partner_id.property_account_receivable.id,
            'partner_id': sale.partner_id.id,
            'address_invoice_id': sale.partner_invoice_id.id,
            'address_contact_id': sale.partner_order_id.id,
            'invoice_line': [(6, 0, create_ids)],
            'currency_id': sale.pricelist_id.currency_id.id,
            'comment': '',
            'payment_term': sale.payment_term.id,
            'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id
        })
        context.update({'invoice_id': invoice_id})
        
        account_invoice_obj.button_reset_taxes(cr, uid, [invoice_id], context=context)

        for inv in sale.invoice_ids:
            ids_inv.append(inv.id)
        ids_inv.append(invoice_id)
        sale_obj.write(cr, uid, sale.id, {'invoice_ids': [(6, 0, ids_inv)]})
        
        #
        # If invoice on picking: add the cost on the SO
        # If not, the advance will be deduced when generating the final invoice
        #
        if sale.order_policy == 'picking':
            self.pool['sale.order.line'].create(cr, uid, {
                'order_id': sale.id,
                'name': res.get('name'),
                'price_unit': -cur_obj.round(cr, uid, cur, amount),
                'product_uom_qty': advance_qty,
                'product_uos_qty': advance_qty,
                'product_uos': res.get('uos_id'),
                'product_uom': res.get('uos_id'),
                'product_id': advance_product.id,
                'discount': False,
                'tax_id': [(6, 0, res.get('invoice_line_tax_id'))],
            }, context)

        return {
            'name': 'Open Invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.open.invoice',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sale order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        invoice_vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context)

        if context.get('repair_order_id', False) and context.get('set_partner_id', False):
            repair_order = self.pool['repair.order'].browse(cr, uid, context['repair_order_id'], context)
            if repair_order.under_warranty:
                set_partner = self.pool['repair.set.partner'].browse(cr, uid, context['set_partner_id'], context=context)
                pricelist = set_partner.partner_id.property_product_pricelist or False
                
                invoice_vals.update({
                    'account_id': set_partner.partner_id.property_account_receivable.id,
                    'partner_id': set_partner.partner_id.id,
                    'address_invoice_id': set_partner.address_invoice_id and set_partner.address_invoice_id.id or False,
                    'address_contact_id': set_partner.address_contact_id and set_partner.address_contact_id.id or False,
                    'fiscal_position': set_partner.partner_id.property_account_position and set_partner.partner_id.property_account_position.id or False,
                    'currency_id': pricelist and pricelist.currency_id and pricelist.currency_id.id,
                    'payment_term': set_partner.partner_id.property_payment_term and set_partner.partner_id.property_payment_term.id or False
                })
        
        return invoice_vals


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'is_free': fields.boolean("No Invoice"),
        'repair_order_id': fields.many2one("repair.order", "Repair Order"),
        'cost_price': fields.related('product_id', 'cost_price', type='float', string=_('Cost price'), store=False)
    }
    
    _defaults = {
        'is_free': lambda self, cr, uid, context: context.get('is_free', None),
    }

    def on_change_is_free(self, cr, uid, ids, is_free):
        res = {'value': {}}
        if is_free:
            res['value'].update({
                'discount': 100.00,
            })
        else:
            res['value'].update({
                'discount': 0.0,
            })
        return res

    def _create_so_from_ro(self, cr, uid, repair_order_id, temp=False, context=None):
        so_id = None
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        if not company.repair_shop_id:
                raise orm.except_orm(_('Warning'), _('Please set repair shop'))
        if repair_order_id:
            rorder = self.pool['repair.order'].browse(cr, uid, repair_order_id, context=context)
            if not temp and rorder.so_id:
                return rorder.so_id.id
            elif temp and rorder.temp_so_id:
                return rorder.temp_so_id.id

            sale_order_params = self.pool['sale.order'].onchange_partner_id(cr, uid, [], rorder.customer_id.id)['value']

            sale_order_params.update({
                'shop_id': company.repair_shop_id.id,
                'partner_id': rorder.customer_id.id,
                # 'pricelist_id': rorder.pricelist_id and rorder.pricelist_id.id or rorder.customer_id.property_product_pricelist.id,
                # 'partner_invoice_id': rorder.dest_address_id.id or rorder.partner_address_id.id,
                'partner_order_id': rorder.dest_address_id.id or rorder.partner_address_id.id,
                'partner_shipping_id': rorder.dest_address_id.id or rorder.partner_address_id.id,
                'date_order': rorder.order_date,
                # 'fiscal_position': rorder.customer_id.property_account_position and rorder.customer_id.property_account_position.id or False,
                'client_order_ref': rorder.customer_ref,
                'origin': rorder.name,
                'repair_order_id': repair_order_id,
                'order_policy': 'manual',
                'project_id': rorder.account_id.id or '',
                # 'payment_term': rorder.so_id and rorder.so_id.payment_term and rorder.so_id.payment_term.id or company.default_property_payment_term and company.default_property_payment_term.id or ''
            })

            if temp:
                if rorder.so_id:
                    sale_order_params['name'] = rorder.so_id.name + '_CONSUNTIVO_' 
                so_id = self.pool['temp.sale.order'].create(cr, uid, sale_order_params)
                project_so = self.pool['temp.sale.order'].browse(cr, uid, so_id, context=context).project_id
                vals = {
                    'temp_so_id': so_id,
                    'account_id': project_so and project_so.id or ''
                }
                self.pool['repair.order'].write(cr, uid, [repair_order_id], vals, context=context)
            else:
                so_id = self.pool['repair.sale.order'].create(cr, uid, sale_order_params)
                project_so = self.pool['repair.sale.order'].browse(cr, uid, so_id, context=context).project_id
                vals = {
                    'so_id': so_id,
                    'account_id': project_so and project_so.id or ''
                }
                self.pool['repair.order'].write(cr, uid, [repair_order_id], vals, context=context)
        return so_id

    def create(self, cr, uid, vals, context=None):
        if not vals.get("order_id") and vals.get('repair_order_id'):
            so_id = self._create_so_from_ro(cr, uid, vals.get('repair_order_id'), context=context)
            vals.update({'order_id': so_id})
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

    def account_invoice_line_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        create_ids = []
        sales = set()
        for line in self.browse(cr, uid, ids, context=context):
            vals = self._prepare_order_line_invoice_line(cr, uid, line, False, context)
            if vals:
                inv_id = self.pool['account.invoice.line'].create(cr, uid, vals, context)
                # cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                # self.write(cr, uid, [line.id], {'invoiced': True})
                sales.add(line.order_id.id)
                create_ids.append(inv_id)
        return create_ids


class RepairSaleOrder(orm.Model):
    _name = "repair.sale.order"
    _inherits = {'sale.order': 'sale_order_id'}
    _description = "Repair Sale Order"


class RepairSaleOrderLine(orm.Model):
    _name = "repair.sale.order.line"
    _inherits = {'sale.order.line': 'sale_order_line_id'}
    _description = "Repair Sale Order"

    def create(self, cr, uid, vals, context=None):
        if not vals.get("order_id") and vals.get('repair_order_id'):
            so_id = self.pool['sale.order.line']._create_so_from_ro(cr, uid, vals.get('repair_order_id'), temp=False, context=context)
            repar_sale_order = self.pool['repair.sale.order'].browse(cr, uid, so_id, context)
            vals.update({'order_id': repar_sale_order.sale_order_id.id})
        return super(RepairSaleOrderLine, self).create(cr, uid, vals, context=context)

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        fiscal_position = self.pool['res.partner'].browse(cr, uid, partner_id, context).property_account_position.id
        return self.pool['sale.order.line'].product_id_change(cr, uid, ids, pricelist, product_id, qty=qty,
                                                              uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                                              lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)

    def on_change_is_free(self, cr, uid, ids, is_free):
        res = {'value': {}}
        if is_free:
            res['value'].update({
                'discount': 100.00,
            })
        else:
            res['value'].update({
                'discount': 0.0,
            })
        return res

    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
                           uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                           lang=False, update_tax=True, date_order=False, context=None):

        return self.pool['sale.order.line'].product_uom_change(cursor, user, ids, pricelist, product, qty,
                                                               uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, context)


class TempSaleOrder(orm.Model):
    _name = "temp.sale.order"
    _inherits = {'sale.order': 'sale_order_id'}
    _description = "Temporary Sale Order"


class TempSaleOrderLine(orm.Model):
    _name = "temp.sale.order.line"
    _inherits = {'sale.order.line': 'sale_order_line_id'}
    _description = "Temporary Sale Order"
    
    def _get_cost_price(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for temp_order_line in self.browse(cr, uid, ids, context):
            if temp_order_line.service_cost_price:
                result[temp_order_line.id] = temp_order_line.service_cost_price
            else:
                result[temp_order_line.id] = temp_order_line.product_id.cost_price
            
        return result
    
    _columns = {
        'service_cost_price': fields.float(_('Service cost')),
        'cost_price': fields.function(_get_cost_price, type='float', string=_('Cost price'), method=True, store=False)
    }

    def on_change_is_free(self, cr, uid, ids, is_free):
        res = {'value': {}}
        if is_free:
            res['value'].update({
                'discount': 100.00,
                'price_unit': 0.0,
            })
        else:
            res['value'].update({
                'discount': 0.0,
            })
        return res

    def create(self, cr, uid, vals, context=None):
        if not vals.get("order_id") and vals.get('repair_order_id'):
            so_id = self.pool['sale.order.line']._create_so_from_ro(cr, uid, vals.get('repair_order_id'), temp=True, context=context)
            temp_sale_order = self.pool['temp.sale.order'].browse(cr, uid, so_id, context)
            vals.update({'order_id': temp_sale_order.sale_order_id.id})
        return super(TempSaleOrderLine, self).create(cr, uid, vals, context=context)

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
                          uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                          lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        # Carlo: patch for a strange reason fiscal_position is not pass correctly from view, not remove below line
        fiscal_position = self.pool['res.partner'].browse(cr, uid, partner_id, context).property_account_position.id
        return self.pool['sale.order.line'].product_id_change(cr, uid, ids, pricelist, product_id, qty=qty,
                                                              uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
                                                              lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)

    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
                           uom=False, qty_uos=0, uos=False, name='', partner_id=False,
                           lang=False, update_tax=True, date_order=False, context=None):

        return self.pool['sale.order.line'].product_uom_change(cursor, user, ids, pricelist, product, qty,
                                                               uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, context)
