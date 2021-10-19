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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta, date
from sale_order import OrderLinePolicy
import netsvc

import pdb


wf_service = netsvc.LocalService("workflow")

SALE_STATE = [
    ('draft', _('Quotation')),
    ('wait_technical_validation', _('Technical Validation')),
    ('wait_manager_validation', _('Manager Validation')),
    ('send_to_customer', _('Send To Customer')),
    ('wait_customer_validation', _('Customer Validation')),
    ('waiting_date', _('Waiting Schedule')),
    ('manual', _('To Invoice')),
    ('progress', _('In Progress')),
    ('shipping_except', _('Shipping Exception')),
    ('invoice_except', _('Invoice Exception')),
    ('done', _('Done')),
    ('cancel', _('Cancelled'))
]


class asset_category(orm.Model):
    _inherit = 'asset.category'
    
    _columns = {
        'rentable': fields.boolean('Can be rented?'),
        'service_product_id': fields.many2one('product.product', _('Corrisponding Service Product'), domain="[('type', '=like', 'service')]"),
        'exclude_saturday': fields.boolean(_('Exclude Saturday'), help=_('Exclude Saturday from business week')),
        'exclude_sunday': fields.boolean(_('Exclude Sunday'), help=_('Exclude Sunday from business week')),
        'exclude_holiday': fields.boolean(_('Exclude Holidays'), help=_('Exclude Holidays from business week'))
    }
    
    def get_rentable_assets(self, cr, uid, service_product_id, context=None):
        asset_product_obj = self.pool['asset.product']
        
        category_ids = self.search(cr, uid, [('rentable', '=', True), ('service_product_id', '=', service_product_id)])
        if category_ids and len(category_ids) == 1:
            rentable_asset_ids = []
            
            asset_product_ids = asset_product_obj.search(cr, uid, [('asset_category_id', '=', category_ids[0])])
            for asset_product_id in asset_product_ids:
                rentable_asset_ids += self.pool['asset.asset'].search(cr, uid, [('asset_product_id', '=', asset_product_id)])
            
            return rentable_asset_ids
        else:
            return False
    
    def _check_service_product_unique(self, cr, uid, ids, context=None):
        for category in self.browse(cr, uid, ids):
            if category.rentable:
                duplicate_category_ids = self.search(cr, uid, [('rentable', '=', True), ('service_product_id', '=', category.service_product_id.id), ('id', '!=', category.id)])
                if duplicate_category_ids:
                    return False
    
        return True
        
    _constraints = [
        (_check_service_product_unique, _('This Service Product already selected for other category'), ['service_product_id', 'rentable'])
    ]

    def get_assets_status(self, cr, uid, category_id, start_date, end_date, install_date=False, uninstall_date=False, context=None):
        """
        :param cr:
        :param uid:
        :param category_id: integer or browse record
        :param start_date: string
        :param end_date: string
        :param install_date: string
        :param uninstall_date: string
        :param context: dictionary
        :return: dictionary
        """
        rent_period_obj = self.pool['asset.rent.period']
        # order_line_obj = self.pool['sale.order.line']

        # get total number of assets in this category
        if isinstance(category_id, orm.browse_record):
            asset_category = category_id
            category_id = asset_category.id
        else:
            asset_category = self.browse(cr, uid, category_id, context)
        total_category_assets = reduce(lambda category_assets, asset_product: category_assets + len(asset_product.asset_ids), asset_category.asset_product_ids, 0)

        start_date = start_date.split()[0]
        end_date = end_date.split()[0]
        start = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT).date()
        end = datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT).date()

        if start > end:
            start, end = end, start

        busy_assets = 0
        booked_assets = 0
        booking_date = start
        while booking_date <= end:
            # domain = [
            #     ('product_id', '=', asset_category.service_product_id.id),
            #     ('date_start_rent', '<=', booking_date),
            #     ('date_end_rent', '>=', booking_date)
            # ]
            domain = [
                ('asset_category_id', '=', asset_category.id),
                ('date_start', '<=', booking_date),
                ('date_end', '>=', booking_date)
            ]
            # busy_domain = domain + [('state', '!=', 'confirmed')]
            # busy_line_ids = order_line_obj.search(cr, uid, busy_domain, context=context)
            # busy_lines = order_line_obj.browse(cr, uid, busy_line_ids, context)
            busy_domain = domain + [('confirmed', '=', False)]
            busy_line_ids = rent_period_obj.search(cr, uid, busy_domain, context=context)
            busy_lines = rent_period_obj.browse(cr, uid, busy_line_ids, context)
            busy_assets_qty = reduce(lambda x, period: x + period.product_uom_qty, busy_lines, 0)
            if busy_assets_qty > busy_assets:
                busy_assets = busy_assets_qty

            # get number of reserved (but not yet confirmed) assets
            # booked_domain = domain + [('state', '=', 'confirmed')]
            # booked_line_ids = order_line_obj.search(cr, uid, booked_domain, context=context)
            # booked_lines = order_line_obj.browse(cr, uid, booked_line_ids, context)
            booked_domain = domain + [('confirmed', '=', True)]
            booked_line_ids = rent_period_obj.search(cr, uid, booked_domain, context=context)
            booked_lines = rent_period_obj.browse(cr, uid, booked_line_ids, context)
            booked_assets_qty = reduce(lambda x, period: x + period.product_uom_qty, booked_lines, 0)
            if booked_assets_qty > booked_assets:
                booked_assets = booked_assets_qty

            booking_date += timedelta(1)

            print booking_date
            print 'Free:', total_category_assets - booked_assets
            print 'Rentable_reserved', busy_line_ids, busy_assets
            print 'Rentable_booked', booked_line_ids, booked_assets

            print '---'

        return {
            # 'total': total_category_assets,
            'rentable_free': total_category_assets - booked_assets,
            'rentable_reserved': busy_assets,
            'rentable_booked': booked_assets
        }


class AssetRentPeriod(orm.Model):
    _name = 'asset.rent.period'
    _description = 'Renting periods'
    
    def name_get(self, cr, uid, ids, context=None):
        result = {}
        
        for period in self.browse(cr, uid, ids, context):
            if period.order_line_id:
                result[period.id] = "{0} - {1} - {2}".format(period.asset_id.name_get()[0][1], period.order_id.partner_id.name, period.order_id.name)
            else:
                result[period.id] = period.asset_id.name_get()[0][1]

        return result
    
    def _get_name(self, cr, uid, ids, field_name, arg, context):
        return self.name_get(cr, uid, ids, context)
    
    def _get_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for id in ids:
            res[id] = self.browse(cr, uid, id, context).order_id.state

        return res
    
    _columns = {
        # 'asset_id': fields.many2one('asset.asset', 'Asset', required=True),
        # 'asset_category_id': fields.related('asset_id', 'asset_product_id', 'asset_category_id', type='many2one', relation='asset.category', string=_('Category'), store=False, domain="[('rentable', '=', True)]", ),
        # 'asset_ids': fields.many2many('asset.asset', 'Asset', required=False),
        'asset_category_id': fields.many2one('asset.category', string=_('Asset Category'), required=True, domain="[('rentable', '=', True)]"),
        # 'asset_quantity': fields.integer(_('Products quantity')),
        'asset_quantity': fields.related('order_line_id', 'product_uom_qty', type='integer', string=_('Quantity'), store=False),
        'confirmed': fields.boolean(_('Confirmed'), readonly=True),
        'name': fields.function(_get_name, string=_('Name'), method=True, type="char"),

        'order_line_id': fields.many2one('sale.order.line', 'Order Lines'),
        'date_start': fields.related('order_line_id', 'date_start_rent', type='date', store=False, string=_('Start'), ),
        'date_end': fields.related('order_line_id', 'date_end_rent', type='date', store=False, string=_('End'), ),
        'partner_id': fields.related('order_line_id', 'order_id', 'partner_id', type='many2one', relation='res.partner', string=_('Customer'), store=False, ),
        'partner_shipping_id': fields.related('order_line_id', 'order_id', 'partner_shipping_id', type='many2one', relation='res.partner.address', string=_('Shipping Address'), store=False, ),
        'pricelist_id': fields.related('order_line_id', 'order_id', 'pricelist_id', type='many2one', relation='product.pricelist', string=_('Pricelist'), store=False, ),
        'price_unit': fields.related('order_line_id', 'price_unit', type='float', string=_('Price'), store=False, ),
        'discount': fields.related('order_line_id', 'discount', type='float', string=_('Discount'), store=False, ),
        'order_id': fields.related('order_line_id', 'order_id', type='many2one', string=_('Sale Order'), relation='sale.order', store=False, ),
        'product_uom_qty': fields.related('order_line_id', 'product_uom_qty', type='float', string=_('Quantity'), store=False, ),

        'link_order': fields.boolean(_('Link to Other Sale Order'), ),
        # non và'state': fields.related('order_id', 'state', type='selection', string=_('State'), store=False),
        'state': fields.function(_get_state, string='State', type='selection', selection=SALE_STATE, readonly=False)
    }
    
    _defaults = {
        'confirmed': False
    }
    
    # def asset_state(self, cr, uid, asset_id, date_start, date_end, context=None):
    #     domain = [
    #         '&', '|', '&',
    #         ('date_start', '<=', date_start), ('date_end', '>=', date_start),
    #         '&',
    #         ('date_end', '>=', date_start), ('date_end', '<=', date_end),
    #         ('asset_id', '=', asset_id)
    #     ]
    #
    #     overbooking_ids = self.search(cr, uid, domain)
    #
    #     if overbooking_ids:
    #         for overbooking in self.browse(cr, uid, overbooking_ids, context):
    #             if overbooking.confirmed:
    #                 return 'confirmed'
    #         return 'reserved'
    #     return 'free'

    def asset_state(self, cr, uid, asset_id, date_start, date_end, context=None):
        move_obj = self.pool['stock.move']

        asset_location_property_obj = self.pool['asset.location.property']

        asset_stock_location = asset_location_property_obj.get_location(cr, uid, 'asset.asset')
        if asset_stock_location and asset_stock_location.stock_location:
            asset_stock_location_id = asset_stock_location.stock_location.id
        else:
            raise orm.except_orm(_('Warning'), _('Please set asset main location (Asset/Configuration/Asset Location)'))

        start = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        end = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT).date()

        date_x = start
        status = 'undefined'
        while date_x <= end:
            # print date_x
            # pdb.set_trace()
            move_ids = move_obj.search(cr, uid, [('asset_id', '=', asset_id), ('date', '<=', date_x.strftime(DEFAULT_SERVER_DATE_FORMAT))], order='date desc')
            date_x += timedelta(1)

            if move_ids:
                last_move = move_obj.browse(cr, uid, move_ids[0], context)
                if last_move.location_dest_id.id == asset_stock_location_id:
                    status = 'free'
                else:
                    return 'busy'
            else:
                status = 'free'

        return status

    def check_overbooking(self, cr, uid, rent_period_id, date_start=None, date_end=None, context=None):
        """
        :param cr:
        :param uid:
        :param rent_period_id:
        :param date_start:
        :param date_end:
        :param context:
        :return: dictionary: 'rentable_free', 'rentable_reserved', 'rentable_booked'
        """
        # state_start = 'free'
        # state_end = 'free'

        asset_rent = self.browse(cr, uid, rent_period_id, context)
        if not date_start:
            date_start = asset_rent.date_start
        if not date_end:
            date_end = asset_rent.date_end

        return self.pool['asset.category'].get_assets_status(cr, uid, asset_rent.asset_category_id, date_start, date_end, context)

        # overbooking_ids = self.search(cr, uid, [
        #     ('id', '!=', asset_rent.id),
        #     ('date_start', '<=', date_start or asset_rent.date_start),
        #     ('date_end', '>=', date_start or asset_rent.date_start),
        #     ('asset_id', '=', asset_rent.asset_id.id),
        # ])
        # if overbooking_ids:
        #     for overbooking in self.browse(cr, uid, overbooking_ids, context):
        #         if overbooking.confirmed:
        #             state_start = 'confirmed'
        #             break
        #     else:
        #         state_start = 'reserved'
        # else:
        #     state_start = 'free'
        #
        # overbooking_ids = self.search(cr, uid, [
        #     ('id', '!=', asset_rent.id),
        #     ('date_start', '<=', date_end or asset_rent.date_end),
        #     ('date_end', '>=', date_end or asset_rent.date_end),
        #     ('asset_id', '=', asset_rent.asset_id.id),
        # ])
        # if overbooking_ids:
        #     for overbooking in self.browse(cr, uid, overbooking_ids, context):
        #         if overbooking.confirmed:
        #             state_end = 'confirmed'
        #             break
        #     else:
        #         state_end = 'reserved'
        # else:
        #     state_end = 'free'
        # return {'state_start': state_start, 'state_end': state_end}

    def _check_overbooking(self, cr, uid, ids, context=None):
        for rent_period in self.browse(cr, uid, ids, context):
        # for rent_period_id in ids:
        #     period_check = self.check_overbooking(cr, uid, rent_period.id, context=context)
            period_check = self.pool['asset.category'].get_assets_status(
                cr, uid, rent_period.asset_category_id,
                start_date=rent_period.date_start,
                end_date=rent_period.date_end,
                context=context
            )
            # pdb.set_trace()
            # if period_check['state_start'] == 'confirmed' or period_check['state_end'] == 'confirmed':
            # if period_check['rentable_free'] < 0 and not rent_period.confirmed:
            if period_check['rentable_free'] < 0:
                return False
        return True
    
    def _check_start_end(self, cr, uid, ids, context=None):
        for asset_rent in self.browse(cr, uid, ids, context):
            date_start = datetime.strptime(asset_rent.date_start, DEFAULT_SERVER_DATE_FORMAT)
            date_end = datetime.strptime(asset_rent.date_end, DEFAULT_SERVER_DATE_FORMAT)
            
            if date_start > date_end:
                return False
            
        return True
        
    _constraints = [
        (_check_overbooking, _('No free assets in selected period'), ['date_start', 'date_end']),
        (_check_start_end, _("End date can't be before Start"), ['date_start', 'date_end'])
    ]
    
    def onchange_date(self, cr, uid, ids, date_start, date_end, asset_category_id, partner_shipping_id, context=None):
        if date_start and date_end and asset_category_id and partner_shipping_id:
            start = date_start.split()[0]
            end = date_end.split()[0]
            
            start = datetime.strptime(start, DEFAULT_SERVER_DATE_FORMAT).date()
            end = datetime.strptime(end, DEFAULT_SERVER_DATE_FORMAT).date()
            product_uom_qty = self.pool['sale.order.line'].biz_date_delta_inclusive(cr, uid, start, end, partner_shipping_id, asset_category_id=asset_category_id)
            
            return {'value': {'product_uom_qty': product_uom_qty}}
        else:
            return {}
    
    def onchange_asset_category(self, cr, uid, ids, date_start, date_end, asset_category_id, partner_shipping_id, context=None):
        onchange_date = self.onchange_date(cr, uid, ids, date_start, date_end, asset_category_id, partner_shipping_id, context)
        product_uom_qty = onchange_date and onchange_date['value']['product_uom_qty'] or 0
        
        if date_start and date_end and asset_category_id:
            asset_product_ids = self.pool['asset.product'].search(cr, uid, [('asset_category_id', '=', asset_category_id)])
            asset_ids = self.pool['asset.asset'].search(cr, uid, [('asset_product_id', 'in', asset_product_ids)])
            free_asset_ids = self.pool['asset.asset'].select_rentable_assets(cr, uid, asset_ids, date_start, date_end, context)
            if free_asset_ids:
                return {
                    'domain': {'asset_id': [('id', 'in', free_asset_ids)]},
                    'value': {'product_uom_qty': product_uom_qty}
                }
            else:
                raise orm.except_orm(_('Warning'), _('No Asset is free in selected period'))
        else:
            return {}
        
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        order_defaults = self.pool['sale.order'].onchange_partner_id(cr, uid, 0, partner_id)['value']
        
        return {'value': {
            'partner_shipping_id': order_defaults['partner_shipping_id'],
            'pricelist_id': order_defaults['pricelist_id']
        }}
    
    #qui verranno fuori problemi
    #def copy(self, cr, uid, id, default=None, context=None):
    #    if not default:
    #        default = {}
    #    default.update({
    #        'order_line_id': False,
    #    })
    #    return super(AssetRentPeriod, self).copy(cr, uid, values, context)
    
    def create(self, cr, uid, values, context=None):
        '''
        pp(values)
        {
            'asset_category_id': 2,
             'asset_id': 1,
             'date_end': '2014-05-20 07:00:00',
             'date_start': '2014-05-17 06:00:00',
             'partner_id': 3,
             'partner_shipping_id': 5,
             'pricelist_id': 1
        }
        '''
        
        if values.get('partner_id', False) and values.get('partner_shipping_id', False) and values.get('pricelist_id', False):
            asset = self.pool['asset.asset'].browse(cr, uid, values['asset_id'], context)
            product = asset.asset_product_id.asset_category_id.service_product_id
            partner = self.pool['res.partner'].browse(cr, uid, values['partner_id'], context)
            sale_order_obj = self.pool['sale.order']
            order_defaults = sale_order_obj.onchange_partner_id(cr, uid, 0, values['partner_id'])['value']
            company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
            
            fiscal_position = self.pool['account.fiscal.position'].browse(cr, uid, order_defaults['fiscal_position'], context)
            tax_ids = self.pool['account.fiscal.position'].map_tax(cr, uid, fiscal_position, product.taxes_id)
            
            date_start = values['date_start'].split()[0]
            date_end = values['date_end'].split()[0]
            date_start = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT).date()
            date_end = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT).date()
            
            values['order_line_id'] = self.pool['sale.order.line'].create(cr, uid, {
                'product_uos_qty': 1,
                # 'procurement_id': ,
                'product_uom': product.uom_id.id,
                'price_unit': values['price_unit'],
                'product_uom_qty': values['product_uom_qty'],
                'discount': values.get('discount', 0.0),
                'tax_id': [(6, 0, tax_ids)],
                'invoiced': False,
                # 'delay': , ???
                'name': product.name_get()[0][1],
                # salesman_id
                'product_id': product.id,
                'order_partner_id': values['partner_id'],
                'th_weight': 0,
                # 'product_packaging': ,
                'type': product.procure_method,
                # 'address_allotment_id',
                'margin': product.list_price - product.standard_price,
                'purchase_price': product.standard_price,
                'product_type': product.type,
                'date_start_rent': values['date_start'],
                'date_end_rent': values['date_end'],
            })
            
            if not company.rent_shop_id:
                raise orm.except_orm(_('Warning'), _('Please set renting shop'))
            
            policy = OrderLinePolicy(cr, uid, self.pool, date_start, date_end, values['partner_shipping_id'], product.id)
            pick_up_day = date_start - timedelta(days=1)
            pick_up_date = policy.closest_biz_day(date(pick_up_day.year, pick_up_day.month, pick_up_day.day), forward=False)
            
            if values.get('order_id', False):
                order = sale_order_obj.browse(cr, uid, values['order_id'], context)
                if order.pick_up_date:
                    order_pick_up_date = datetime.strptime(order.pick_up_date, DEFAULT_SERVER_DATE_FORMAT).date()
                    pick_up_date = pick_up_date < order_pick_up_date and pick_up_date or order_pick_up_date
                else:
                    order_pick_up_date = False
                
                sale_order_obj.write(cr, uid, values['order_id'], {
                    'pick_up_date': pick_up_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                })
                
                self.pool['sale.order.line'].write(cr, uid, values['order_line_id'], {
                    'order_id': values['order_id'],
                })
            else:
                sale_order_obj.create(cr, uid, {
                    'picking_policy': 'direct',  # ????
                    'order_policy': 'picking',
                    'shop_id': company.rent_shop_id.id,
                    'date_order': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'partner_id': values['partner_id'],
                    'fiscal_position': order_defaults['fiscal_position'],
                    'payment_term': order_defaults['payment_term'],
                    'pricelist_id': company.rent_shop_id.pricelist_id.id or values['pricelist_id'],
                    'partner_order_id': order_defaults['partner_order_id'],
                    'partner_invoice_id': order_defaults['partner_invoice_id'],
                    'user_id': order_defaults['user_id'],
                    'partner_shipping_id': values['partner_shipping_id'],
                    'shipped': False,
                    'invoice_quantity': 'order',
                    'invoice_type_id': partner.property_invoice_type and partner.property_invoice_type.id or False,
                    'version': 0,
                    'active': True,
                    'need_manager_validation': company.need_manager_validation,
                    'need_tech_validation': company.need_tech_validation,
                    'customer_validation': False,
                    'manager_validation': False,
                    'tech_validation': False,
                    'email_sent_validation': False,
                    'order_line': [(6, 0, [values['order_line_id']])],
                    'pick_up_date': pick_up_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                })
            
            context['action_validate'] = True
            #self.pool['sale.order'].action_validate(cr, uid, [order_id], context)
            #wf_service.trg_validate(uid, 'sale.order', order_id, 'action_validation', cr)
            
        return super(AssetRentPeriod, self).create(cr, uid, values, context)

    def onchange_asset_id(self, cr, uid, ids, asset_category_id, partner_id, context=None):
        asset_category = self.pool['asset.category'].browse(cr, uid, asset_category_id, context)
        partner = self.pool['res.partner'].browse(cr, uid, partner_id, context)
        product = asset_category.service_product_id
        
        list_price = self.pool['product.pricelist'].price_get(cr, uid, [partner.property_product_pricelist.id],
                                                              product.id, 1.0, partner.id, {
                                                                  'uom': product.uom_id.id,
                                                                  'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
                                                              })[partner.property_product_pricelist.id]
        
        return {'value': {'price_unit': list_price, 'discount': 0.0}}

#    def onchange_discount(self, cr, uid, ids, asset_category_id, discount, context=None):
#        asset_category = self.pool['asset.category'].browse(cr, uid, asset_category_id, context)
#        price = asset_category.service_product_id.list_price * (100 - discount) / 100
#        return {'value': {'price_unit': price}}


class asset_asset(orm.Model):
    _inherit = 'asset.asset'
    
    _columns = {
        'account_income_id' : fields.many2one('account.account', 'Income Account', help='Income Account if different from product account'),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []

        if ids:
            for asset in self.browse(cr, uid, ids, context=context):
                name = [asset.name, ]

                #if asset.name:
                #    name.append(asset.name)
                
                if asset.asset_product_id:
                    name.append(asset.asset_product_id.name)
    
                if asset.serial_number:
                    name.append('({0})'.format(asset.serial_number.name))
                
                name = ' '.join(name)
                
                if 'date_start' in context and 'date_end' in context:
                    asset_state = self.pool['asset.rent.period'].asset_state(cr, uid, asset.id, context['date_start'], context['date_end'], context)
                    if asset_state == 'reserved':
                        name = '>>> {0} <<<'.format(name)
                
                res.append((asset.id, name))

        return res
    
    def select_rentable_assets(self, cr, uid, asset_ids, period_start, period_end, context=None):
        if period_start and period_end:
            if len(period_start.split()) == 2:
                date_start = datetime.strptime(period_start, DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                date_start = datetime.strptime(period_start, DEFAULT_SERVER_DATE_FORMAT)
            
            if len(period_end.split()) == 2:
                date_end = datetime.strptime(period_end, DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                date_end = datetime.strptime(period_end, DEFAULT_SERVER_DATE_FORMAT)
            
            if date_start <= date_end:
                free_asset_ids = []
                
                # Only choose assets that are not booked for required time period.
                for asset_id in asset_ids:
                    if self.pool['asset.rent.period'].asset_state(cr, uid, asset_id, period_start, period_end, context) in ('free', 'reserved'):
                        free_asset_ids.append(asset_id)
                # pdb.set_trace()
                return free_asset_ids
            else:
                raise orm.except_orm(_('Warning'), _('Renting should begin before the end (renting period should be positive)'))
        else:
            raise orm.except_orm(_('Warning'), _('You should select a period for renting a product'))
