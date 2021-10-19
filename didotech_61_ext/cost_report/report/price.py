# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product Detailed Structure Cost Report, Open Source    
#    Copyright (C) 2017 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#
#    Created on: 2017-12-01
#    Author : Fabio Colognesi
#    Refactoring : Andrei Levin 2017 Didotech srl
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

import os
import time
import math

import openerp
from openerp.report.interface import report_rml
from openerp.tools import to_xml
from openerp.report import report_sxw
from datetime import datetime
from openerp.tools.translate import _

PRODUCTSLIST = {}
price_digits = 2


def _moduleName():
    path = os.path.dirname(__file__)
    return os.path.basename(os.path.dirname(path))


odooModule = _moduleName()


def _thisModule():
    return os.path.splitext(os.path.basename(__file__))[0]


thisModule = _thisModule()


def _translate(value):
    return _(value)


def _float_check_precision(precision_digits=None, precision_rounding=None):
    assert (precision_digits is not None or precision_rounding is not None) and \
           not (precision_digits and precision_rounding), \
        "exactly one of precision_digits and precision_rounding must be specified"
    if precision_digits is not None:
        return 10 ** -precision_digits
    return precision_rounding


def float_round(value, precision_digits=None, precision_rounding=None, rounding_method='HALF-UP'):
    """Return ``value`` rounded to ``precision_digits`` decimal digits,
       minimizing IEEE-754 floating point representation errors, and applying
       the tie-breaking rule selected with ``rounding_method``, by default
       HALF-UP (away from zero).
       Precision must be given by ``precision_digits`` or ``precision_rounding``,
       not both!

       :param float value: the value to round
       :param int precision_digits: number of fractional digits to round to.
       :param float precision_rounding: decimal number representing the minimum
           non-zero value at the desired precision (for example, 0.01 for a 
           2-digit precision).
       :param rounding_method: the rounding method used: 'HALF-UP' or 'UP', the first
           one rounding up to the closest number with the rule that number>=0.5 is 
           rounded up to 1, and the latest one always rounding up.
       :return: rounded float
    """
    rounding_factor = _float_check_precision(precision_digits=precision_digits,
                                             precision_rounding=precision_rounding)
    if rounding_factor == 0 or value == 0: return 0.0

    # NORMALIZE - ROUND - DENORMALIZE
    # In order to easily support rounding to arbitrary 'steps' (e.g. coin values),
    # we normalize the value before rounding it as an integer, and de-normalize
    # after rounding: e.g. float_round(1.3, precision_rounding=.5) == 1.5

    # TIE-BREAKING: HALF-UP (for normal rounding)
    # We want to apply HALF-UP tie-breaking rules, i.e. 0.5 rounds away from 0.
    # Due to IEE754 float/double representation limits, the approximation of the
    # real value may be slightly below the tie limit, resulting in an error of
    # 1 unit in the last place (ulp) after rounding.
    # For example 2.675 == 2.6749999999999998.
    # To correct this, we add a very small epsilon value, scaled to the
    # the order of magnitude of the value, to tip the tie-break in the right
    # direction.
    # Credit: discussion with OpenERP community members on bug 882036

    normalized_value = value / rounding_factor  # normalize
    epsilon_magnitude = math.log(abs(normalized_value), 2)
    epsilon = 2 ** (epsilon_magnitude - 53)
    if rounding_method == 'HALF-UP':
        normalized_value += cmp(normalized_value, 0) * epsilon
        rounded_value = round(normalized_value)  # round to integer

    # TIE-BREAKING: UP (for ceiling operations)
    # When rounding the value up, we instead subtract the epsilon value
    # as the the approximation of the real value may be slightly *above* the
    # tie limit, this would result in incorrectly rounding up to the next number
    # The math.ceil operation is applied on the absolute value in order to
    # round "away from zero" and not "towards infinity", then the sign is
    # restored.

    elif rounding_method == 'UP':
        sign = cmp(normalized_value, 0)
        normalized_value -= sign * epsilon
        rounded_value = math.ceil(abs(normalized_value)) * sign  # ceil to integer

    result = rounded_value * rounding_factor  # de-normalize
    return result


###############################################################################################################à

def _createtemplate():
    """
        Automatic XML menu creation
    """
    filepath = os.path.dirname(__file__)
    fileName = thisModule + '.xml'
    fileOut = open(os.path.join(filepath, fileName), 'w')

    listout = [('report_detailed_cost_structure', 'Detailed Cost Structure', 'cost.product.structure')]

    fileOut.write(u'<?xml version="1.0"?>\n<openerp>\n    <data>\n\n')
    fileOut.write(u'<!--\n       IMPORTANT : DO NOT CHANGE THIS FILE, IT WILL BE REGENERERATED AUTOMATICALLY\n-->\n\n')

    for label, description, name in listout:
        fileOut.write(u'        <report menu="False"\n                model="product.product"\n')
        fileOut.write(u'                id="%s"\n                string="%s"\n                name="%s"\n' % (
        label, description, name))
        fileOut.write(u'                xsl="%s/report/%s.xsl" />\n' % (odooModule, thisModule))

    fileOut.write(u'<!--\n       IMPORTANT : DO NOT CHANGE THIS FILE, IT WILL BE REGENERERATED AUTOMATICALLY\n-->\n\n')
    fileOut.write(u'    </data>\n</openerp>\n')
    fileOut.close()


_createtemplate()


###############################################################################################################

class report_custom(report_rml):
    def create_xml(self, cr, uid, ids, datas, context=None):
        global PRODUCTSLIST
        PRODUCTSLIST = {}
        listflat = (datas.get('form', False) and datas['form']['listflat'])
        number = (datas.get('form', False) and datas['form']['number']) or 1
        # bomType = (datas.get('form', False) and datas['form']['bomtype']) or 'normal'
        global price_digits
        price_digits = (datas.get('form', False) and datas['form']['pricedigits']) or 2
        liststandard = (datas.get('form', False) and datas['form']['liststandard'])
        usestandard = (datas.get('form', False) and datas['form']['usestandard'])
        registry = openerp.pooler.get_pool(cr.dbname)
        product_pool = registry.get('product.product')
        # stock_move_pool = registry.get('stock.move')
        # stock_quant_pool = registry.get('stock.quant')
        product_uom_pool = registry.get('product.uom')
        workcenter_pool = registry.get('mrp.workcenter')
        user_pool = registry.get('res.users')
        bom_pool = registry.get('mrp.bom')
        pricelist_pool = registry.get('product.pricelist')
        rml_obj = report_sxw.rml_parse(cr, uid, product_pool._name, context)
        rml_obj.localcontext.update({'lang': context.get('lang', False)})
        company_currency = user_pool.browse(cr, uid, uid, context).company_id.currency_id
        company_currency_symbol = company_currency.symbol or company_currency.name

        # price_digits = rml_obj.get_digits(dp='Product Price')

        def check_manufacture_route(product):
            ret = False
            if product.supply_method.lower() == 'produce':
                ret = True
            return ret

        def check_buy_route(product):
            ret = False
            if product.supply_method.lower() == 'buy':
                ret = True
            return ret

        def get_uom_factor(product_uom):
            """
                Evaluates the conversion factor of UoM 
            """
            product_factor = product_uom.factor
            if product_uom.uom_type.lower() == 'smaller':
                product_factor = product_uom.factor_inv

            return product_factor

        def get_product_factor(product, qty=1):
            """
                Evaluates the factor of usage of a product
            """
            return qty * get_uom_factor(product.uom_id)

        def process_line(productLine, line_qtty, factor):
            bomxml = ""
            # sum_lines = 0.0
            sellers, sellers_price = "", ""
            main_sp_name, main_sp_price = "", ""
            prod = product_pool.browse(cr, uid, productLine['product_id'], context=context)
            # qty_on_hand = productLine['qty_available']
            lineprice = productLine['price']
            std_price = productLine['std_price']
            prod_name = to_xml(productLine['default_code'])
            prod_description = to_xml(_(productLine['name']))
            product_uom = product_uom_pool.browse(cr, uid, productLine['product_uom'], context=context)
            product_uom_name = to_xml(product_uom.name)
            prod_qtty = line_qtty * factor
            #             if prod_qtty-qty_on_hand<0:
            #                 purch_qty=0
            #             else:
            #                 purch_qty=prod_qtty-qty_on_hand
            sum_lines = lineprice
            purch_qty = prod_qtty
            sum_strd = prod_qtty * std_price

            if not usestandard:
                if prod.seller_id:
                    pricelist = prod.seller_id.property_product_pricelist_purchase
                    currency_symbol = pricelist.currency_id.symbol
                    # rate = (pricelist.currency_id.rate or 1.0)
                    buyprice = get_uom_factor(product_uom) * get_uom_factor(prod.product_tmpl_id.uom_id) * \
                               pricelist_pool.price_get(cr, uid, [pricelist.id],
                                                        prod.id, purch_qty or 1.0, prod.seller_id.id, {
                                                            'uom': prod.uom_po_id.id,
                                                            'date': time.strftime('%Y-%m-%d'),
                                                        })[pricelist.id]
                    if buyprice:
                        main_sp_name = """
                              <b>""" + to_xml(prod.seller_id.name) + """</b>"""
                        main_sp_price = """
                              <b>""" + rml_obj.formatLang(buyprice, digits=price_digits) + ' ' + (
                                currency_symbol) + """</b>"""
                    else:
                        main_sp_name = """
                                - """
                        main_sp_price = """
                                  <b>""" + rml_obj.formatLang(lineprice, digits=price_digits) + ' ' + (
                        company_currency_symbol) + """</b>"""

                else:
                    main_sp_price = """
                              <b>""" + rml_obj.formatLang(lineprice, digits=price_digits) + ' ' + (
                    company_currency_symbol) + """</b>"""

                for seller_id in prod.seller_ids:
                    if seller_id.name.id == prod.seller_id.id:
                        continue
                    sellers += """
                                  <i>""" + to_xml(seller_id.name.name) + """</i>"""
                    pricelist = seller_id.name.property_product_pricelist_purchase
                    currency_symbol = pricelist.currency_id.symbol
                    price = pricelist_pool.price_get(cr, uid, [pricelist.id],
                                                     prod.id, purch_qty or 1.0, seller_id.name.id, {
                                                         'uom': prod.product_tmpl_id.uom_po_id.id,
                                                         'date': time.strftime('%Y-%m-%d'),
                                                     })[pricelist.id]
                    sellers_price += """
                                  <i>""" + rml_obj.formatLang(price, digits=price_digits) + ' ' + (
                    currency_symbol) + """</i>"""

            if (liststandard) and (std_price > 0):
                sellers += """
                              <i>""" + to_xml(_("Standard Price")) + """</i>"""
                sellers_price += """
                              <i>""" + rml_obj.formatLang(std_price, digits=price_digits) + ' ' + (
                company_currency_symbol) + """</i>"""

            if lineprice:
                bomxml += """
                <row>
                    <col para='yes'>""" + prod_name + """</col>
                    <col para='yes'>""" + prod_description + """</col>
                    <col para='yes'>""" + main_sp_name + sellers + """</col>
                    <col f='yes'>""" + rml_obj.formatLang(line_qtty) + ' ' + product_uom_name + """</col>
                    <col f='yes'>""" + main_sp_price + sellers_price + """</col>
                </row>
                """
            else:
                bomxml += """
                <row>
                    <col r='yes'>""" + prod_name + """</col>
                    <col para='yes'>""" + prod_description + """</col>
                    <col para='yes'>""" + main_sp_name + sellers + """</col>
                    <col f='yes'>""" + rml_obj.formatLang(line_qtty) + ' ' + product_uom_name + """</col>
                    <col f='yes'>""" + main_sp_price + sellers_price + """</col>
                </row>
                """

            return bomxml, sum_lines, sum_strd

        def preprocess_prices(productItem):
            global PRODUCTSLIST
            global price_digits
            price = 0.0
            std_price = 0.0

            prod = product_pool.browse(cr, uid, productItem['product_id'], context)
            # qty_on_hand = productItem['qty_available']
            prod_qtty = productItem['product_qty'] or 1
            product_uom = product_uom_pool.browse(cr, uid, productItem['product_uom'], context=context)

            if productItem['bom'] and not check_buy_route(prod):
                bom_id = bom_pool._bom_find(cr, uid, prod.id, prod.uom_id.id)
                bom = bom_pool.browse(cr, uid, bom_id, context=context)
                sub_boms = bom_pool._bom_explode(cr, uid, bom, prod_qtty / bom.product_qty)

                for sub_bom in (sub_boms and sub_boms[0]):
                    stdprice, buyprice = preprocess_prices(PRODUCTSLIST[sub_bom['product_id']])
                    std_price += (stdprice * (sub_bom['product_qty'] / prod_qtty))
                    price += (buyprice * (sub_bom['product_qty'] / prod_qtty))

                if check_manufacture_route(prod):
                    for wrk in (sub_boms and sub_boms[1]):
                        _, cost = process_workcenter(wrk, prod_qtty)
                        std_price += (cost / prod_qtty)
                        price += (cost / prod_qtty)
            else:
                purch_qty = prod_qtty
                std_price = product_uom_pool._compute_price(cr, uid, prod.product_tmpl_id.uom_id.id,
                                                            prod.product_tmpl_id.standard_price,
                                                            to_uom_id=product_uom.id)

                if not usestandard:
                    if prod.seller_id and purch_qty:
                        pricelist = prod.seller_id.property_product_pricelist_purchase
                        rate = (pricelist.currency_id.rate or 1.0)
                        price = get_uom_factor(product_uom) * get_uom_factor(prod.product_tmpl_id.uom_id) * \
                                pricelist_pool.price_get(cr, uid, [pricelist.id],
                                                         prod.id, purch_qty or 1.0, prod.seller_id.id, {
                                                             'uom': prod.uom_po_id.id,
                                                             'date': time.strftime('%Y-%m-%d'),
                                                         })[pricelist.id] / rate

                if price < 0.001:
                    price = std_price
            return float_round(std_price, price_digits), float_round(price, price_digits)

        def process_workcenter(wrk, qtyReq=1):
            operation = wrk['name']
            workcenter = workcenter_pool.browse(cr, uid, wrk['workcenter_id'], context)
            cost_cycle = wrk['cycle'] * workcenter.costs_cycle
            cost_hour = wrk['hour'] * workcenter.costs_hour
            total = cost_cycle + cost_hour
            wrkxml = """
                <row>
                    <col para='yes'>""" + to_xml(workcenter.name) + """</col>
                    <col para='yes'>""" + to_xml(operation) + """</col>
                    <col f='yes'>""" + rml_obj.formatLang(workcenter.costs_cycle, digits=price_digits) + ' ' + (
            company_currency_symbol) + """</col>
                    <col f='yes'>""" + rml_obj.formatLang(workcenter.costs_hour, digits=price_digits) + ' ' + (
                     company_currency_symbol) + """</col>
                    <col f='yes'>""" + rml_obj.formatLang(cost_hour + cost_cycle, digits=price_digits) + ' ' + (
                     company_currency_symbol) + """</col>
                </row>
            """
            return wrkxml, total

        def get_factor_of_used_material(product, bom, qty):
            """
                Evaluates the factor of usage of raw material based on UoM factors
            """
            return qty * get_uom_factor(product.uom_id) * get_uom_factor(bom.product_uom)

        def preprocess_bom(product, processQty=1):
            ret = {}
            if not check_buy_route(product):
                bom_id = bom_pool._bom_find(cr, uid, product.id, product.uom_id.id)
                if bom_id:
                    bom = bom_pool.browse(cr, uid, bom_id, context=context)
                    factor = get_factor_of_used_material(product, bom, processQty)
                    # sub_boms = bom_pool._bom_explode(cr, uid, bom, product, factor / bom.product_qty, context=context)
                    sub_boms = bom_pool._bom_explode(cr, uid, bom, factor / bom.product_qty)
                    for sub_bom in (sub_boms and sub_boms[0]):
                        subproduct = product_pool.browse(cr, uid, sub_bom['product_id'], context=context)
                        ret[sub_bom['product_id']] = {
                            'std_price': 0.0,
                            'price': 0.0,
                            'wrk_price': 0.0,
                            'qty_available': 0.0,
                            'virtual_available': 0.0,
                            'product_qty': sub_bom['product_qty'],
                            'name': sub_bom['name'],
                            'description': subproduct.product_tmpl_id.description or '',
                            'product_uom': sub_bom['product_uom'],
                            'product_id': sub_bom['product_id'],
                            'bom': False,
                            'default_code': subproduct.default_code
                        }
            return ret

        def product_availabilty(cr, uid, ids, context={}):
            # domain_products = [('product_id', 'in', ids)]
            # domain_quant, domain_move_in, domain_move_out = [], [], []
            # domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_pool._get_domain_locations(cr, uid, ids, context=context)
            # domain_move_in += product_pool._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
            # domain_move_out += product_pool._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
            # domain_quant += domain_products
            #
            # domain_move_in += domain_move_in_loc
            # domain_move_out += domain_move_out_loc
            # moves_in = stock_move_pool.read_group(cr, uid, domain_move_in, ['product_id', 'product_qty'], ['product_id'], context=context)
            # moves_out = stock_move_pool.read_group(cr, uid, domain_move_out, ['product_id', 'product_qty'], ['product_id'], context=context)
            #
            # domain_quant += domain_quant_loc
            # quants = stock_quant_pool.read_group(cr, uid, domain_quant, ['product_id', 'qty'], ['product_id'], context=context)
            # quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))
            #
            # moves_in = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_in))
            # moves_out = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_out))

            res = {}
            quants = product_pool._product_available(cr, uid, ids, context=context)
            for product in product_pool.browse(cr, uid, ids, context=context):
                qty_available = float_round(quants[product.id].get('qty_available', 0.0),
                                            precision_rounding=product.uom_id.rounding)
                incoming_qty = float_round(quants[product.id].get('incoming_qty', 0.0),
                                           precision_rounding=product.uom_id.rounding)
                outgoing_qty = float_round(quants[product.id].get('outgoing_qty', 0.0),
                                           precision_rounding=product.uom_id.rounding)
                virtual_available = float_round(quants[product.id].get('virtual_available', 0.0),
                                                precision_rounding=product.uom_id.rounding)
                res[product.id] = {
                    'qty_available': qty_available,
                    'incoming_qty': incoming_qty,
                    'outgoing_qty': outgoing_qty,
                    'virtual_available': virtual_available,
                }
            return res

        def evaluation_products():
            global PRODUCTSLIST
            ids = PRODUCTSLIST.keys()

            quantities = product_availabilty(cr, uid, ids)
            for product_key, product_value in PRODUCTSLIST.items():
                product_value['qty_available'] = quantities[product_key]['qty_available']
                product_value['virtual_available'] = quantities[product_key]['virtual_available']
                product_value['std_price'], product_value['price'] = preprocess_prices(product_value)

        def preprocess_products(product_id, product_qty=1):
            global PRODUCTSLIST

            product = product_pool.browse(cr, uid, product_id, context=context)
            ret = {
                product_id: {
                    'std_price': 0.0,
                    'price': 0.0,
                    'wrk_price': 0.0,
                    'qty_available': 0.0,
                    'virtual_available': 0.0,
                    'product_qty': product_qty,
                    'description': product.product_tmpl_id.description or '',
                    'default_code': product.default_code,
                    'name': product.product_tmpl_id.name,
                    'product_uom': product.product_tmpl_id.uom_id.id,
                    'product_id': product.id,
                    'bom': False
                }
            }

            listedProducts = preprocess_bom(product, product_qty)
            if listedProducts:
                if product.id in PRODUCTSLIST:
                    PRODUCTSLIST[product.id]['bom'] = True
                ret['bom'] = True

            for product_name, product_values in listedProducts.items():
                new_product_id = set_products(product_values)
                if (new_product_id in listedProducts) and not (new_product_id == product.id):
                    preprocess_products(product_values['product_id'],
                                        product_values['product_qty'])

        def print_products(product_id):
            # Print plain list
            global PRODUCTSLIST

            linesxml = ""

            product_values = PRODUCTSLIST.values()
            product_values.sort(key=lambda obj: obj['name'])

            for product_value in product_values:
                prod_name = to_xml(product_value['name'])
                if product_value['product_id'] == product_id:
                    continue
                #  qty_on_hand=productLine['qty_available']
                lineprice = product_value['price']
                std_price = product_value['std_price']
                # wrk_price = productLine['wrk_price']
                prod_qtty = product_value['product_qty']
                prod_description = to_xml(_(product_value['name']))
                prod_default_code = product_value['default_code']
                product_uom = product_uom_pool.browse(cr, uid, product_value['product_uom'], context=context)
                product_uom_name = to_xml(product_uom.name)

                if not lineprice:
                    lineprice = std_price

                main_sp_price = """
                              <b>""" + rml_obj.formatLang(lineprice, digits=price_digits) + ' ' + (
                company_currency_symbol) + """</b>"""

                if lineprice:
                    linesxml += """
                    <row>
                        <col para='yes'>""" + prod_default_code + """</col>
                        <col para='yes'>""" + prod_description + """</col>
                        <col/>
                        <col f='yes'>""" + rml_obj.formatLang(prod_qtty) + ' ' + product_uom_name + """</col>
                        <col f='yes'>""" + main_sp_price + """</col>
                    </row>
                    """
                else:
                    linesxml += """
                    <row>
                        <col r='yes'>""" + prod_default_code + """</col>
                        <col para='yes'>""" + prod_description + """</col>
                        <col/>
                        <col f='yes'>""" + rml_obj.formatLang(prod_qtty) + ' ' + product_uom_name + """</col>
                        <col f='yes'>""" + main_sp_price + """</col>
                    </row>
                    """

            title = "<title>%s : </title>" % (_('Flat Products List'))
            flatxml = """
            <lines style='sub_total'>
            """ + title + prod_header0 + """</lines>
            """
            flatxml += """
            <lines style='header'>
            """ + prod_header + """</lines>
            """
            flatxml += """
            <lines style='lines'>""" + linesxml + """</lines>
            """
            flatxml += """
            <lines style='total'>
            """ + prod_header0 + """</lines>
            """

            return flatxml

        # def chain_products(listedProduct):
        #     global PRODUCTSLIST
        #     productName = ''
        #     if listedProduct and ('name' in listedProduct):
        #         productName = listedProduct['name']
        #         if productName in PRODUCTSLIST.keys():
        #             PRODUCTSLIST[productName]['product_qty'] += listedProduct['product_qty']
        #         else:
        #             PRODUCTSLIST[productName] = listedProduct
        #     return productName

        def set_products(product_values):
            global PRODUCTSLIST
            product_id = False
            if product_values and ('name' in product_values):
                product_id = product_values['product_id']
                if product_id in PRODUCTSLIST.keys():
                    PRODUCTSLIST[product_id]['product_qty'] += product_values['product_qty']
                else:
                    PRODUCTSLIST[product_id] = product_values
            return product_id

        def clean_products():
            global PRODUCTSLIST
            PRODUCTSLIST = {}

        def process_products(product, bom_id, qtyReq=1, level=False):
            global PRODUCTSLIST

            subxml = ""
            subtotal = 0.0
            subtotalwrk = 0.0
            subtotal_strd = 0.0

            if not check_buy_route(product):
                groupsxml = ""
                linesxml = ""
                factor = 1.0

                product_uom_name = to_xml(product.uom_id.name)
                bom = bom_pool.browse(cr, uid, bom_id, context=context)

                for bom_line in bom.bom_lines:
                    factor = qtyReq
                    sub_bom = PRODUCTSLIST[bom_line.product_id.id]
                    line_qty = bom_line.product_qty
                    bom_product_uom_name = to_xml(bom_line.product_uom.name)
                    if sub_bom['bom']:
                        if sub_bom['price']:
                            groupsxml += """
                        <lines style='lines'>
                            <row>
                                <col>""" + to_xml(sub_bom['default_code']) + """</col>
                                <col>""" + to_xml(sub_bom['name']) + """</col>
                                <col/>
                                <col t='yes'>""" + rml_obj.formatLang(line_qty) + ' ' + bom_product_uom_name + """</col>
                                <col t='yes'>""" + rml_obj.formatLang(sub_bom['price'], digits=price_digits) + ' ' + (
                            company_currency_symbol) + """</col>
                            </row>
                        </lines>
                        """
                        else:
                            groupsxml += """
                        <lines style='lines'>
                            <row>
                                <col r='yes'>""" + to_xml(sub_bom['default_code']) + """</col>
                                <col>""" + to_xml(sub_bom['name']) + """</col>
                                <col/>
                                <col t='yes'>""" + rml_obj.formatLang(line_qty) + ' ' + bom_product_uom_name + """</col>
                                <col t='yes'>""" + rml_obj.formatLang(sub_bom['price'], digits=price_digits) + ' ' + (
                            company_currency_symbol) + """</col>
                            </row>
                        </lines>
                        """
                    else:
                        linexml, priceLine, stdPriceLine = process_line(sub_bom, line_qty, factor)
                        linesxml += linexml
                    subtotal += (sub_bom['price'] * (line_qty * factor))
                    subtotal_strd += (sub_bom['std_price'] * (line_qty * factor))

                xml_prd = ''
                if check_manufacture_route(product):
                    # wrk_boms = bom_pool._bom_explode(cr, uid, bom, product, factor / bom.product_qty, context=context)
                    wrk_boms = bom_pool._bom_explode(cr, uid, bom, factor / bom.product_qty)
                    for wrk in (wrk_boms and wrk_boms[1]):
                        txt, cost = process_workcenter(wrk, factor)
                        xml_prd += txt
                        subtotalwrk += cost

                    PRODUCTSLIST[product.id]['wrk_price'] = subtotalwrk

                if level:
                    subxml += """
                    <lines style='sub_total'>
                        <row>
                            <col>""" + to_xml(product.product_tmpl_id.name) + """</col>
                            <col>""" + to_xml(_(product.product_tmpl_id.description or '')) + """</col>
                            <col/>
                            <col/>
                            <col/>
                        </row>
                    </lines>
                    """

                subxml += voidline
                subxml += """
                <lines style='header'>""" + prod_header + """</lines>
                """

                subxml += groupsxml

                if linesxml:
                    subxml += """
                    <lines style='lines'>
                    """ + linesxml + """
                    </lines>
                    """

                qty_evaluated = rml_obj.formatLang(PRODUCTSLIST[product.id]['product_qty'], 0)

                if xml_prd:
                    subxml += """
                    <lines style='sub_total'>
                        <row>
                            <col/>
                            <col> """ + _('Components Cost of %s %s') % (qty_evaluated, product_uom_name) + """: </col>
                            <col/>
                            <col/>
                            <col t='yes'>""" + rml_obj.formatLang(subtotal, digits=price_digits) + ' ' + (
                    company_currency_symbol) + """</col>
                        </row>
                    </lines>
                    """

                    subxml += voidline + workcenter_header
                    subxml += """
                    <lines style='lines'>""" + xml_prd + """</lines>
                    """
                    subxml += """
                    <lines style='sub_total'>
                        <row>
                            <col/>
                            <col> """ + _('Work Cost of %s %s') % (qty_evaluated, product_uom_name) + """: </col>
                            <col/>
                            <col/>
                            <col t='yes'>""" + rml_obj.formatLang(subtotalwrk, digits=price_digits) + ' ' + (
                    company_currency_symbol) + """</col>
                        </row>
                    </lines>
                    """

                subxml += """
                <lines style='header'>""" + prod_header0 + """</lines>
                """
                subxml += """
                <lines style='sub_total'>
                    <row>
                        <col/>
                        <col> """ + _('Total Cost of') + _(' one ') + _(product_uom_name) + """: </col>
                        <col/>
                        <col/>
                        <col t='yes'>""" + rml_obj.formatLang(PRODUCTSLIST[product.id]['price'],
                                                              digits=price_digits) + ' ' + (company_currency_symbol) + """</col>
                    </row>
                </lines>          
                """

                if level:
                    message = _("SubTotal Cost of")
                else:
                    message = _("Total Cost of")

                subxml += """
                <lines style='total'>
                    <row>
                        <col/>
                        <col> """ + _(message) + ' ' + qty_evaluated + ' ' + _(product_uom_name) + """: </col>
                        <col/>
                        <col/>
                        <col t='yes'>""" + rml_obj.formatLang(subtotal + subtotalwrk, digits=price_digits) + ' ' + (
                company_currency_symbol) + """</col>
                    </row>
                </lines>          
                """

            return subxml, subtotal_strd, subtotal, subtotalwrk

        xml = ""

        config_start = """
        <config>
            <date>""" + to_xml(rml_obj.formatLang(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), date_time=True)) + """</date>
            <company>%s</company>
            <PageSize>210.00mm,297.00mm</PageSize>
            <PageWidth>595.27</PageWidth>
            <PageHeight>841.88</PageHeight>
            <tableSize>35.00mm,60.00mm,47.00mm,29.00mm,29.00mm</tableSize>
            """ % to_xml(user_pool.browse(cr, uid, uid, context).company_id.name)
        config_stop = """
            <report-footer>Generated by Odoo</report-footer>
        </config>
        """

        workcenter_header = """
            <lines style='header'>
                <row>
                    <col>%s</col>
                    <col>%s</col>
                    <col t='yes'>%s</col>
                    <col t='yes'>%s</col>
                    <col t='yes'>%s</col>
                </row>
            </lines>
        """ % (
        _('Work Center Name'), _('Work Center Operation'), _('Cost per Cycle'), _('Cost per Hour'), _('Work Cost'))

        prod_header = """
            <row>
                <col>%s</col>
                <col>%s</col>
                <col>%s</col>
                <col t='yes'>%s</col>
                <col t='yes'>%s</col>
            </row>
        """ % (_('Components'), _('Description'), _('Components suppliers'), _('Quantity Requested'),
               _('Cost Price per Unit of Measure'))

        prod_header0 = """
            <row>
                <col/>
                <col/>
                <col/>
                <col/>
                <col/>
            </row>
        """
        voidline = """
        <lines style='sub_total'>
            <row>
                <col/>
                <col/>
                <col/>
                <col/>
                <col/>
            </row>
        </lines>
        """

        for product in product_pool.browse(cr, uid, ids, context=context):
            flatxml = ""
            groupsxml = ""
            # total_strd = 0.0
            # total = 0.0
            # totalwrk = 0.0
            clean_products()

            preprocess_products(product.id, number)
            evaluation_products()

            ret = {
                'wrk_price': 0.0,
                'std_price': 0.0,
                'price': 0.0,
                'qty_available': 0.0,
                'virtual_available': 0.0,
                'product_qty': number,
                'description': product.product_tmpl_id.description or '',
                'name': product.product_tmpl_id.name,
                'default_code': product.default_code,
                'product_uom': product.product_tmpl_id.uom_id.id,
                'product_id': product.id,
                'bom': True,
            }

            set_products(ret)
            PRODUCTSLIST[ret['product_id']]['std_price'], PRODUCTSLIST[ret['product_id']]['price'] = preprocess_prices(ret)

            product_uom_name = to_xml(product.product_tmpl_id.uom_id.name)
            bom_id = bom_pool._bom_find(cr, uid, product.id, product.uom_id.id)
            title = "<title>%s</title>" % (_("Nested Cost Structure"))
            title += "<title>%s : %s</title>" % (
            to_xml(product.product_tmpl_id.name), to_xml(product.product_tmpl_id.description or ''))
            xml += """
            <lines style='sub_total'>
            """ + title + prod_header0 + """</lines>
            """
            if not bom_id:
                # total_strd = number * product.standard_price
                # total = number * product_pool.price_get(cr, uid, [product.id], 'standard_price')[product.id]
                xml += """
                <lines style='header'>
                """ + prod_header + """</lines>
                """
                xml += """
                <lines style='lines'>
                    <row>
                        <col para='yes'>-</col>
                        <col para='yes'>-</col>
                        <col t='yes'>-</col>
                        <col t='yes'>-</col>
                        <col t='yes'>-</col>
                    </row>
                </lines>
                """
            else:
                for product_key, product_value in PRODUCTSLIST.items():
                    if not (product_value['product_id'] == product.id) and product_value['bom']:
                        subbom_id = bom_pool._bom_find(cr, uid, product_value['product_id'], product.uom_id.id)
                        subproduct = product_pool.browse(cr, uid, product_value['product_id'], context=context)
                        subxml, total_strd, total, totalwrk = process_products(subproduct, subbom_id,
                                                                               product_value['product_qty'], True)
                        groupsxml += subxml

                subxml, total_strd, total, totalwrk = process_products(product, bom_id, number)
                xml += subxml

                if listflat:
                    flatxml += print_products(product.id)

            if flatxml:
                xml += flatxml

            if groupsxml:
                xml += groupsxml

        xml = """<?xml version="1.0" ?>
        <report>
        """ + config_start + config_stop + xml + """ 
        </report>
        """

        return xml


report_custom('report.cost.product.structure', 'product.product', '', '%s/report/price.xsl' % (odooModule))
