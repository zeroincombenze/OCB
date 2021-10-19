# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, timedelta
from core_extended.bizdatetime import SAT, SUN, Policy
import decimal_precision as dp


class OrderLinePolicy(Policy):
    def __init__(self, cr, uid, pool, date_start, date_end, shipping_id, product_id=None, asset_category_id=None):
        """
         @param date date_start and date_end: is of form date(year, month, date)
         @param int shipping_id: used when calculating workdays in various countries
         @param int product_id or asset_category_id: used to get parameters needed for inclusion/esclusion of weekends
        """
        self.pool = pool
        
        asset_category_obj = self.pool['asset.category']
        public_holidays_obj = self.pool['public.holidays']
        weekends = []
        holidays = []
        
        holiday_start = (date_start - timedelta(days=28)).strftime(DEFAULT_SERVER_DATE_FORMAT)

        if not asset_category_id:
            asset_category_ids = asset_category_obj.search(cr, uid, [('service_product_id', '=', product_id)])
            asset_category_id = asset_category_ids and asset_category_ids[0]

        if asset_category_id:
            asset_category = asset_category_obj.browse(cr, uid, asset_category_id)
            if asset_category.rentable:
                if asset_category.exclude_saturday:
                    weekends.append(SAT)
                
                if asset_category.exclude_sunday:
                    weekends.append(SUN)
                
                if asset_category.exclude_holiday:
                    domain = [('holiday_date', '>=', holiday_start), ('holiday_date', '<=', date_end)]
                    shipping_address = self.pool['res.partner.address'].browse(cr, uid, shipping_id)
                    
                    if shipping_address.country_id:
                        country_id = shipping_address.country_id.id
                        domain.append(('country_id', '=', country_id))
                    
                    holiday_ids = public_holidays_obj.search(cr, uid, domain)
                    if holiday_ids:
                        holidays = [datetime.strptime(day.holiday_date, DEFAULT_SERVER_DATE_FORMAT).date() for day in public_holidays_obj.browse(cr, uid, holiday_ids)]

        super(OrderLinePolicy, self).__init__(weekends=weekends, holidays=holidays)


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def __init__(self, pool, cr):
        super(sale_order, self).__init__(pool, cr)
        option = ('rent_selection', 'Rent Selection')
        state_selection = self._columns['state'].selection
        if option not in state_selection:
            state_selection.append(option)
    
    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return ()

        res = []
        
        for order in self.browse(cr, uid, ids, context):
            name = []
            
            name.append(order.name)
            name.append(order.partner_id.name)
            
            name = ' '.join(name)
            res.append((order.id, name))
        
        return res
    
    _columns = {
        'pick_up_date': fields.date('Pick Up Date', help=_('Date of the pick up of goods.')),
    }
    
    def action_validate(self, cr, uid, ids, context=None):
        """
            When sending sale_order to customer control if there are rentable products.
                If there are rentable products, create stock.picking. During creation let the
                user choose products from the rental category connected to rentable product.

                The state of the asset in the selected period became "reserved" (not confirmed).

            When confirming sale_order control if there are rentable products:
                If there are rentable products, confirm reservation

                The state of the asset in the selected period became "confirmed" (booked)
        """

        if context and context.get('action_validate', False):
            return super(sale_order, self).action_validate(cr, uid, ids, context)
        elif context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        rent_period_obj = self.pool['asset.rent.period']
        asset_category_obj = self.pool['asset.category']

        for order in self.browse(cr, uid, ids, context):
            if order.state == 'draft':
                for line in order.order_line:
                    if line.rentable:
                        # create asset.rent.period
                        asset_category_ids = asset_category_obj.search(cr, uid, [('service_product_id', '=', line.product_id.id)])
                        asset_category_id = asset_category_ids and asset_category_ids[0] or False
                        if asset_category_id:
                            # The check of free assets is done by constraints on a period
                            rent_period_obj.create(cr, uid, {
                                'asset_category_id': asset_category_id,
                                'confirmed': False,
                                'order_line_id': line.id,
                            })
            elif order.state == 'wait_customer_validation':
                for line in order.order_line:
                    if line.rentable:
                        if line.sale_line_copy_id:
                            rent_period_ids = rent_period_obj.search(cr, uid, [('order_line_id', '=', line.sale_line_copy_id.id)])
                            rent_period_obj.write(cr, uid, rent_period_ids, {
                                'order_line_id': line.id,
                                'date_start': line.sale_line_copy_id.date_start_rent or None,
                                'date_end': line.sale_line_copy_id.date_end_rent or None,
                                'confirmed': True
                            })
                        else:
                            rent_period_ids = rent_period_obj.search(cr, uid, [('order_line_id', '=', line.id)])
                            rent_period_obj.write(cr, uid, rent_period_ids, {'confirmed': True})

        return super(sale_order, self).action_validate(cr, uid, ids, context)

    def action_rent_select(self, cr, uid, ids, context=None):
        # rent_period_obj = self.pool['asset.rent.period']
        asset_obj = self.pool['asset.asset']

        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                if line.rentable:
                    asset_ids = self.pool['asset.category'].get_rentable_assets(cr, uid, line.product_id.id, context)
                    free_asset_ids = asset_obj.select_rentable_assets(cr, uid, asset_ids, line.date_start_rent, line.date_end_rent, context)
                    if free_asset_ids and len(free_asset_ids) >= line.product_uom_qty:
                        rent_lines = []
                        seleted_assets = 0
                        while seleted_assets < line.product_uom_qty:
                            free_asset = asset_obj.browse(cr, uid, free_asset_ids[seleted_assets], context)

                            rent_lines.append({
                                'name': free_asset.name,
                                'complete_name': free_asset.complete_name,
                                'asset_id': free_asset.id,
                                'sale_line_id': line.id,
                                'free_asset_ids': free_asset_ids and [(6, 0, free_asset_ids)] or False
                            })
                            seleted_assets += 1
                    else:
                        raise orm.except_orm(_('Warning'), _('Insufficent free Assets in selected period'))

            if rent_lines:
                select_asset_id = self.pool['select.rent.asset'].create(cr, uid, {
                    'name': order.name,
                    'rent_line_ids': [(0, False, line) for line in rent_lines],
                    'order_id': order.id
                })

                form_res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale_rent', 'select_rent_asset')
                form_id = form_res and form_res[1] or False

                return {
                    'type': 'ir.actions.act_window',
                    'name': _("Select Asset"),
                    'res_model': 'select.rent.asset',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': False,
                    'views': [(form_id, 'form')],
                    'res_id': select_asset_id,
                    'nodestroy': True,
                    'target': 'new',
                    # 'target': 'current',
                    'domain': '[]',
                    'context': context,
                }

        return True

    def test_rent(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context):
            for line in order.order_line:
                if line.rentable:
                    return True
        return False

    #  def action_validate(self, cr, uid, ids, context=None):
    #     """
    #         When sending sale_order to customer control if there are rentable products.
    #             If there are rentable products, create stock.picking. During creation let the
    #             user choose products from the rental category connected to rentable product.
    #
    #             The state of the asset in the selected period became "reserved" (not confirmed).
    #
    #         When confirming sale_order control if there are rentable products:
    #             If there are rentable products, confirm reservation
    #
    #             The state of the asset in the selected period became "confirmed" (booked)
    #     """
    #
    #     if context and context.get('action_validate', False):
    #         return super(sale_order, self).action_validate(cr, uid, ids, context)
    #     elif context is None:
    #         context = self.pool['res.users'].context_get(cr, uid)
    #
    #     rent_period_obj = self.pool['asset.rent.period']
    #
    #     for order in self.browse(cr, uid, ids, context):
    #         if order.state == 'draft':
    #             picking_ids = self.pool['stock.picking'].search(cr, uid, [('sale_id', '=', order.id)])
    #             if not picking_ids:
    #                 rentables = []
    #                 for line in order.order_line:
    #                     if line.rentable:
    #                         rentables.append(line)
    #
    #                 if rentables:
    #                     rent_lines = []
    #                     for rentable in rentables:
    #                         rent_period_ids = self.pool['asset.rent.period'].search(cr, uid, [('order_line_id', '=', rentable.id)])
    #                         if rent_period_ids:
    #                             rent_period = self.pool['asset.rent.period'].browse(cr, uid, rent_period_ids[0], context)
    #
    #                         if rent_period and not rent_period.confirmed:
    #                             asset_ids = self.pool['asset.category'].get_rentable_assets(cr, uid, rentable.product_id.id, context)
    #                             free_asset_ids = self.pool['asset.asset'].select_rentable_assets(cr, uid, asset_ids, rentable.date_begin_rent, rentable.date_end_rent, context)
    #                             if free_asset_ids:
    #                                 rent_lines.append({
    #                                     'name': rentable.name,
    #                                     'asset_id': rentable.asset_id and rentable.asset_id.id,
    #                                     'sale_line_id': rentable.id,
    #                                     'free_asset_ids': free_asset_ids and [(6, 0, free_asset_ids)] or False
    #                                 })
    #                             else:
    #                                 raise orm.except_orm(_('Warning'), _('No Asset is free in selected period'))
    #
    #                     if rent_lines:
    #                         select_asset_id = self.pool['select.rent.asset'].create(cr, uid, {
    #                             'name': order.name,
    #                             'rent_line_ids': [(0, False, line) for line in rent_lines],
    #                             'order_id': order.id
    #                         })
    #
    #                         form_res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale_rent', 'select_rent_asset')
    #                         form_id = form_res and form_res[1] or False
    #
    #                         return {
    #                             'type': 'ir.actions.act_window',
    #                             'name': _("Select Asset"),
    #                             'res_model': 'select.rent.asset',
    #                             'view_mode': 'form',
    #                             'view_type': 'form',
    #                             'view_id': False,
    #                             'views': [(form_id, 'form')],
    #                             'res_id': select_asset_id,
    #                             'nodestroy': True,
    #                             'target': 'new',
    #                             'domain': '[]',
    #                             'context': context,
    #                         }
    #                     else:
    #                         context['action_validate'] = True
    #                         self.pool['sale.order'].action_validate(cr, uid, [order.id], context)
    #
            # elif order.state == 'wait_customer_validation':
            #     picking_lines = []
            #
            #     asset_location_property_obj = self.pool['asset.location.property']
            #
            #     source_location_property = asset_location_property_obj.get_location(cr, uid, 'asset.asset')
            #     if source_location_property and source_location_property.stock_location:
            #         source_location_id = source_location_property.stock_location.id
            #     else:
            #         raise orm.except_orm(_('Warning'), _('Please set asset main location (Asset/Configuration/Asset Location)'))
            #
            #     dest_location_property = asset_location_property_obj.get_location(cr, uid, 'res.partner')
            #     if dest_location_property and dest_location_property.stock_location:
            #         dest_location_id = dest_location_property.stock_location.id
            #     else:
            #         raise orm.except_orm(_('Warning'), _('Please set asset Partner (Customer) location (Asset/Configuration/Asset Location)'))
            #
            #     for line in order.order_line:
            #         if line.rentable:
            #             if line.sale_line_copy_id:
            #                 rent_period_ids = rent_period_obj.search(cr, uid, [('order_line_id', '=', line.sale_line_copy_id.id)])
            #                 rent_period_obj.write(cr, uid, rent_period_ids, {
            #                     'order_line_id': line.id,
            #                     'date_start': line.sale_line_copy_id.date_begin_rent or None,
            #                     'date_end': line.sale_line_copy_id.date_end_rent or None,
            #                     'confirmed': True
            #                 })
            #             else:
            #                 rent_period_ids = rent_period_obj.search(cr, uid, [('order_line_id', '=', line.id)])
            #                 rent_period_obj.write(cr, uid, rent_period_ids, {'confirmed': True})
            #
            #             for rent_period in rent_period_obj.browse(cr, uid, rent_period_ids, context):
            #                 asset_product_ids = rent_period.asset_category_id.asset_product_ids
            #                 pdb.set_trace()
            #                 picking_lines.append({
            #                     # 'name': rent_period.asset_id.asset_product_id.product_product_id.name_get()[0][1],
            #                     'name': rent_period.asset_category_id.name,
            #                     'origin': order.name,
            #                     'address_id': order.partner_shipping_id.id,
            #                     # 'product_id': rent_period.asset_id.asset_product_id.product_product_id.id,
            #                     # 'product_uom': rent_period.asset_id.asset_product_id.uom_id.id,
            #                     'asset_category_id': rent_period.asset_category_id.id,
            #                     'product_uom': asset_product_ids[0].uom_id.id,
            #                     'product_qty': line.product_uom_qty,
            #                     'date_expected': rent_period.date_start,
            #                     'date': rent_period.date_start,
            #                     # 'prodlot_id': rent_period.asset_id.serial_number.id,  # Serial number
            #                     'location_id': source_location_id,  # Source location
            #                     'location_dest_id': dest_location_id,  # Destination location (9 - customer)
            #                     'partner_id': order.partner_id.id,
            #                     'sale_line_id': line.id,
            #                         'asset_id':
            #                 })
            #                 self.pool['sale.order.line'].write(cr, uid, line.id, {'product_uom_qty_2invoice': line.product_uom_qty})
            #
            #     if picking_lines:
            #         # Create stock.picking
            #         picking_id = self.pool['stock.picking'].create(cr, uid, {
            #             'origin': order.name,
            #             'address_id': order.partner_shipping_id.id,
            #             'date': line.date_begin_rent,
            #             'min_date': line.date_begin_rent,
            #             'max_date': line.date_end_rent,
            #             'location_id': source_location_id,  # Source location
            #             'location_dest_id': dest_location_id,  # Destination location (9 - customer)
            #             'partner_id': order.partner_id.id,
            #             'move_type': 'direct',
            #             'auto_picking': False,
            #             'type': 'out',
            #             'sale_id': order.id,
            #             'number_of_packages': 0,
            #             'move_lines': [(0, False, line) for line in picking_lines],
            #             'invoice_state': 'none',
            #             'stock_journal_id': source_location_property.stock_location.chained_journal_id and source_location_property.stock_location.chained_journal_id.id or False
            #         })
            #
            #         self.pool['stock.picking'].draft_validate(cr, uid, [picking_id], context)


    
    def onchange_order_line(self, cr, uid, ids, order_lines, shipping_id, context=None):
        if order_lines:
            pick_up_date = False
            for line_values in order_lines:
                # New line (not saved yet):
                if line_values[0] == 0 and line_values[2].get('product_id', False):
                    date_start_rent = line_values[2]['date_start_rent']
                    date_end_rent = line_values[2]['date_end_rent']
                    product_id = line_values[2]['product_id']
                    product = self.pool['product.product'].browse(cr, uid, product_id, context)
                    product_type = product.type
                # Modified line
                elif line_values[0] == 1:
                    order_line = self.pool['sale.order.line'].browse(cr, uid, line_values[1], context)
                    product_id = line_values[2].get('product_id', False) or order_line.product_id and order_line.product_id.id
                    if product_id:
                        date_start_rent = line_values[2].get('date_start_rent', order_line.date_start_rent)
                        date_end_rent = line_values[2].get('date_end_rent', order_line.date_end_rent)
                        product = self.pool['product.product'].browse(cr, uid, product_id, context)
                        product_type = product.type
                    else:
                        product_type = ''
                        date_start_rent = False
                        date_end_rent = False
                # Deleted line:
                elif line_values[0] == 2:
                    product_type = ''
                    date_start_rent = False
                    date_end_rent = False
                # Line (already saved):
                elif line_values[0] == 4:
                    order_line = self.pool['sale.order.line'].browse(cr, uid, line_values[1], context)
                    if order_line.product_id:
                        date_start_rent = order_line.date_start_rent
                        date_end_rent = order_line.date_end_rent
                        product_id = order_line.product_id.id
                        product_type = order_line.product_id.type
                    else:
                        product_type = ''
                        date_start_rent = False
                        date_end_rent = False
                else:
                    product_type = ''
                    date_start_rent = False
                    date_end_rent = False
                
                if product_type == 'service' and date_start_rent and date_end_rent:
                    date_start = datetime.strptime(date_start_rent, DEFAULT_SERVER_DATE_FORMAT).date()
                    date_end = datetime.strptime(date_end_rent, DEFAULT_SERVER_DATE_FORMAT).date()
                    policy = OrderLinePolicy(cr, uid, self.pool, date_start, date_end, shipping_id, product_id)
                    pick_up_day = date_start - timedelta(days=1)
                    line_pick_up_date = policy.closest_biz_day(date(pick_up_day.year, pick_up_day.month, pick_up_day.day), forward=False)
                    
                    if not pick_up_date or line_pick_up_date < pick_up_date:
                        pick_up_date = line_pick_up_date
            
            if pick_up_date:
                return {'value': {'pick_up_date': pick_up_date.strftime(DEFAULT_SERVER_DATE_FORMAT)}}
            else:
                return {}
        else:
            return {}

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = super(sale_order, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=False, context=None)
        if line.asset_id:
            if line.asset_id.account_income_id:
                res['account_id'] = line.asset_id.account_income_id.id
        return res

    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        if line.rentable:
            subtotal = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * line.duration
        else:
            subtotal = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

        for c in self.pool.get('account.tax').compute_all(cr, uid,
                                                          line.tax_id,
                                                          subtotal,
                                                          line.product_uom_qty,
                                                          line.order_id.partner_invoice_id.id,
                                                          line.product_id,
                                                          line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"
    
    def biz_date_delta_inclusive(self, cr, uid, date_start, date_end, shipping_id, product_id=None, asset_category_id=None):
        policy = OrderLinePolicy(cr, uid, self.pool, date_start, date_end, shipping_id, product_id, asset_category_id)
        if policy.is_day_off(date_end):
            return policy.biz_day_delta(date_start, date_end)
        else:
            return policy.biz_day_delta(date_start, date_end) + 1
    
    def onchange_date(self, cr, uid, ids, date_start_rent, date_end_rent, product_id, shipping_id, context=None):
        if date_start_rent and date_end_rent:
            asset_category_obj = self.pool['asset.category']
            value = {}
            date_start = date_start_rent.split()[0]
            date_end = date_end_rent.split()[0]
            start = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT).date()
            end = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT).date()
            if end < start:
                value.update({
                    'date_start_rent': date_end_rent,
                    'date_end_rent': date_start_rent
                })

            value['duration'] = self.biz_date_delta_inclusive(cr, uid, start, end, shipping_id, product_id)

            category_ids = asset_category_obj.search(cr, uid, [('service_product_id', '=', product_id)])
            status = asset_category_obj.get_assets_status(cr, uid, category_ids[0], date_start, date_end, context=context)
            value.update(status)

            return {'value': value}
        else:
            return {}
    
    def _can_be_rented(self, cr, uid, ids, field_name, args, context):
        result = {}
        for line in self.browse(cr, uid, ids, context):
            if line.product_id and line.product_id.type == 'service':
                category_ids = self.pool['asset.category'].search(cr, uid, [('service_product_id', '=', line.product_id.id)])
                if category_ids:
                    result[line.id] = True
                else:
                    result[line.id] = False
            else:
                result[line.id] = False
        return result
    
    # def _get_asset_id(self, cr, uid, ids, field_name, args, context):
    #     result = {}
    #     rent_period_obj = self.pool['asset.rent.period']
    #     for sale_line_id in ids:
    #         rent_period_ids = rent_period_obj.search(cr, uid, [('order_line_id', '=', sale_line_id)])
    #         if rent_period_ids:
    #             rent_period = rent_period_obj.browse(cr, uid, rent_period_ids[0], context)
    #             result[sale_line_id] = rent_period.asset_id and rent_period.asset_id.id
    #         else:
    #             result[sale_line_id] = False
    #     return result

    # def get_duration(self, cr, uid, ids, field_name, args, context):
    #     duration = {}
    #     for period in self.browse(cr, uid, ids, context):
    #         if period.date_begin_rent and period.date_end_rent:
    #             start = datetime.strptime(period.date_begin_rent, DEFAULT_SERVER_DATE_FORMAT).date()
    #             end = datetime.strptime(period.date_end_rent, DEFAULT_SERVER_DATE_FORMAT).date()
    #             duration[period.id] = self.biz_date_delta_inclusive(cr, uid, start, end, period.order_id.partner_shipping_id.id, period.product_id.id)
    #         else:
    #             duration[period.id] = 0
    #
    #     return duration

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool['account.tax']
        currency_obj = self.pool['res.currency']
        # order_obj = self.pool['sale.order']
        res = {}
        if context is None:
            context = {}

        for line in self.browse(cr, uid, ids, context=context):
            if line.rentable:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * line.duration
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.order_id.partner_invoice_id.id, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id

            res[line.id] = currency_obj.round(cr, uid, cur, taxes['total'])
        return res

    def _product_margin(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = 0
            if line.product_id:
                subtotal = line.price_unit * line.product_uos_qty * (100.0 - line.discount) / 100.0
                if line.rentable:
                    subtotal *= line.duration

                if line.purchase_price:
                    res[line.id] = round(subtotal - (line.purchase_price * line.product_uos_qty), 2)
                else:
                    res[line.id] = round(subtotal - (line.product_id.standard_price * line.product_uos_qty), 2)
        return res

    def _get_rentable_status(self, cr, uid, ids, field_name=False, arg=False, context=None):
        results = {}

        asset_category_obj = self.pool['asset.category']

        for line in self.browse(cr, uid, ids, context):
            asset_category_ids = asset_category_obj.search(cr, uid, [('service_product_id', '=', line.product_id.id)])
            if asset_category_ids:
                results[line.id] = asset_category_obj.get_assets_status(
                    cr, uid, asset_category_ids[0], start_date=line.date_start_rent, end_date=line.date_end_rent, context=context)
            else:
                results[line.id] = {
                    'rentable_free': 0,
                    'rentable_reserved': 0,
                    'rentable_booked': 0
                }

        return results

    _columns = {
        'date_start_rent': fields.date('Rent start date', help=_('Date of the start of the leasing.')),
        'date_end_rent': fields.date('Rent end date', help=_('Date of the end of the leasing.')),
        'rentable': fields.function(_can_be_rented, method=True, string=_('Can be rented'), type='boolean'),
        # 'asset_id': fields.function(_get_asset_id, method=True, string=_('Asset'), type='many2one', relation='asset.asset'),
        #'product_uom_qty_2invoice': fields.float('Quantity (UoM) to invoice', digits_compute=dp.get_precision('Product UoS'), required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'duration': fields.integer(_('Duration (days)')),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Sale Price')),
        'margin': fields.function(_product_margin, string='Margin', store=True),
        'rentable_free': fields.function(_get_rentable_status, string=_('Free rentables'), multi=True, type='integer'),
        'rentable_reserved': fields.function(_get_rentable_status, string=_('Reserved rentables'), multi=True, type='integer'),
        'rentable_booked': fields.function(_get_rentable_status, string=_('Booked rentables'), multi=True, type='integer'),
        # rentable in pick up
        # rentable in installation
        'rent_period_ids': fields.one2many('asset.rent.period', 'order_line_id', _('Period'))
    }
