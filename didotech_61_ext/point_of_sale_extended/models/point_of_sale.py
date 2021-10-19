# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Didotech SRL
#
#                          All Rights Reserved.
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

import logging
import time

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from tools.translate import _

_logger = logging.getLogger('pos_order')
import StringIO
import openerp.tools as tools

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    _logger.debug('Cannot `import barcode`.')  # Avoid init error if not installed


def bar_code_image(code):
    EAN = barcode.get_barcode_class('ean13')
    ean = EAN(code, writer=ImageWriter())
    io_stream = StringIO.StringIO()
    ean.write(io_stream)
    return io_stream.getvalue().encode('base64')


class PosOrder(orm.Model):
    _inherit = "pos.order"

    def _auto_init(self, cr, context={}):
        super(PosOrder, self)._auto_init(cr, context)

        cr.execute("SELECT 1 FROM pg_indexes WHERE indexname='pos_order_user_id_index'")
        if not cr.fetchone():
            cr.execute('CREATE INDEX pos_order_user_id_index ON pos_order (user_id)')

        cr.execute("SELECT 1 FROM pg_indexes WHERE indexname='pos_order_user_id_shop_id_index'")
        if not cr.fetchone():
            cr.execute('CREATE INDEX pos_order_user_id_shop_id_index ON pos_order (user_id, shop_id)')

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = []
        tz = context.get('tz') or self.pool['res.users'].context_get(cr, uid).get('tz')
        context.update({'context_tz': tz})
        if not vals.get('sale_journal', False):
            sale_journal_id = self._default_sale_journal(cr, uid, context)
            if not sale_journal_id:
                raise orm.except_orm(_(u'ERROR'),
                                     _(u'There are no Sale Journal, please craete a Journal of type \'Sale\' for user {user}'.format(user=self.pool['res.users'].browse(cr, uid, uid).name)))
            vals.update({'sale_journal': sale_journal_id})
        else:
            journal = self.pool['account.journal'].browse(cr, uid, vals.get('sale_journal'), context)
            if not journal:
                vals.update({'sale_journal': self._default_sale_journal(cr, uid, context)})

        if context.get('hashcode', False):
            line_hashcode = self.search(cr, uid, [('hashcode', '=', context.get('hashcode')), ('user_id', '=', uid)], limit=1, context=context)
            if line_hashcode:
                res = line_hashcode[0]
            vals.update({'hashcode': context.get('hashcode')})
        if context.get('customer_code', False):
            customer_code = context.get('customer_code')
            partner_ids = self.pool['res.partner'].search(cr, uid, [('property_customer_ref', '=', customer_code)], context=context)
            if partner_ids:
                vals.update({'partner_id': partner_ids[0]})
            vals.update({'customer_code': customer_code})
        if not res:
            res = super(PosOrder, self).create(cr, uid, vals, context=context)
        return res

    def action_invoice(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(PosOrder, self).action_invoice(cr, uid, ids, context=context)
        view = self.pool['ir.model.data'].get_object_reference(cr, uid, 'point_of_sale_extended', 'invoice_smart_form')
        res_id = view and view[1] or False
        res['view_id'] = [res_id],

        order = self.browse(cr, uid, ids, context)[0]
        payment_journal_id = order.statement_ids and order.statement_ids[0].statement_id.journal_id.id or False
        date_invoice = order.date_order
        self.pool['account.invoice'].write(cr, uid, res['res_id'], {'payment_journal_id': payment_journal_id, 'date_invoice': date_invoice})
        return res

    def cancel_pos_order(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for pos_order in self.browse(cr, uid, ids, context):
            if pos_order.picking_id and pos_order.picking_id.type == 'out':
                pos_order.picking_id.action_reopen()
                pos_order.picking_id.unlink()
            self.pool['account.bank.statement.line'].unlink(cr, SUPERUSER_ID,
                                                            [statement.id for statement in pos_order.statement_ids],
                                                            context)
            pos_order.write({'state': 'draft'})
        return True

    def location_pos_order(self, cr, uid, ids, context=None):
        inventory_obj = self.pool['stock.inventory']
        product_obj = self.pool['product.product']
        inventory_line_obj = self.pool['stock.inventory.line']
        for pos_order in self.browse(cr, uid, ids, context):
            context['warehouse'] = pos_order.shop_id.warehouse_id.id
            inventory_ids = inventory_obj.search(cr, uid, [('name', '=', pos_order.shop_id.name), ('state', '=', 'draft')], context=context)
            if inventory_ids:
                inventory_id = inventory_ids[0]
            else:
                inventory_id = inventory_obj.create(cr, uid, {'name': pos_order.shop_id.name, 'date': pos_order.date_order, 'user_id': uid}, context)

            grouped_lines = {}

            for line in pos_order.lines:
                if line.product_id.type != 'service':
                    if not grouped_lines.get(line.product_id, False):
                        grouped_lines[line.product_id] = line.qty
                    else:
                        grouped_lines[line.product_id] += line.qty

            location_id = pos_order.stock_location_id.id
            for product_line in grouped_lines:
                product_id = product_line.id

                inventory_line_ids = inventory_line_obj.search(cr, uid, [('inventory_id', '=', inventory_id), ('location_id', '=', location_id), ('product_id', '=', product_id)], context=context)
                product = product_obj.browse(cr, uid, product_id, context)

                if inventory_line_ids:
                    product_qty = inventory_line_obj.read(cr, uid, inventory_line_ids[0], ['product_qty'], context)['product_qty']
                    inventory_line_value = {
                        'product_qty': product_qty + grouped_lines[product_line],
                        'product_qty_calc': product.qty_available,
                    }
                    inventory_line_obj.write(cr, uid, inventory_line_ids[0], inventory_line_value, context)
                else:
                    product_uom = product_line.uom_id.id
                    context.update({
                        'location': location_id,
                        'uom': product_uom,
                        'to_date': pos_order.date_order
                    })
                    inventory_line_value = inventory_line_obj.on_change_product_id(cr, uid, [], location_id, product_id,
                                                                                   product_uom, pos_order.date_order).get('value')
                    inventory_line_value.update({
                        'inventory_id': inventory_id,
                        'location_id': location_id,
                        'product_id': product_id,
                        'product_qty': grouped_lines[product_line],
                        'product_uom': product_uom,
                        'product_qty_calc': product.qty_available,
                    })
                    inventory_line_obj.create(cr, uid, inventory_line_value, context)

            # inventory_obj.action_confirm(cr, uid, [inventory_id], context=context)
            # inventory_obj.action_done(cr, uid, [inventory_id], context=context)
            if pos_order.picking_id:
                pos_order.picking_id.action_reopen()
                pos_order.picking_id.unlink()
            self.pool['account.bank.statement.line'].unlink(cr, SUPERUSER_ID,
                                                            [statement.id for statement in pos_order.statement_ids],
                                                            context)
            pos_order.write({'state': 'cancel', 'active': False})
            self.pool['pos.order.line'].write(cr, SUPERUSER_ID, [line.id for line in pos_order.lines], {'active': False}, context)
        return True

    def transfert_pos_order(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        stock_move_obj = self.pool['stock.move']
        for pos_order in self.browse(cr, uid, ids, context):
            if pos_order.shop_transfert_id and pos_order.picking_id:
                if pos_order.shop_transfert_id.warehouse_id.lot_stock_id:
                    stock_move_ids = stock_move_obj.search(cr, uid, [('picking_id', '=', pos_order.picking_id.id)], context=context)
                    stock_move_obj.write(cr, uid, stock_move_ids, {'location_dest_id': pos_order.shop_transfert_id.warehouse_id.lot_stock_id.id}, context)
                    # qui andrebbe fatto il DDT
                    if self.pool.get('wizard.assign.ddt'):
                        picking = pos_order.picking_id
                        if picking.ddt_number:
                            continue
                        picking_obj = self.pool['stock.picking']
                        if pos_order.shop_id.ddt_sequence:
                            ddt_number = self.pool['ir.sequence'].next_by_id(cr, uid, pos_order.shop_id.ddt_sequence.id)
                        else:
                            ddt_number = self.pool['ir.sequence'].get(cr, uid, 'stock.ddt')

                        text = _(u'{picking} using sequence for DDT to {ddt_number}').format(picking=picking.name,
                                                                                             ddt_number=ddt_number)
                        picking_obj.log(cr, uid, picking.id, text)
                        picking_obj.message_append(cr, uid, [picking.id], text, body_text=text, context=context)
                        vals_picking = picking_obj.default_get(cr, uid, ['goods_description_id', 'trasportation_condition_id', 'carriage_condition_id', 'carrier_id'], context)
                        vals_picking.update({
                            'address_id': pos_order.shop_transfert_id.warehouse_id.partner_address_id and pos_order.shop_transfert_id.warehouse_id.partner_address_id.id or False,
                            'address_delivery_id': pos_order.shop_transfert_id.warehouse_id.partner_address_id and pos_order.shop_transfert_id.warehouse_id.partner_address_id.id or False,
                            'ddt_number': ddt_number,
                            'ddt_date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                            'stock_journal_id': pos_order.shop_id.transfert_journal_id and pos_order.shop_id.transfert_journal_id.id
                        })
                        picking.write(vals_picking)

                self.pool['account.bank.statement.line'].unlink(cr, SUPERUSER_ID, [statement.id for statement in pos_order.statement_ids], context)

                pos_order.write({'active': False})
                # self.pool['pos.order.line'].write(cr, SUPERUSER_ID, [line.id for line in pos_order.lines], {'active': False}, context)
                email_template_obj = self.pool['email.template']
                model_data_obj = self.pool['ir.model.data']
                model_data, res_id = model_data_obj.get_object_reference(cr, uid, 'point_of_sale_extended', 'send_picking_out')
                try:
                    email_template_obj.send_mail(cr, uid, res_id, pos_order.id, force_send=True, context=context)
                    _logger.info(u'Sent Email for internal transfert for {name} #{order_id}, email notification sent.'.format(name=self._name, order_id=pos_order.id))
                except Exception as e:
                    _logger.error(e)
        return True

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if self.pool['res.groups'].user_in_group(cr, uid, uid, 'point_of_sale_extended.group_pos_order_cancel', context):
            self.cancel_pos_order(cr, uid, ids, context)
        try:
            res = super(PosOrder, self).unlink(cr, uid, ids, context)
        except Exception as e:
            raise orm.except_orm(_('Note {error}'.format(error=e[0])),
                                _('Is impossible to Delete because user {user} is not allow do to do that. \n {error}'.format(user=self.pool['res.users'].browse(cr, uid, uid, context).name, error=e[1])))
        return res

    def test_paid(self, cr, uid, ids, context=None):
        """A Point of Sale is paid when the sum
        @return: True
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        for order in self.pool['pos.order'].browse(cr, uid, ids, context=context):
            if order.shop_transfert_id:  # transfert
                self.transfert_pos_order(cr, uid, [order.id], context)
                return True
            elif order.stock_location_id and order.state == 'draft':
                self.location_pos_order(cr, uid, [order.id], context)  # inventory
                return True
        return super(PosOrder, self).test_paid(cr, uid, ids, context)

    def _get_barcode(self, cr, uid, ids, prop, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if not obj.hashcode:
                result[obj.id] = False
                continue
            result[obj.id] = bar_code_image(obj.hashcode)
        return result

    def _get_date_order_tz(self, cr, uid, ids, field_names=None, arg=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}
        dt_format = tools.DEFAULT_SERVER_DATETIME_FORMAT
        tz = context.get('tz', 'UTC')
        for pos_order in self.browse(cr, uid, ids, context=context):
            tz = pos_order.shop_id.pos_user_id.context_tz or tz
            res[pos_order.id] = pos_order.date_order and tools.server_to_local_timestamp(pos_order.date_order, dt_format, dt_format, tz) or False
        return res

    def _customer_complete_code(self, cr, uid, ids, prop, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if not obj.hashcode:
                result[obj.id] = False
                continue
            result[obj.id] = bar_code_image(obj.hashcode)
        return result

    _columns = {
        'product_barcode': fields.char('Barcode', readonly=True, states={'draft': [('readonly', False)]}),
        'history_id': fields.many2one('pos.history', 'History'),
        'shop_transfert_id': fields.many2one('sale.shop', 'Shop Transfert'),
        'stock_location_id': fields.many2one('stock.location', 'Stock Location'),
        'hashcode': fields.char('Hashcode', size=128),
        'hashcode_barcode': fields.function(_get_barcode, string='Medium Image', type="binary"),
        'date_order_tz': fields.function(_get_date_order_tz, method=True, type='char', string='Pos Date with TZ', store={
            'pos.order': (lambda self, cr, uid, ids, c={}: ids, ['date_order'], 2000),
        }),
        'customer_complete_code': fields.function(_customer_complete_code, method=True, type='char', string='Complete Customer Code', store={
            'pos.order': (lambda self, cr, uid, ids, c={}: ids, ['hashcode'], 2000),
        }),
        'customer_code': fields.char('Customer Code', size=64),
        'product_id': fields.related('lines', 'product_id', type='many2one', relation='product.product',
                                     string='Product'),
    }

    def onchange_product_barcode(self, cr, uid, ids, product_barcode, partner_id, shop_id, pricelist_id, lines, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        warning = {}
        pos_order_line_obj = self.pool['pos.order.line']
        product_obj = self.pool['product.product']
        if context.get('product_id', False):
            product_ids = [context['product_id']]
        else:
            product_ids = product_obj.search(cr, uid, [('ean13', '=', product_barcode)], context=context)
            if not product_ids:
                product_ids = product_obj.search(cr, uid, [('default_code', '=', product_barcode)], context=context)
            if not product_ids:
                product_ids = product_obj.search(cr, uid, [('name', '=', product_barcode)], context=context)

        if product_ids:
            find_line = False
            product_id = product_ids[0]
            if not product_obj.browse(cr, uid, product_id, context).sale_ok:
                title = _('Error')
                message = _('Not able to sale product with code {code}').format(code=product_barcode)
                return {'value': {
                    'lines': lines,
                    'product_barcode': False
                }, 'warning': {
                    'title': title,
                    'message': message,
                }}
            for line in lines:
                # create new line
                if line[0] == 0 or line[0] == 1:  # new or update
                    # (0, 0,  { values })    link to a new record that needs to be created with the given values dictionary
                    # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                    if 'product_id' in line[2] and line[2]['product_id'] == product_id:
                        qty = line[2]['qty'] + 1
                        product_change_value = pos_order_line_obj.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, partner_id, context)
                        warning = product_change_value.get('warning')
                        line[2].update(product_change_value.get('value'))
                        line[2].update({'product_id': product_id,
                                        'qty': qty})
                        find_line = True
                        continue
                elif line[0] == 4 and line[1]:
                    pos_order_line = pos_order_line_obj.browse(cr, uid, line[1], context)
                    if pos_order_line.product_id.id == product_id:
                        line[0] = 1  # update
                        line[2] = {
                            'qty': pos_order_line.qty + 1,
                            'product_id': product_id
                        }
                        # (1, ID, { values })    update the linked record with id = ID (write *values* on it)
                        find_line = True
                        continue
            # if not find product need to create line
            if not find_line:
                line_values = pos_order_line_obj.default_get(cr, uid, ['sequence'], context=context)
                qty = 1
                try:
                    product_change_value = pos_order_line_obj.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, partner_id, context)
                    warning = product_change_value.get('warning')
                except Exception as e:  # if not set customer
                    title = e and e[0] or ''
                    message = ''
                    if 1 in e:
                        message = e[1]
                    return {'value': {
                        'order_line': lines,
                        'product_barcode': False
                    }, 'warning': {
                        'title': title,
                        'message': message,
                    }}

                line_values.update(product_change_value.get('value'))
                line_values.update({
                    'product_id': product_id,
                    'qty': qty
                })
                lines.append([0, 0, line_values])
        else:
            title = _('Error')
            message = _('Not able to find product with code {code}').format(code=product_barcode)
            warning = {
                'title': title,
                'message': message,
            }

        return {'value': {
            'lines': lines,
            'product_barcode': False
        }, 'warning': warning}

    def search(self, cr, uid, domains, offset=0, limit=0, order=None, context=None, count=False):
        for domain in domains:
            if domain[0] == 'hashcode' and isinstance(domain, list):
                domain[2] = domain[2][0:12]  # workaround because iPad send hashcode of 12, but ean13 need 13 char
            if domain[0] == 'date_order' and isinstance(domain, list):
                domain[0] = 'date_order_tz'
        pos_order_ids = super(PosOrder, self).search(cr, uid, domains, offset=offset, limit=limit, order=order, context=context, count=count)
        return pos_order_ids


class PosOrderLine(orm.Model):
    _inherit = "pos.order.line"

    def _auto_init(self, cr, context={}):
        super(PosOrderLine, self)._auto_init(cr, context)
        cr.execute("SELECT 1 FROM pg_indexes WHERE indexname='pos_order_line_order_id_index'")
        if not cr.fetchone():
            cr.execute('CREATE INDEX pos_order_line_order_id_index ON pos_order_line (order_id)')

        cr.execute("SELECT 1 FROM pg_indexes WHERE indexname='pos_order_line_active_product_id_index'")
        if not cr.fetchone():
            cr.execute('CREATE INDEX pos_order_line_active_product_id_index ON pos_order_line (active, product_id)')

        cr.execute("SELECT 1 FROM pg_indexes WHERE indexname='pos_order_line_active_order_id_index'")
        if not cr.fetchone():
            cr.execute('CREATE INDEX pos_order_line_active_order_id_index ON pos_order_line (active, order_id)')

        cr.execute("SELECT 1 FROM pg_indexes WHERE indexname='pos_order_line_active_index'")
        if not cr.fetchone():
            cr.execute('CREATE INDEX pos_order_line_active_index ON pos_order_line (active)')

    def _get_barcode(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for pos_order_line in self.browse(cr, uid, ids, context=context):
            if not pos_order_line.hashcode:
                result[pos_order_line.id] = False
                continue
            result[pos_order_line.id] = bar_code_image(pos_order_line.hashcode)
        return result

    def _get_product_barcode(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for pos_order_line in self.browse(cr, uid, ids, context=context):
            if not pos_order_line.product_id.ean13:
                result[pos_order_line.id] = False
                continue
            result[pos_order_line.id] = bar_code_image(pos_order_line.product_id.ean13)
        return result

    _columns = {
        'date_order': fields.related('order_id', 'date_order_tz', string='Date Order', type='date', size=64, store={
                'pos.order.line': (lambda self, cr, uid, ids, c={}: ids, ['order_id'], 2000),

        }),
        'hashcode': fields.char('Hashcode', size=128),
        'hashcode_barcode': fields.function(_get_barcode, string='Hashcode Barcode', type="binary"),
        'product_barcode': fields.function(_get_product_barcode, string='Product Barcode', type="binary"),
    }

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        context.update(self.pool['res.users'].context_get(cr, uid))
        sale_shop_obj = self.pool['sale.shop']
        context.update({'context_tz': context['tz']})
        res = []
        if context.get('hashcode', False):
            line_hashcode = self.search(cr, uid, [['hashcode', '=', context.get('hashcode')]], limit=1, context=context)
            if line_hashcode:
                res = line_hashcode[0]
            vals.update({'hashcode': context.get('hashcode')})
        if not res:
            shop_ids = sale_shop_obj.search(cr, uid, [('transfert_product_id', '=', vals.get('product_id'))], limit=1, context=context)
            if shop_ids:
                self.pool['pos.order'].write(cr, uid, vals.get('order_id'), {'shop_transfert_id': shop_ids[0]}, context)

            inventory_shop_ids = sale_shop_obj.search(cr, uid, [('pos_user_id', '=', uid), ('inventory_product_id', '=', vals.get('product_id'))], context=context)
            if inventory_shop_ids:
                sale_shop = sale_shop_obj.browse(cr, uid, inventory_shop_ids[0], context)
                self.pool['pos.order'].write(cr, uid, vals.get('order_id'), {'stock_location_id': sale_shop.warehouse_id.lot_stock_id.id}, context)
            try:
                res = super(PosOrderLine, self).create(cr, uid, vals, context=context)
            except Exception as e:
                _logger.info(u'POS ORDER LINE: Error {error}'.format(error=vals))
                res = 666
        return res

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not context.get('call_unlink', False):
            for line in self.browse(cr, uid, ids, context):
                if line.order_id.state != 'draft':
                    raise orm.except_orm(
                        'Errore',
                        'Connected Order not in Draft')
        return super(PosOrderLine, self).unlink(cr, uid, ids, context)
