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
import datetime
import time

import decimal_precision as dp
import netsvc
from dateutil.relativedelta import relativedelta
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class res_partner(orm.Model):
    _inherit = "res.partner"

    def _check_manufacturer(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for partner in self.read(cr, uid, ids, ['manufacturer'], context):
            product_ids = self.pool['product.product'].search(cr, uid, [('manufacturer', '=', partner['id'])])
            if len(product_ids) > 0:
                res[partner['id']] = True
            else:
                res[partner['id']] = False

        return res

    _columns = {
        'manufacturer': fields.boolean("Manufacturer"),
        'is_manufacturer': fields.function(_check_manufacturer, type="boolean", method=True),
        'repair_machine_ids': fields.one2many('repair.machine', 'customer_id', 'Repair Machine'),
    }

    _defaults = {
        'manufacturer': lambda *a: False,
    }


class repair_machine(orm.Model):
    _name = 'repair.machine'
    _description = 'Repair Machine'

    def name_get(self, cr, uid, ids, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        if not len(ids):
            return []
        res = []
        context = context or self.pool['res.users'].context_get(cr, uid)
        for machine in self.browse(cr, uid, ids, context=context):

            if not machine.name:
                name = machine.description
            else:
                name = u'[{name}] {description}'.format(name=machine.name, description=machine.description)
            if machine.telaio:
                name += " : " + machine.telaio
            elif machine.plate:
                name += " : " + machine.plate

            res.append((machine.id, name))
        return res
    
    def on_change_asset_asset_id(self, cr, uid, ids, asset_asset_id):
        res = {'value': {}}
        if asset_asset_id:
            vals = {}
            asset = self.pool['asset.asset'].browse(cr, uid, asset_asset_id)
            vals.update({
                'name': asset.asset_product_id.name, 
                'manufacturer': asset.partner_id and asset.partner_id.id or False,
                'telaio': asset.serial_number and asset.serial_number.name or False,
                'description': asset.complete_name,
                'customer_id': asset.company_id and asset.company_id.partner_id.id or False,
                'account_id': asset.account_id and asset.account_id.id or False,
                'product_id': asset.asset_product_id and asset.asset_product_id.product_product_id and asset.asset_product_id.product_product_id.id or False,
            })
            res.update({'value': vals})
        return res

    def on_change_product_id(self, cr, uid, ids, product_id, asset_asset_id):
        res = {'value': {}}
        if product_id and not asset_asset_id:
            vals = {}
            product = self.pool['product.product'].browse(cr, uid, product_id)
            vals.update({
                'manufacturer': product.manufacturer and product.manufacturer.id  or False,
            })
            res.update({'value': vals})
        return res
    
    def _get_repair_order(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        repair_machine_obj = self.pool['repair.machine']
        context = context or self.pool['res.users'].context_get(cr, uid)
        for machine in repair_machine_obj.browse(cr, uid, ids, context):
            result[machine.id] = self.pool['repair.order'].search(cr, uid, [('machine_id', '=', machine.id)], order="order_date desc", context=context)
        return result
    
    def _get_repair_product(self, cr, uid, ids, field_name, model_name, context=None):
        result = {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        for machine_id in ids:
            for repair in self.pool['repair.order'].search(cr, uid, [('machine_id', '=', machine_id)], context=context):
                if result.get(machine_id, False):
                    result[machine_id] += self.pool['temp.sale.order.line'].search(cr, uid, [('repair_order_id', '=', repair)], context=context)
                else:
                    result[machine_id] = self.pool['temp.sale.order.line'].search(cr, uid, [('repair_order_id', '=', repair)], context=context)
        return result

    def _default_product(self, cr, uid, context=None):
        if context.get('produtc_id', False):
            return context['product_id']
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        if user.company_id and user.company_id.property_repair_product_id:
            return user.company_id.property_repair_product_id.id
        return None
    
    _columns = {
        'name': fields.char('Machine', size=64, required=True),
        # 'machine': fields.char('Machine', size=64, required=False),
        'plate': fields.char('Targa', size=64),
        'manufacturer': fields.many2one("res.partner", "Manufacturer", domain="[('manufacturer', '=', True)]", required=False),
        'model': fields.char('Model', size=64),
        'telaio': fields.char('Telaio', size=64),
        'date_start': fields.date('Insert Date'),
        'description': fields.char('Description', size=64, required=True),
        'customer_id': fields.many2one('res.partner', "Customer", domain="[('customer', '=', True)]", required=True),
        'asset_asset_id': fields.many2one('asset.asset', 'Asset'),
        'account_id': fields.many2one('account.analytic.account', 'Analytic Account', domain="[('type', '!=','view'), ('partner_id','=', customer_id), ('parent_id', '!=', False)]" ),
        'repair_order_ids': fields.function(_get_repair_order, 'Repair Order', type='one2many', relation='repair.order', readonly=True, method=True),
        'repair_product_ids': fields.function(_get_repair_product, 'Repaired Product', type='one2many', relation='temp.sale.order.line', readonly=True, method=True),
        'product_id': fields.many2one("product.product", "Product", required=True, domain="[('type', 'not in', ['service'] )]"),
        
    }
    
    _sql_constraints = [('asset_asset_uniq', 'unique(asset_asset_id)', 'Asset must be unique!')]

    _order = "customer_id, name, plate"

    _defaults = {
        'date_start': lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'customer_id': lambda self, cr, uid, context: context.get('customer_id', False),
        'product_id': _default_product,
    }


class repair_order(orm.Model):
    _name = 'repair.order'
    _description = 'Repair Order'

    _inherit = ['mail.thread']
    
    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        if not len(ids):
            return []
        res = []

        for order in self.browse(cr, uid, ids, context=context):
            name = order.name + ": " + (order.customer_id and order.customer_id.name)
            res.append((order.id, name))
        return res

    def _get_contact_number(self, cr, uid, ids, field_name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        for order in self.read(cr, uid, ids, ['customer_id', 'phone', 'cell_phone'], context=context):
            number = order['cell_phone'] and order['cell_phone'] or order['phone']
            if not number and order['customer_id']:
                partner = self.pool['res.partner'].read(cr, uid, order['customer_id'][0], ['phone'], context=context)
                if partner and partner.get('phone', False):
                    number = partner['phone']
            res[order['id']] = number or ''
        return res

    def _check_picking_done(self, cr, uid, ids, field_name, arg, context=None):
        picking_repair_field_map = {
            'in_picking_id': 'inward_ok',
            'out_picking_id': 'is_delivered',
            'in_picking_producer_id': 'inward_producer_ok',
            'out_picking2producer_id': 'outward_producer_ok'
        }

        res = {}.fromkeys(ids, dict([(field, False) for field in picking_repair_field_map.values()]))
        if not ids:
            return res

        repair_fields = picking_repair_field_map.keys()
        repair_fields.append('state')
        for order in self.read(cr, uid, ids, repair_fields, context=context):
            for field in picking_repair_field_map.keys():
                if order.get(field, False):
                    picking = self.pool['stock.picking'].read(cr, uid, order[field][0], ['state'], context=context)
                    if picking and picking['state'] == 'done':
                        res[order['id']][picking_repair_field_map[field]] = True
        return res

    def _check_picking_state(self, cr, uid, ids, context=None):
        order_ids = []
        stock = self.pool['stock.picking']
        for repair in stock.browse(cr, uid, ids, context=context):
            if repair.state and repair.state == 'done':
                stock_order_ids = self.pool['repair.order'].search(cr, uid, ['|', ('in_picking_id', '=', repair.id), '|', ('out_picking_id', '=', repair.id), '|', ('out_picking2producer_id', '=', repair.id), ('in_picking_producer_id', '=', repair.id)], context=context)
                order_ids += stock_order_ids
        return order_ids

    def _get_order(self, cr, uid, ids, context=None):
        res = []
        for order in self.pool['sale.order'].read(cr, uid, ids, ['repair_order_id'], context=context):
            if order.get('repair_order_id', False):
                res.append(order['repair_order_id'][0])
        return res

    def _get_order_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool['sale.order.line'].browse(cr, uid, ids, context=context):
            repair_order_id = None
            if line.repair_order_id or line.order_id.repair_order_id:
                if line.repair_order_id:
                    repair_order_id = line.repair_order_id.id
                elif line.order_id.repair_order_id:
                    repair_order_id = line.order_id.repair_order_id.id
                    self.pool['sale.order.line'].write(cr, uid, [line.id], {'repair_order_id': repair_order_id}, context)
            if repair_order_id:
                result[repair_order_id] = True
        return result.keys()
    
    # def fix_temp_orders(self, cr, uid, context):
    #    repair_order_ids = self.search(cr, uid, [('temp_so_id', '=', False)])
    #    print repair_order_ids
    #    for repair_order in self.browse(cr, uid, repair_order_ids, context):
    #        if repair_order.temp_so_lines:
    #            print repair_order.id, repair_order.name
    
    def _all_products(self, cr, uid, ids, field_name, arg, context=None):
        # Dummy function, returns False for every order

        # self.fix_temp_orders(cr, uid, context)
        
        return dict([(order_id, False) for order_id in ids])

    def _get_invoice_ids(self, cr, uid, ids, name, args, context=None):
        result = {}
        for repair in self.browse(cr, uid, ids, context=context):
            invoice_ids = []
            # sale_order = repair.temp_so_id or repair.so_id or False
            if repair.so_id:
                for invoice in repair.so_id.invoice_ids:
                    invoice_ids.append(invoice.id)
            if repair.temp_so_id:
                for invoice in repair.temp_so_id.invoice_ids:
                    invoice_ids.append(invoice.id)
            result[repair.id] = invoice_ids
        return result

    def _get_picking_ids(self, cr, uid, ids, name, args, context=None):
        result = {}
        for repair in self.browse(cr, uid, ids, context=context):
            picking_ids = []
            if repair.so_id:
                for picking in repair.so_id.picking_ids:
                    picking_ids.append(picking.id)
            if repair.temp_so_id:
                for picking in repair.temp_so_id.picking_ids:
                    picking_ids.append(picking.id)
            result[repair.id] = picking_ids
        return result

    _columns = {
        'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model', '=', _name)]),
        'name': fields.char('Title', size=24),
        'partner_id': fields.related('customer_id', type="many2one", relation='res.partner', string="Customer"),
        'customer_id': fields.many2one('res.partner', "Customer", domain="[('customer', '=', True)]", required=True),
        'partner_address_id': fields.many2one("res.partner.address", "Customer Address", domain="[('partner_id', '=', customer_id)]"),
        'dest_address_id': fields.many2one("res.partner.address", "Customer Address", domain="[('partner_id', '=', customer_id)]"),
        'machine_id': fields.many2one('repair.machine', "Repair Machine"), 
        'product_id': fields.many2one("product.product", "Product", required=True, domain="[('type', 'not in', ['service'] )]"),
        'phone': fields.char('Home Phone', size=16),
        'cell_phone': fields.char('Mobile Phone', size=16),
        'contact_number': fields.function(_get_contact_number, type="char", method=True, size=64, store=True, string="Contact Number"),
        'email': fields.char('Personal Email', size=64),
        'manufacturer': fields.many2one("res.partner", "Manufacturer", domain="[('is_manufacturer', '=', True)]", required=False),
        'manufacturer_pname': fields.char("Product Name", size=128, required=False),
        'manufacturer_pref': fields.char("Product Number", size=128, required=False),
        # 'product_category': fields.many2one("product.category", "Category"),
        'repair_condition': fields.many2one("product.condition", "Condition"),
        'serial': fields.many2one('stock.production.lot', "Serial Number", ondelete="no action", required=False, domain="[('product_id', '=', product_id)]"),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('confirmed', 'Confirmed'),
            ('analyzing', 'Under Examination'),
            ('processed', 'Processed'),
            ('wait_confirmation', 'Waiting for confirmation from Customer'),
            ('ready', 'Ready to Repair'),
            ('under_repair', 'Under Repair'),
            ('wait_delivery', 'Waiting to deliver to Customer'),
            ('wait_outgo', 'Waiting for Outgo'),
            ('2binvoiced', 'To be Invoiced'),
            ('sending2manu', 'Waiting to deliver to Supplier'),
            ('wait_reception', 'Waiting to receive from Supplier'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ], 'State', readonly=True),
        'order_move_id': fields.many2one('stock.move', 'Move', domain="[('location_dest_id.usage', '=', 'customer'), ('partner_id', '=', customer_id)]", readonly=True, states={'draft': [('readonly', False)]}),
        # 'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', states={'confirmed': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)]}),
        'location_id': fields.many2one('stock.location', 'Current Location', select=True, readonly=True, states={'draft': [('readonly', False)]}),
        'deliver_bool': fields.boolean('Deliver', help="Check this box if you want to manage the delivery once the product is repaired. If cheked, it will create a picking with selected product. Note that you can select the locations in the Info tab, if you have the extended view."),
        'purchased_date': fields.date("Purchased Date"),
        'warranty_date': fields.date("Warranty Date"),
        'order_date': fields.date("Create Date"),
        'order_date_sale_id': fields.related('so_id', 'sale_order_id', 'date_order', type="date", string="Create Date"),
        'order_date_temp_sale_id': fields.related('temp_so_id', 'sale_order_id', 'date_order', type="date", string="Create Date"),
        'invoiced': fields.boolean('Invoiced', readonly=True),
        'repaired': fields.boolean('Repaired', readonly=True),
        'under_warranty': fields.boolean('Under Warranty'),
        'repairable': fields.boolean('Repairable', readonly=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', help='The pricelist comes from the selected partner, by default.'),
        'partner_invoice_id': fields.many2one('res.partner.address', 'Invoicing Address', domain="[('partner_id', '=', customer_id)]"),
        'invoice_method': fields.selection([
            ("none", "No Invoice"),
            ("b4repair", "Before Repair"),
            ("after_repair", "After Repair")
        ], "Invoice Method",
            select=True, required=True, states={
                'draft': [('readonly', False)],
                'confirmed': [('readonly', False)],
                'analyzing': [('readonly', False)],
                'processed': [('readonly', False)],
                'wait_confirmation': [('readonly', False)],
            }, readonly=True, help='This field allow you to change the workflow of the repair order. If value selected is different from \'No Invoice\', it also allow you to select the pricelist and invoicing address.'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'picking_id': fields.many2one('stock.picking', 'Picking', readonly=True),
        'internal_notes': fields.text('Internal Notes'),
        'quotation_notes': fields.text('Quotation Notes'),
        'paid_by': fields.selection([('customer', 'Customer'), ('manufacturer', "Manufacturer")], "Paid By", select=True),
        'sale_id': fields.related('so_id', 'sale_order_id', type="many2one", relation='sale.order', string="Order", store=True),
        'temp_sale_id': fields.related('temp_so_id', 'sale_order_id', type="many2one", relation='sale.order', string="Temporary Order", store=True),
        'so_id': fields.many2one("repair.sale.order", "Sale Order"),
        'so_lines': fields.one2many('repair.sale.order.line', 'repair_order_id', 'Order Lines', readonly=True, 
                                    states={'analyzing': [('readonly', False)],
                                            '2binvoiced': [('readonly', False)],
                                            'confirmed': [('readonly', False)],
                                            'draft': [('readonly', False)],
                                            'wait_confirmation': [('readonly', False)],
                                            }),
        'temp_so_id': fields.many2one("temp.sale.order", "Temp Sale Order"),
        'temp_so_lines': fields.one2many('temp.sale.order.line', 'repair_order_id', 'Real Order Lines', readonly=True,
                                         states={'under_repair': [('readonly', False)],
                                                 'wait_outgo': [('readonly', False)],
                                                 '2binvoiced': [('readonly', False)]}),
        # 'invoice_ids': fields.related('temp_so_id', "invoice_ids", type="many2many", relation="account.invoice", readonly=True, states={'draft': [('invisible', True)]}),
        # 'picking_ids': fields.related('temp_so_id', "picking_ids", type="one2many", relation="stock.picking", readonly=True, states={'draft': [('invisible', True)]}),
        'invoice_ids': fields.function(_get_invoice_ids, string="Invoice", type="many2many", relation="account.invoice", readonly=True, states={'draft': [('invisible', True)]}),
        'picking_ids': fields.function(_get_picking_ids, string="Picking", type="one2many", relation="stock.picking", readonly=True, states={'draft': [('invisible', True)]}),

        'po_id': fields.many2one("purchase.order", "Purchase Order", states={'draft': [('invisible', True)]}),
        'po_lines': fields.related('po_id', "order_line", type="one2many", relation="purchase.order.line", states={'draft': [('invisible', True)]}),
        'company_id': fields.many2one("res.company", "Company"),
        'in_picking_id': fields.many2one("stock.picking", "Reception"),
        'out_picking_id': fields.many2one("stock.picking", "Delivery"),
        'out_picking2producer_id': fields.many2one("stock.picking", "Delivery to Producer"),
        'in_picking_producer_id': fields.many2one("stock.picking", "Reception From Producer"),
        'inward_ok': fields.function(_check_picking_done, method=True, multi='picking_done', type="boolean", string="Inward ok?",
                                     store={'stock.picking': (_check_picking_state, ['state'], 10)}),
        'outward_producer_ok': fields.function(_check_picking_done, method=True, multi='picking_done', type="boolean", string="Sent to Producer?",
                                               store={'stock.picking': (_check_picking_state, ['state'], 10)}),
        'inward_producer_ok': fields.function(_check_picking_done, method=True, multi='picking_done', type="boolean", string="Recived from Producer?",
                                              store={'stock.picking': (_check_picking_state, ['state'], 10)}),
        'is_analized': fields.boolean("Study Ok", readonly=True),
        'is_delivered': fields.function(_check_picking_done, method=True, multi='picking_done', type="boolean", string="Delivered to Customer",
                                        store={'stock.picking': (_check_picking_state, ['state'], 10)}),

        'description': fields.text('Problem', required=True),
        'customer_ref': fields.char('Customer Ref', size=24),
        'accessory_ids': fields.one2many("repair.order.accessory", "order_id", "Accessories"),
        'hr_analytic_timesheet_ids': fields.one2many("hr.analytic.timesheet", "repair_order_id", "Related Timeline Id", ondelete='set null'),
        'account_id': fields.many2one('account.analytic.account', 'Analytic Account', domain="[('type', '!=','view'), ('partner_id','=', customer_id), ('parent_id', '!=', False)]"),
        # 'account_id': fields.related('so_id', 'project_id', type='many2one', relation='account.analytic.account', string=_('Sale Analytic Account'), store=False),
        'all_products': fields.function(_all_products, method=True, string="All products", type="boolean"),
        'on_site': fields.boolean(_('On-site')),
        'on_site_ids': fields.one2many('repair.order.on.site', 'repair_order_id', _('On-site repairs')),
        'on_site_description': fields.text(_('Work description')),
        'user_id': fields.many2one('res.users', 'User'),
    }

    def action_view_invoice(self, cr, uid, ids, context=None):
        inv_ids = []
        for repair in self.browse(cr, uid, ids, context):
            for invoice in repair.invoice_ids:
                inv_ids.append(invoice.id)
            if not repair.invoice_ids:
                for invoice_id in self.pool['account.invoice'].search(cr, uid, [('origin', 'ilike', repair.name)], context=context):
                    inv_ids.append(invoice_id)

        if not inv_ids:
            wf_service = netsvc.LocalService("workflow")
            for repair in self.browse(cr, uid, ids, context):
                if repair.temp_sale_id:
                    repair.temp_sale_id.action_cancel_draft()

                    wf_service.trg_delete(uid, 'sale.order', repair.temp_sale_id.id, cr)
                    wf_service.trg_create(uid, 'sale.order', repair.temp_sale_id.id, cr)
                    wf_service.trg_validate(uid, 'sale.order', repair.temp_sale_id.id, 'order_confirm', cr)
                    repair.temp_sale_id.manual_invoice()
                    for invoice in repair.temp_sale_id.invoice_ids:
                        inv_ids.append(invoice.id)

        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        result = act_obj.read(cr, uid, [result and result[1] or False], context=context)[0]

        # choose the view_mode accordingly
        if len(inv_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, inv_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False

        return result

    def action_view_delivery(self, cr, uid, ids, context=None):
        pick_ids = []
        for repair in self.browse(cr, uid, ids, context):
            for line in repair.picking_ids:
                pick_ids.append(line.id)

        mod_obj = self.pool['ir.model.data']
        act_obj = self.pool['ir.actions.act_window']

        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree')
        result = act_obj.read(cr, uid, [result and result[1] or False], context=context)[0]

        # compute the number of delivery orders to display

        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        result['context'] = {'default_type': 'out', 'contact_display': 'partner_address', 'search_default_confirmed': 0, 'search_default_available': 0}
        return result

    _defaults = {
        # 'name': lambda self, cr, uid, context: self.pool['ir.sequence'].get(cr, uid, 'repair.order'),
        'state': 'draft',
        'is_analized': False,
        'is_delivered': False,
        'repairable': True,
        'repaired': False,
        'invoiced': False,
        'invoice_method': 'after_repair',
        'paid_by': 'customer',
        'pricelist_id': lambda self, cr, uid, context: self.pool['product.pricelist'].search(cr, uid, [('type', '=', 'sale')])[0],
        'order_date': fields.date.context_today,
        'company_id': lambda self, cr, uid, context: self.pool['res.users']._get_company(cr, uid, context),
        'all_products': False
    }
    
    _order = "order_date desc, customer_id"

    def create(self, cr, uid, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if not values.get('name', False):
            values['name'] = self.pool['ir.sequence'].get(cr, uid, 'repair.order')
        # TODO: update value for machine_id
        if values.get('product_id', False) and not values.get('machine_id', False):
            product = self.pool['product.product'].browse(cr, uid, values['product_id'], context)
            if values.get('manufacturer', False) and not product.manufacturer:
                product.write({'manufacturer': values['manufacturer']})
        
        return super(repair_order, self).create(cr, uid, values, context)

    def write(self, cr, uid, ids, values, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if values.get('so_lines', False):
            for line in values['so_lines']:
                if line[0] == 2:
                    # Deleted line
                    so_line = self.pool['repair.sale.order.line'].browse(cr, uid, line[1], context)
                    so_line.sale_order_line_id.unlink()  # work also without parameter
                    
        if values.get('temp_so_lines', False):
            for line in values['temp_so_lines']:
                if line[0] == 2:
                    # Deleted line
                    so_line = self.pool['temp.sale.order.line'].browse(cr, uid, line[1], context)
                    so_line.sale_order_line_id.unlink()  # work also without parameter

        for (id, name) in self.name_get(cr, uid, ids, context):
            if values.get('state', False):
                text = u"{name}".format(name=name) + _(' has been change to ') + dict(self.fields_get(cr, uid, allfields=['state'], context=context)['state']['selection'])[values.get('state', False)]
                self.log(cr, uid, id, text)
                self.message_append(cr, uid, [id], text, body_text=text, context=context)
            if values.get('date_order', False) or values.get('customer_id', False) or values.get('customer_ref', False):
                order = self.browse(cr, uid, id, context)
                if values.get('date_order', False) and (order.date_order != values.get('date_order', False)):
                    text = _(u'{order} has been change date from {date_from} to {date_to}').format(order=order.name, date_from=order.date_order, date_to=values.get('date_order', False))
                    self.log(cr, uid, id, text)
                    self.message_append(cr, uid, [id], text, body_text=text, context=context)
                if values.get('customer_id', False) and (order.customer_id.id != values.get('customer_id', False)):
                    text = _(u'{order} has been change customer from {customer_from}').format(order=order.name, customer_from=order.customer_id.name)
                    self.log(cr, uid, id, text)
                    self.message_append(cr, uid, [id], text, body_text=text, context=context)

        
        result = super(repair_order, self).write(cr, uid, ids, values, context)

        # change value on connect document (sale order)
        if values.get('customer_id', False) or values.get('customer_ref', False):
            for repair in self.browse(cr, uid, ids, context=context):
                order_value = {}
                if values.get('customer_ref', False):
                    order_value.update({'client_order_ref': values.get('customer_ref', False)})
                if values.get('customer_id', False):
                    addr = self.pool.get('res.partner').address_get(cr, uid, [values.get('customer_id', False)], ['delivery', 'invoice', 'contact'])
                    part = self.pool.get('res.partner').browse(cr, uid, values.get('customer_id', False), context)
                    pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
                    payment_term = part.property_payment_term and part.property_payment_term.id or False
                    fiscal_position = part.property_account_position and part.property_account_position.id or False
                    dedicated_salesman = part.user_id and part.user_id.id or uid
                    order_value.update({
                        'partner_id': values.get('customer_id', False),
                        'partner_invoice_id': addr['invoice'],
                        'partner_order_id': addr['contact'],
                        'partner_shipping_id': addr['delivery'],
                        'payment_term': payment_term,
                        'fiscal_position': fiscal_position,
                        'user_id': dedicated_salesman,
                    })
                if order_value:
                    if repair.sale_id:
                        repair.sale_id.write(order_value)
                    if repair.temp_sale_id:
                        repair.temp_sale_id.write(order_value)
                    if repair.so_id:
                        repair.so_id.write(order_value)
                    if repair.temp_so_id:
                        repair.temp_so_id.write(order_value)

        if values.get('so_id') or values.get('temp_so_id'):
            return result

        service = {}
        service_cost = {}


        company = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id
        don_t_group_service_line = not company.group_service_line
        if company.update_service:
            for repair in self.browse(cr, uid, ids, context=context):
                for hr_analytic_timesheet in repair.hr_analytic_timesheet_ids:
                    # prodotto usato
                    if service.get(hr_analytic_timesheet.product_id.id, False):
                        service[hr_analytic_timesheet.product_id.id] += hr_analytic_timesheet.unit_amount
                        service_cost[hr_analytic_timesheet.product_id.id] += abs(hr_analytic_timesheet.amount)
                    else:
                        service[hr_analytic_timesheet.product_id.id] = hr_analytic_timesheet.unit_amount
                        service_cost[hr_analytic_timesheet.product_id.id] = abs(hr_analytic_timesheet.amount)

                if service:
                    for service_product in service:
                        product = self.pool['product.product'].browse(cr, uid, service_product, context)
                        values = {
                            'product_uos_qty': don_t_group_service_line and service[service_product] or 1,
                            'product_uom_qty': don_t_group_service_line and service[service_product] or 1,
                            'service_cost_price': service_cost[service_product],
                            'price_unit': don_t_group_service_line and product.list_price or product.list_price * service[service_product],
                        }

                        if repair.temp_so_id and repair.temp_so_lines:
                            temp_service_products = dict([(temp_so_line.product_id.id, temp_so_line) for temp_so_line in repair.temp_so_lines])

                            if service_product in temp_service_products:
                                self.pool['temp.sale.order.line'].write(cr, uid, [temp_service_products[service_product].id], values)
                            else:
                                val = self.pool['account.invoice.line'].product_id_change(cr, uid, [], service_product,
                                                                                          uom=False, partner_id=repair.customer_id.id, fposition_id=repair.customer_id.property_account_position.id)
                                res = val['value']

                                values.update({
                                    'name': "[{code}] {name}".format(code=product.default_code or ' ', name=product.name),
                                    'product_id': service_product,
                                    'repair_order_id': repair.id,
                                    'order_id': repair.temp_so_id.sale_order_id.id,
                                    'delay': product.produce_delay,
                                    'product_uom': product.uom_id.id,
                                    'tax_id': [(6, 0, res.get('invoice_line_tax_id'))],
                                    'type': 'make_to_stock',
                                    })
                                self.pool['temp.sale.order.line'].create(cr, uid, values, context)
                        else:
                            val = self.pool['account.invoice.line'].product_id_change(cr, uid, [], service_product,
                                                                                      uom=False, partner_id=repair.customer_id.id, fposition_id=repair.customer_id.property_account_position.id)
                            res = val['value']

                            values.update({
                                'name': "[{code}] {name}".format(code=product.default_code or ' ', name=product.name),
                                'product_id': service_product,
                                'repair_order_id': repair.id,
                                'delay': product.produce_delay,
                                'product_uom': product.uom_id.id,
                                'tax_id': [(6, 0, res.get('invoice_line_tax_id'))],
                                'type': 'make_to_stock',
                                })
                            self.pool['temp.sale.order.line'].create(cr, uid, values, context)
            
        return result

    def copy(self, cr, uid, order_id, defaults, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        raise orm.except_orm(_('Warning'), _("Repair order can't be duplicated"))
        return False

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        repair_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for repair in repair_orders:
            if repair['state'] in ['draft', 'cancel']:
                unlink_ids.append(repair['id'])
            else:
                raise orm.except_orm(_('Invalid action !'), _('Is impossible to Cancel a Repair Order'))
        return super(repair_order, self).unlink(cr, uid, unlink_ids, context)

    def on_change_product(self, cr, uid, ids, product_id):
        res = {'value': {}}
        if product_id:
            vals = {}
            product = self.pool['product.product'].browse(cr, uid, product_id)
            vals.update({
                'manufacturer': product.manufacturer and product.manufacturer.id or False,
                'manufacturer_pname': product.manufacturer_pname or product.name,
                'manufacturer_pref': product.manufacturer_pref or product.default_code,
                # 'product_category': product.categ_id and product.categ_id.id or False
            })
            res.update({'value': vals})
        return res
    
    def on_change_machine(self, cr, uid, ids, machine_id):
        res = {'value': {}}
        if machine_id:
            vals = {}
            machine = self.pool['repair.machine'].browse(cr, uid, machine_id)
            vals.update({
                'manufacturer': machine.manufacturer and machine.manufacturer.id or False,
                'manufacturer_pname': machine.model or False,
                'manufacturer_pref': machine.telaio or machine.plate or False,
                'account_id': machine.account_id and machine.account_id.id or False,
                'product_id': machine.product_id and machine.product_id.id or False,
                # 'product_category': product.categ_id and product.categ_id.id or False
            })
            res.update({'value': vals})
        return res
    
    def on_change_move_id(self, cr, uid, ids, move_id, product_id=None, customer_id=None, order_date=None):
        res = {'value': {}}
        if move_id:
            vals = {}
            move = self.pool['stock.move'].browse(cr, uid, move_id)
            purchased_date = move.date or move.create_date
            order_date = order_date or datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
            last_warranty_date = datetime.datetime.strptime(purchased_date, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(months=int(move.product_id.warranty or 0))
            under_warranty = False
            if last_warranty_date.strftime(DEFAULT_SERVER_DATE_FORMAT) >= order_date:
                under_warranty = True

            vals.update({
                'purchased_date': purchased_date,
                # 'serial': move.prodlot_id and "/".join([move.prodlot_id.prefix, move.prodlot_id.name]) or False,
                'serial': move.prodlot_id and move.prodlot_id.id or False,
                'under_warranty': under_warranty,
            })

            if under_warranty:
                vals.update({'invoice_method': 'after_repair', 'paid_by': 'manufacturer'})
            
            if not product_id or product_id != move.product_id.id:
                vals.update({'product_id': move.product_id.id})
                product_updates = self.on_change_product(cr, uid, ids, move.product_id.id)
                vals.update(product_updates.get('value', {}))
            if not customer_id:
                vals.update({'customer_id': move.partner_id.id})
                customer_updates = self.on_change_customer(cr, uid, ids, move.partner_id.id)
                vals.update(customer_updates.get('value', {}))
            res.update({'value': vals})
        return res

    def on_change_under_warranty(self, cr, uid, ids, under_warranty):
        res = {'value': {}}
        vals = {}
        if under_warranty:
            vals.update({
                'invoice_method': 'after_repair', 'paid_by': 'manufacturer'
            })
        else:
            vals.update({'paid_by': 'customer'})
        res['value'] = vals
        return res

    def on_change_customer(self, cr, uid, ids, customer_id, dest_address_id=None):
        context = self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if customer_id:
            vals = {}
            warning = {}
            sale_value = self.pool['sale.order'].onchange_partner_id(cr, uid, ids, customer_id)
            customer = self.pool['res.partner'].browse(cr, uid, customer_id, context)

            if sale_value.get('warning', False):
                warning = {
                    'title': sale_value['warning']['title'] or sale_value['warning']['title'],
                    'message': sale_value['warning']['message'] or sale_value['warning']['message'],
                }

            partner_address_id = sale_value['value'].get('partner_shipping_id')
            if partner_address_id and not dest_address_id:
                partner_contact = self.pool['res.partner.address'].browse(cr, uid, partner_address_id, context)
                vals.update(
                    {
                        'partner_address_id': partner_address_id,
                        'phone': partner_contact.phone and partner_contact.phone or customer.phone,
                        'email': partner_contact.email and partner_contact.email or customer.email,
                    }
                )

            if not partner_address_id and not dest_address_id:
                vals.update(
                    {
                        'phone': customer.phone,
                        'email': customer.email,
                    }
                )

            vals.update(
                {
                    'pricelist_id': sale_value['value'].get('pricelist_id')
                })
            res.update({'value': vals})

        return {'value': res.get('value', {}), 'warning': warning}

    def action_picking_create(self, cr, uid, order_ids, context):
        stock_move_obj = self.pool['stock.move']
        context = context or self.pool['res.users'].context_get(cr, uid)
        picking_id = False
        for order in order_ids:
            picking_id = None
            if order.in_picking_id:
                picking_id = order.in_picking_id.id
            else:
                loc_id = order.customer_id.property_stock_customer.id
                invoice_state = 'none'
                pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.in')
                picking_id = self.pool['stock.picking'].create(cr, uid, {
                    'name': pick_name,
                    'origin': order.name,
                    'type': 'in',
                    'address_id': order.dest_address_id.id or order.partner_address_id.id,
                    'invoice_state': invoice_state,
                    'company_id': order.company_id.id,
                    'move_lines': [],
                }, context)

                if order.product_id:
                    # dest = order.warehouse_id and order.warehouse_id.lot_input_id.id or False
                    dest = order.company_id.repair_location_id.id
                    move_vals = {
                        'name': order.name + ': ' + (order.manufacturer_pname or order.manufacturer_pref or ''),
                        'product_id': order.product_id.id,
                        'product_qty': 1,
                        'product_uos_qty': 1,
                        'product_uom': order.product_id.uom_id.id,
                        'product_uos': order.product_id.uom_id.id,
                        'date': datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'location_id': loc_id,
                        'location_dest_id': dest,
                        'picking_id': picking_id,
                        'state': 'draft',
                        'company_id': order.company_id.id,
                        'prodlot_id': order.serial and order.serial.id or False,
                    }

                    if not order.serial and order.machine_id:
                        existing_prodlot_ids = self.pool['stock.production.lot'].search(cr, uid, [('name', '=', order.machine_id.telaio), ('product_id', '=', order.product_id.id)])
                        if not existing_prodlot_ids:
                            prodlot_id = self.pool['stock.production.lot'].create(cr, uid, {
                                'name': order.machine_id.telaio,
                                'product_id': order.product_id.id,
                            }, context)
                        else:
                            prodlot_id = existing_prodlot_ids[0]
                        move_vals.update({'prodlot_id': prodlot_id})
                        order.write({'serial': prodlot_id})

                    move_id = stock_move_obj.create(cr, uid, move_vals, context)
                    stock_move_obj.action_confirm(cr, uid, [move_id])
                    stock_move_obj.force_assign(cr, uid, [move_id])
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        return picking_id

    def button_study(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        for order in self.read(cr, uid, ids, context=context):
            message = _("The Repair order '%s' is going to study by %s.") % (order['name'], user.name)
            self.log(cr, uid, order['id'], message)
        return self.write(cr, uid, ids, {'state': 'study'})

    def button_confirm(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for order in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [order.id], {'state': 'confirmed'}, context)
            message = _("The Repair order '%s' has been confirmed.") % (order.name)
            self.log(cr, uid, order.id, message)
            if order.in_picking_id:
                if order.in_picking_id.state != 'done':
                    return self.pool['stock.picking'].action_process(cr, uid, [order.in_picking_id.id], context=context)
            else:
                picking_id = self.action_picking_create(cr, uid, [order], context)
                if picking_id:
                    self.write(cr, uid, ids, {'in_picking_id': picking_id}, context)
                    return self.pool['stock.picking'].action_process(cr, uid, [picking_id], context=context)
        return True

    def action_cancel_draft(self, cr, uid, ids, *args):
        """ Cancels repair order when it is in 'Draft' state.
        @param *arg: Arguments
        @return: True
        """
        context = self.pool['res.users'].context_get(cr, uid)
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        if not len(ids):
            return False
        sale_obj = self.pool['sale.order']
        for repair in self.browse(cr, uid, ids, context):
            if repair.so_id:
                # so should be in draft state
                sale_obj.action_cancel_draft(cr, uid, [repair.so_id.sale_order_id.id])
        self.write(cr, uid, ids, {'state': 'draft'}, context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'repair.order', id, cr)
            wf_service.trg_create(uid, 'repair.order', id, cr)
        return True

    def reception_confirm(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        order = self.browse(cr, uid, ids[0], context)
        sale_order_obj = self.pool['sale.order']

        sale_order_ids = sale_order_obj.search(cr, uid, [('name', '=', order.name)], context=context)

        if sale_order_ids:
            for sale_order in sale_order_obj.browse(cr, uid, sale_order_ids, context=context):
                if sale_order.name == order.name:
                    # here i search repair.order
                    # carlo 26 agosto 2015, qui sotto c'è un po' di confusione
                    # 18 febbraio 2016 testato dopo errore segnalato da sc
                    # TODO: verificare
                    order_id = self.search(cr, uid, [('sale_id', '=', sale_order.id)], context=context)
                    if order_id:
                        old_order = self.browse(cr, uid, order_id, context=context)[0]
                        # quotation
                        sale_order_obj.write(cr, uid, sale_order.id, {'name': old_order.name}, context)
                        if old_order.temp_sale_id:
                            sale_order_obj.write(cr, uid, old_order.temp_sale_id.id, {'name': old_order.name + '_CONSUNTIVO_'}, context)
                    else:
                        raise orm.except_orm(_('Error'), _('There are a Sale Order with same name of Repair \n and not any orphan Repair Order'))
        
        if not order.sale_id:
            if not company.repair_shop_id:
                raise orm.except_orm(_('Warning'), _('Please set repair shop'))

            sale_order_vals = self.pool['sale.order'].onchange_partner_id(cr, uid, ids, order.customer_id.id)
            if sale_order_vals.get('warning', False) and order.customer_id.sale_warn == 'block':
                warning = {
                    'title': sale_order_vals['warning']['title'] or sale_order_vals['warning']['title'],
                    'message': sale_order_vals['warning']['message'] or sale_order_vals['warning']['message'],
                }
                raise orm.except_orm(warning['title'], warning['message'])

            if not (order.dest_address_id or order.partner_address_id):
                raise orm.except_orm(_('Error'), _('Missing Address'))

            sale_order_params = sale_order_vals['value']
            sale_order_params.update({
                'partner_id': order.customer_id.id,
                'name': order.name,
                'shop_id': company.repair_shop_id.id,
                'partner_order_id': order.dest_address_id.id or order.partner_address_id.id,
                'partner_shipping_id': order.dest_address_id.id or order.partner_address_id.id,
                'date_order': order.order_date,
                'client_order_ref': order.customer_ref,
                'origin': order.name,
                'repair_order_id': order.id,
                'order_policy': 'manual',
                'project_id': order.account_id.id or '',
            })

            if order.customer_id.property_account_position:
                sale_order_params.update({
                    'fiscal_position': order.customer_id.property_account_position.id,
                })

            so_id = self.pool['repair.sale.order'].create(cr, uid, sale_order_params, context)
            project_so = self.pool['repair.sale.order'].browse(cr, uid, so_id, context=context).project_id
            vals = {
                'so_id': so_id,
                'account_id': project_so and project_so.id or ''
            }
            self.pool['repair.order'].write(cr, uid, [order.id], vals, context=context)

        if order.customer_id.id == company.partner_id.id or order.on_site:
            if order.company_id.skip_quotation_on_onsite:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'repair.order', ids[0], 'direct_repair', cr)
                order.write({'is_analized': True})
            else:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'repair.order', ids[0], 'reception_confirm', cr)
                order.write({'confirmed': True})
            return {}
        else:
            return {
                'name': _('Set Origin Document'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'repair.set.origin',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }

    # --Fixing
    def action_confirm(self, cr, uid, ids, context=None):
        """ Repair order state is set to 'To be invoiced' when invoice method
        is 'Before repair' else state becomes 'Confirmed'.
        @param *arg: Arguments
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
            
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        
        for order in self.browse(cr, uid, ids, context):
            if not order.in_picking_id and not order.customer_id.id == company.partner_id.id and not order.on_site:
                picking_id = self.action_picking_create(cr, uid, [order], context)
                if picking_id:
                    self.write(cr, uid, ids, {'in_picking_id': picking_id})
                    partial_id = self.pool['stock.partial.picking'].create(
                        cr, uid, {'date': datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=dict(active_ids=[picking_id], active_model='stock.picking'))
                    self.pool['stock.partial.picking'].do_partial(cr, uid, [partial_id], context=dict(active_ids=[picking_id], active_model='stock.picking'))
            
            if order.is_analized:
                if order.is_analized and order.invoice_method == 'b4repair' and not order.invoiced:
                    self.write(cr, uid, [order.id], {'state': '2binvoiced'})
                elif order.is_analized and (order.invoice_method != 'b4repair' or order.invoiced) and not order.repairable and not order.outward_producer_ok:
                    self.write(cr, uid, [order.id], {'state': 'sending2manu'})
                else:
                    self.write(cr, uid, [order.id], {'state': 'confirmed'})
            else:
                # If under_warranty, workflow will set state to "ready"
                if not order.under_warranty:
                    self.write(cr, uid, [order.id], {'state': 'confirmed'})
                self.log(cr, uid, order.id, _("The Repair order '%s' has been confirmed.") % (order.name))
        
        return {}

    def action_cancel(self, cr, uid, ids, context=None):
        """ Cancels repair order.
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        wf_service = netsvc.LocalService("workflow")
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.sale_id and repair.sale_id.state != 'draft':
                wf_service.trg_validate(uid, 'sale.order', repair.sale_id.id, 'cancel', cr)
            if repair.temp_sale_id:
                wf_service.trg_validate(uid, 'sale.order', repair.temp_sale_id.id, 'cancel', cr)
        self.write(cr, uid, ids, {'state': 'cancel', 'is_analized': False})
        return True

    def action_ready(self, cr, uid, ids, context=None):
        """ Ready repair order.
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.account_id:
                self.pool['account.analytic.account'].write(cr, uid, repair.account_id.id, {'state' : 'open'}, context)
            self.write(cr, uid, ids, {'state': 'ready'}, context)
        return True
    
    #def action_send2supplier(self, cr, uid, ids, group=False, context=None):
    #    res = {}
    #    for repair in self.browse(cr, uid, ids, context=context):
    #        if repair.out_picking2producer_id and repair.out_picking2producer_id.state != 'done':
    #            partial_id = self.pool['stock.partial.picking'].create(
    #                cr, uid, {}, context=dict(active_ids=[repair.out_picking2producer_id.id]))
    #            self.pool['stock.partial.picking'].do_partial(cr, uid, [partial_id], context=dict(active_ids=[repair.out_picking2producer_id.id]))
    #        res[repair.id] = True
    #    return res

    def action_reception(self, cr, uid, ids, group=False, context=None):
        res = {}
        for repair in self.browse(cr, uid, ids, context=context):
            if repair.in_picking_producer_id and repair.in_picking_producer_id.state != 'done':
                partial_id = self.pool['stock.partial.picking'].create(
                    cr, uid, {}, context=dict(active_ids=[repair.in_picking_producer_id.id]))
                self.pool['stock.partial.picking'].do_partial(cr, uid, [partial_id], context=dict(active_ids=[repair.in_picking_producer_id.id]))
            res[repair.id] = True
        return res

    def action_invoice_create(self, cr, uid, ids, group=False, context=None):
        """ Creates invoice(s) for repair order.
        @param group: It is set to true when group invoice is to be generated.
        @return: Invoice Ids.
        """
        
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        
        wf_service = netsvc.LocalService("workflow")
        res = {}
        ids_2binvoiced = []
        
        for repair_order in self.browse(cr, uid, ids, context=context):
            if repair_order.state == '2binvoiced' and repair_order.temp_sale_id and repair_order.temp_sale_id.invoice_ids:
                # qualcosa non ha funzionato....
                repair_order.write({'state': 'done'})
                continue
            if repair_order.state in ('draft', 'cancel') or repair_order.invoice_id:
                continue

            if repair_order.invoice_method == 'b4repair':
                # Disabled until special instructions from customer:
                #if not repair_order.repairable:
                #    self.write(cr, uid, [repair_order.id], {'state': 'sending2manu'}, context=context)
                #else:
                # Create invoice
                if not repair_order.customer_id.property_account_receivable:
                    raise orm.except_orm(_('Error !'), _('No account defined for customer "%s".') % repair_order.customer_id.name)
                if not repair_order.so_id:
                    raise orm.except_orm(_('Error !'), _('No Sale Order defined for repair Order "%s".') % repair_order.name)
                else:
                    self.pool['sale.order'].advance_invoice_create(cr, uid, repair_order.so_id.sale_order_id.id, context) 
                    self.write(cr, uid, [repair_order.id], {'state': 'ready'}, context=context)
            elif repair_order.invoice_method == 'after_repair':
                if repair_order.temp_sale_id and repair_order.temp_sale_id.state == 'cancel':
                    wf_service.trg_validate(uid, 'sale.order', repair_order.temp_sale_id.id, 'action_cancel_draft', cr)
                    wf_service.trg_validate(uid, 'sale.order', repair_order.temp_sale_id.id, 'repair_confirm', cr)
                    repair_order = self.browse(cr, uid, repair_order.id, context=context)  # da fare perchè browse ha cache e non ci sarebbe dentro
                if repair_order.temp_sale_id and repair_order.temp_sale_id.state == 'shipping_except':
                    wf_service.trg_validate(uid, 'sale.order', repair_order.temp_sale_id.id, 'ship_corrected', cr)
                    repair_order = self.browse(cr, uid, repair_order.id, context=context)
                if repair_order.sale_id.state == 'manual' or repair_order.temp_sale_id.state == 'manual':
                    if repair_order.sale_id.state == 'manual':
                        sale_order_id = repair_order.sale_id.id
                    else:
                        # repair_order.temp_so_id.state == 'manual':
                        sale_order_id = repair_order.temp_sale_id.id
                    
                    if repair_order.under_warranty:
                        context.update({
                            'sale_order_id': sale_order_id,
                            'repair_order_id': repair_order.id
                        })
                        return {
                            'name': _('Set Recipient'),
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'repair.set.partner',
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                            'context': context
                        }
                    else:
                        ids_2binvoiced.append(sale_order_id)
        
        if ids_2binvoiced:  # Create invoice
            invoice_id = self.pool['sale.order'].action_invoice_create(
                  cr, uid, ids_2binvoiced, grouped=group,
                  states=['draft', 'confirmed', 'done', 'exception'], date_inv=False, context=context)
        else:
            invoice_id = False
        
        if invoice_id:
            res.update({'invoice_id': invoice_id})
        for sale_order_id in ids_2binvoiced:
            wf_service.trg_validate(uid, 'sale.order', sale_order_id, 'manual_invoice', cr)
        for repair_order in self.browse(cr, uid, ids, context=context):
            wf_service.trg_validate(uid, 'repair.order', repair_order.id, 'action_invoice_create', cr)
        return res

    def action_invoice_cancel(self, cr, uid, ids, context=None):
        """ Writes repair order state to 'Exception in invoice'
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'invoice_except'}, context)
        return True

    def action_invoice_end(self, cr, uid, ids, context=None):
        """ Writes repair order state to 'Ready' if invoice method is Before repair.
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        repair_line = self.pool['mrp.repair.line']
        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            if order.invoice_method == 'b4repair':
                val['state'] = 'ready'
                repair_line.write(cr, uid, [l.id for
                                            l in order.operations], {'state': 'confirmed'}, context=context)

            self.write(cr, uid, [order.id], val, context=context)
        return True

    def reair_order_confirm_hook(self, cr, uid, order, sale_order, context):
        # todo here need to validate exit of product
        if sale_order.company_id.auto_exit_product:
            sale_order.picking_ids[0].write({'auto_picking': True})
            sale_order.picking_ids[0].force_assign()

        return True

    def wkf_customer_delivery(self, cr, uid, ids, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        
        wf_service = netsvc.LocalService("workflow")
        
        for order in self.browse(cr, uid, ids, context):
            if order.in_picking_id and order.inward_ok:
                if not order.out_picking_id:
                    # Create Out Picking of a repaired product
                    istate = 'none'
                    pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.out')
                    stock_journal_id = self.pool['ir.model.data'].get_object(cr, uid, 'stock', 'journal_reso4').id
                    
                    picking_id = self.pool['stock.picking'].create(cr, uid, {
                        'name': pick_name,
                        'origin': order.name,
                        'type': 'out',
                        'address_id': (order.dest_address_id and order.dest_address_id.id) or (order.partner_address_id and order.partner_address_id.id) or order.customer_id.id,
                        'invoice_state': istate,
                        'company_id': order.company_id.id,
                        'move_lines': [],
                        'stock_journal_id': stock_journal_id,
                        'sale_project': order.account_id and order.account_id.id or False,
                        'address_delivery_id': (order.dest_address_id and order.dest_address_id.id) or (order.partner_address_id and order.partner_address_id.id) or False,
                    }, context)
                    
                    repair_order_reception = order.in_picking_id
                    # -- add every incomming product to delivery
                    for mv in repair_order_reception.move_lines:
                        move_vals = {
                            'name': mv.name,
                            'product_id': mv.product_id.id,
                            'product_qty': mv.product_qty,
                            'product_uos_qty': mv.product_uos_qty,
                            'product_uom': mv.product_uom.id,
                            'product_uos': mv.product_uos.id,
                            'date': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'location_id': mv.location_dest_id.id,
                            'location_dest_id': mv.location_id.id,
                            'picking_id': picking_id,
                            'state': 'draft',
                            'company_id': order.company_id.id,
                            'prodlot_id': mv.prodlot_id.id,
                        }
                        move_id = self.pool['stock.move'].create(cr, uid, move_vals, context)
                        self.pool['stock.move'].action_confirm(cr, uid, [move_id])
                    
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                    self.pool['stock.picking'].force_assign(cr, uid, [picking_id], context)
                    sp_context = dict(active_ids=[picking_id], active_model='stock.picking')
                    partial_id = self.pool["stock.partial.picking"].create(cr, uid, {'date': datetime.date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=sp_context)
                    self.pool['stock.partial.picking'].do_partial(cr, uid, [partial_id], context=sp_context)
                    # self.pool['wizard.assign.ddt'].assign_ddt(cr, uid, None, context=sp_context)
                    
                    self.write(cr, uid, [order.id], {'out_picking_id': picking_id})
            if order.so_id or order.temp_so_id:
                self.write(cr, uid, [order.id], {'state': 'wait_outgo'})
        return {}

    def check_wait(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if self.check_same_partner(cr, uid, ids, context):
            self.pool['repair.order'].write(cr, uid, ids, {'state': 'done'}, context=context)
            return True
        else:
            return False

    def check_same_partner(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        repair_order = self.browse(cr, uid, ids[0], context)
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        if repair_order.customer_id.id == company.partner_id.id:
            return True
        else:
            return False

    def wkf_outgo(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        wf_service = netsvc.LocalService("workflow")
        company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
        
        for order in self.browse(cr, uid, ids, context):
            # Create Delivery Note (stock.picking) of replaced products:
            if order.so_id.state == 'draft' or order.temp_so_id.state == 'draft':
                # Test if temp_sale_order == repair_sale_order:
                if order.so_lines and len(order.so_lines) == len(order.temp_so_lines):
                    estimated_lines = {}
                    for line in order.so_lines:
                        estimated_lines[line.product_id.id] = {'product_uom_qty': line.product_uom_qty}
                    for line in order.temp_so_lines:
                        if not (estimated_lines.get(line.product_id.id, False) and estimated_lines[line.product_id.id]['product_uom_qty'] == line.product_uom_qty):
                            estimated_products = False
                            break
                    else:
                        estimated_products = True
                else:
                    estimated_products = False

                if estimated_products:
                    sale_order_id = order.so_id.sale_order_id.id
                    # Disable Temp Order
                    # TODO: THIS LINE SHOULD be removed as fast as possible!!!
                    if order.temp_so_id:
                        order.temp_so_id.sale_order_id.write({'active': False})
                elif order.temp_so_id:
                    sale_order_id = order.temp_so_id and order.temp_so_id.sale_order_id.id

                    if order.so_id:
                        vals = {
                            'version': (order.so_id.sale_order_id.version and order.so_id.sale_order_id.version or 1) + 1,
                            'sale_version_id': order.so_id.sale_order_id.sale_version_id or order.so_id.sale_order_id.id,
                            'name': (order.so_id.sale_order_id.sale_version_id and order.so_id.sale_order_id.sale_version_id.name or order.so_id.sale_order_id.name) + u" Consuntivo"
                        }
                        order.so_id.sale_order_id.write({'active': False})
                    else:
                        vals = {
                            'name': self.pool['ir.sequence'].get(cr, uid, 'sale.order')
                        }
                    
                    order.temp_so_id.sale_order_id.write(vals)
                else:
                    sale_order_id = False
                    
                if sale_order_id:
                    # Create out_picking:
                    sale_order = self.pool['sale.order'].browse(cr, uid, sale_order_id, context)
                    sale_order.write({'picking_policy': 'one'})
                    wf_service.trg_validate(uid, 'sale.order', sale_order_id, 'repair_confirm', cr)

                    self.reair_order_confirm_hook(cr, uid, order, sale_order, context)

            else:
                sale_order_id = False

            if order.invoice_method == 'after_repair' and not order.customer_id.id == company.partner_id.id:
                self.write(cr, uid, [order.id], {'state': '2binvoiced'})
            elif order.invoice_method == 'after_repair':
                self.write(cr, uid, [order.id], {'state': 'done'})
            
        return {}
    
    def get_customer_products(self, cr, uid, customer_id, context):
        # TODO: add check that product is not already in the stock for repair.
        order_ids = self.search(cr, uid, [('customer_id', '=', customer_id)])
        if order_ids:
            return [order.product_id.id for order in self.browse(cr, uid, order_ids, context)]
        else:
            return []
    
    # def check_piking_done(self, cr, uid, ids, context=None):
    #    """ Checks if move is done or not.
    #    @return: True or False.
    #    """
    #    
    #    return all(not order.temp_so_id or (order.out_picking_id and order.out_picking_id.state == 'done')
    #               for order in self.browse(cr, uid, ids, context=context))
    
    def action_finish(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return {}
    
    def copy_quotation(self, cr, uid, ids, context):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        
        repair_order = self.browse(cr, uid, ids[0], context)
        
        for line in repair_order.so_lines:
            if line.product_id and line.product_id.type != 'service':
                self.pool['temp.sale.order.line'].create(cr, uid, {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'product_uos_qty': line.product_uos_qty,
                    'product_uom_qty': line.product_uom_qty,
                    'repair_order_id': repair_order.id,
                    'cost_price': line.product_id.cost_price,
                    'delay': line.product_id.produce_delay,
                    'product_uom': line.product_uom.id,                    
                    'product_uos': line.product_uos.id,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'tax_id': [(6, 0, [tax.id for tax in line.tax_id])],
                    'type': line.type
                })
        
        return True

    #def action_picking_create_reception(self, cr, uid, ids, context=None):
    #    picking_id = False
    #    for order in self.browse(cr, uid, ids):
    #        if order.repairable:
    #            continue
    #        if order.out_picking2producer_id and order.out_picking2producer_id.state != 'done':
    #            raise orm.except_orm(_('Error !'), _('Delivery to Supplier/Producer is not done yet.'))
    #
    #        picking_id = None
    #        if order.in_picking_producer_id:
    #            picking_id = order.in_picking_producer_id.id
    #        else:
    #            loc_id = order.out_picking2producer_id.address_id.partner_id.property_stock_supplier.id
    #            istate = 'none'
    #            pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.in')
    #            picking_id = self.pool['stock.picking'].create(cr, uid, {
    #                'name': pick_name,
    #                'origin': order.name,
    #                'type': 'out',
    #                'address_id': order.out_picking2producer_id.address_id.id,
    #                'invoice_state': istate,
    #                'company_id': order.company_id.id,
    #                'move_lines': [],
    #            })
    #
    #            self.write(cr, uid, [order.id], {'in_picking_producer_id': picking_id, 'state': 'wait_reception'})
    #
    #            if order.product_id:
    #                dest = order.warehouse_id and order.warehouse_id.lot_input_id.id or False
    #                new_prodlot = None
    #                if order.in_picking_id:
    #                    move_lines = self.pool['stock.move'].search(cr, uid, [('picking_id', '=', order.in_picking_id.id), ('product_id', '=', order.product_id.id)])
    #                    if len(move_lines) > 0:
    #                        product_move = self.pool['stock.move'].browse(cr, uid, move_lines[0])
    #                        if product_move.prodlot_id:
    #                            new_prodlot = product_move.prodlot_id.id
    #                move_vals = {
    #                    'name': order.name + ': ' + order.manufacturer_pname or '' + order.manufacturer_pref and "[%s]" % (order.manufacturer_pref) or '',
    #                    'product_id': order.product_id.id,
    #                    'product_qty': 1,
    #                    'product_uos_qty': 1,
    #                    'product_uom': order.product_id.uom_id.id,
    #                    'product_uos': order.product_id.uom_id.id,
    #                    'date': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
    #                    'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
    #                    'location_id': loc_id,
    #                    'location_dest_id': dest,
    #                    'picking_id': picking_id,
    #                    'state': 'draft',
    #                    'company_id': order.company_id.id,
    #                    'prodlot_id': new_prodlot,
    #                }
    #                move = self.pool['stock.move'].create(cr, uid, move_vals)
    #                self.pool['stock.move'].action_confirm(cr, uid, [move])
    #                self.pool['stock.move'].force_assign(cr, uid, [move])
    #                wf_service = netsvc.LocalService("workflow")
    #                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
    #    return picking_id

    #def action_picking_create_producer(self, cr, uid, ids, context=None):
    #    #print "action_picking_create_producer is called "
    #    picking_id = False
    #    for order in self.browse(cr, uid, ids):
    #        if order.repairable:
    #            continue
    #        picking_id = None
    #        if order.out_picking2producer_id:
    #            picking_id = order.out_picking2producer_id.id
    #        else:
    #            loc_id = order.manufacturer.property_stock_supplier.id
    #            istate = 'none'
    #
    #            address_ids = self.pool['res.partner'].address_get(cr, uid, [order.manufacturer.id], ['default', 'delivery'])
    #            address_id = address_ids['delivery'] and address_ids['delivery'] or address_ids['default']
    #            pick_name = self.pool['ir.sequence'].get(cr, uid, 'stock.picking.out')
    #            picking_id = self.pool['stock.picking'].create(cr, uid, {
    #                'name': pick_name,
    #                'origin': order.name,
    #                'type': 'out',
    #                'address_id': address_id,
    #                'invoice_state': istate,
    #                'company_id': order.company_id.id,
    #                'move_lines': [],
    #            })
    #
    #            self.write(cr, uid, [order.id], {'out_picking2producer_id': picking_id, 'state': 'sending2manu'})
    #
    #            if order.product_id:
    #                source = order.location_id and order.location_id.id or (order.warehouse_id and order.warehouse_id.lot_input_id.id or False)
    #                new_prodlot = None
    #                if order.in_picking_id:
    #                    move_lines = self.pool['stock.move'].search(cr, uid, [('picking_id', '=', order.in_picking_id.id), ('product_id', '=', order.product_id.id)])
    #                    if len(move_lines) > 0:
    #                        product_move = self.pool['stock.move'].browse(cr, uid, move_lines[0])
    #                        if product_move.prodlot_id:
    #                            new_prodlot = product_move.prodlot_id.id
    #                move_vals = {
    #                    'name': order.name + ': ' + order.manufacturer_pname or '' + order.manufacturer_pref and "[%s]" % (order.manufacturer_pref) or '',
    #                    'product_id': order.product_id.id,
    #                    'product_qty': 1,
    #                    'product_uos_qty': 1,
    #                    'product_uom': order.product_id.uom_id.id,
    #                    'product_uos': order.product_id.uom_id.id,
    #                    'date': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
    #                    'date_expected': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
    #                    'location_id': source,
    #                    'location_dest_id': loc_id,
    #                    'picking_id': picking_id,
    #                    'state': 'draft',
    #                    'company_id': order.company_id.id,
    #                    'prodlot_id': new_prodlot,
    #                }
    #                move = self.pool['stock.move'].create(cr, uid, move_vals)
    #                self.pool['stock.move'].action_confirm(cr, uid, [move])
    #                self.pool['stock.move'].force_assign(cr, uid, [move])
    #                wf_service = netsvc.LocalService("workflow")
    #                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
    #    return picking_id

    #def action_repair_ready(self, cr, uid, ids, context=None):
    #    """ Writes repair order state to 'Ready'
    #    @return: True
    #    """
    #    #print "action_repair_ready is called "
    #    for repair in self.browse(cr, uid, ids, context=context):
    #        #self.pool['mrp.repair.line').write(cr, uid, [l.id for
    #        #        l in repair.operations], {'state': 'confirmed'}, context=context)
    #        self.write(cr, uid, [repair.id], {'state': 'ready'})
    #    return True


class repair_order_accessory(orm.Model):
    _name = 'repair.order.accessory'
    _description = 'Repair Order Accessory'
    _columns = {
        'accessory_id': fields.many2one("product.accessory", "Accessory", required=True),
        'order_id': fields.many2one("repair.order", "Repair Order"),
        'product_uom_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoM')),
        'serial': fields.many2one('stock.production.lot', "Serial Number", ondelete="no action", required=False),
        'note': fields.text("Note")
    }


class repair_order_on_site(orm.Model):
    _name = 'repair.order.on.site'
    _description = 'On-site repair'

    _columns = {
        'repair_order_id': fields.many2one('repair.order', 'Repair Order'),
        'start_from': fields.many2one('res.city', _('City')),
        'start_time': fields.datetime(_('From')),
        'end_arrival': fields.many2one('res.city', _('City')),
        'end_time': fields.datetime(_('To')),
        'note': fields.text(_('Note'))
    }
