# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#    Copyright (C) 2014 Didotech SRL
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

import time
from openerp.report import report_sxw
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'raggruppa': self._raggruppa,
            'div': self._div,
            'mul': self._mul,
            'italian_number': self._get_italian_number,
            'sum_item': self._sum_item,
            'product': self._product,
        })

    def _product(self, id):
        return self.pool['product.product'].browse(self.cr, self.uid, id)
        
    def _div(self, up, down):
        res = 0
        if down:
            res = up / down
        return res

    def _mul(self, up, down):
        res = 0
        if down:
            res = up * down
        return res

    def _get_italian_number(self, number, precision=2, no_zero=False):
        if not number and no_zero:
            return ''
        elif not number:
            return '0,00'

        if number < 0:
            sign = '-'
        else:
            sign = ''
        # Requires Python >= 2.7:
        # before, after = "{:.{digits}f}".format(number, digits=precision).split('.')
        # Works with Python 2.6:
        if precision:
            before, after = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')
        else:
            before = "{0:10.{digits}f}".format(number, digits=precision).strip('- ').split('.')[0]
            after = ''
        belist = []
        end = len(before)
        for i in range(3, len(before) + 3, 3):
            start = len(before) - i
            if start < 0:
                start = 0
            belist.append(before[start: end])
            end = len(before) - i
        before = '.'.join(reversed(belist))
        
        if no_zero and int(number) == float(number) or precision == 0: 
            return sign + before
        else:
            return sign + before + ',' + after

    def _raggruppa(self, pos_order, ttype=None):
        pos_order_ids = []
        vals = []
        for pos in pos_order:
            pos_order_ids.append(pos.id)
            if ttype == 'categ_id':
                vals = ['categ_id', 'qty']
            else:
                ttype = 'product_id'
                vals = ['product_id', 'qty']
        res = self.pool['pos.order.line'].read_group(self.cr, self.uid, [('order_id', 'in', pos_order_ids)], ['categ_id', 'product_id', 'qty', 'pos_discount', 'price_subtotal_incl'], vals, offset=0, limit=None, context=None, orderby=ttype)
        return res

    def _sum_item(self, pos_order, ttype=None):
        qty = 0
        qty_disc = 0
        righe = self._raggruppa(pos_order, ttype)
        for riga in righe:
            qty += riga['qty']
        res = {
            'qty': qty,
            'qty_disc': qty_disc,
        }

        return res

