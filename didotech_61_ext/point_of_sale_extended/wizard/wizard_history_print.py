# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
import copy
import datetime
import logging
from cStringIO import StringIO

from dateutil.relativedelta import relativedelta
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from xlwt import *

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
import collections


class Style:

    main = easyxf('font: height 160; align: horiz center')
    main_small = easyxf('font: height 120; align: horiz center; borders: left thin, right thin')
    main_with_borders = easyxf(
        'font: height 120; align: horiz center; borders: top thin, bottom thin, left thin, right thin')
    main_cell = easyxf('font: height 160; align: horiz center; borders: left thin, right thin')
    kit_main_cell = easyxf(
        'font: height 160; pattern: pattern solid, fore-colour gold; align: horiz center; borders: left thin, right thin')
    main_cell_left = main_cell = easyxf('font: height 160; align: horiz left;')
    kit_main_cell_left = easyxf(
        'font: height 160; pattern: pattern solid, fore-colour gold; align: horiz left; borders: left thin, right thin')

    euro = copy.deepcopy(main)
    euro.num_format_str = u'"$"#,##0.00'


    ##  6*0x14 = 120
    ##  8*0x14 = 160
    ## 10*0x14 = 200
    ## 12*0x14 = 240
    ## 14*0x14 = 280
    modello = easyxf('font: bold on, height 200')

    bold = easyxf('font: bold on, height 160; align: horiz center')

    bold_border = copy.deepcopy(bold)
    bold_border.num_format_str = u'0.0'
    bold_border.borders.left = 1
    bold_border.borders.right = 1
    bold_border.borders.top = 1
    bold_border.borders.bottom = 1

    red = easyxf('font: italic off, color red, height 160, height 160; align: horiz right',
                 num_format_str=u'€#,##0.00')
    green = easyxf('font: italic off, color green, height 160; align: horiz right',
                   num_format_str=u'€#,##0.00')
    blue = easyxf('font: italic off, color blue, height 160; align: horiz right',
                  num_format_str=u'€#,##0.00')
    grey = easyxf('font: italic off, color grey_ega, height 160; align: horiz right',
                  num_format_str=u'€#,##0.00')
    black = easyxf('font: italic off, color black, height 160; align: horiz right', num_format_str=u'##0.00')
    red_on_yellow = easyxf(
        'font: italic off, color red, height 160; pattern: pattern solid, fore-colour yellow; align: horiz right',
        num_format_str=u'€#,##0.00')
    green_on_yellow = easyxf(
        'font: italic off, color green, height 160; pattern: pattern solid, fore-colour yellow; align: horiz right',
        num_format_str=u'€#,##0.00')
    blue_on_yellow = easyxf(
        'font: italic off, color blue, height 160; pattern: pattern solid, fore-colour yellow; align: horiz right',
        num_format_str=u'€#,##0.00')
    black_on_grey = easyxf('font: italic off, height 160; pattern: pattern solid, fore-colour grey25',
                           num_format_str=u'€#,##0.00')
    black_on_yellow = easyxf('font: italic off, height 160; pattern: pattern solid, fore-colour yellow',
                             num_format_str=u'€#,##0.00')
    yellow_on_grey = easyxf(
        'font: italic off, color yellow, height 160; pattern: pattern solid, fore-colour grey25; align: horiz center; borders: top thin, bottom thin, left thin, right thin',
        num_format_str=u'€#,##0.00')
    blue_on_blue = easyxf(
        'font: italic off, color blue, height 160; pattern: pattern solid, fore-colour 0x29; align: horiz center; borders: top thin, bottom thin, left thin, right thin',
        num_format_str=u'€#,##0.00')

    blue_with_borders = copy.deepcopy(blue)
    blue_with_borders.num_format_str = u'0.0%'
    blue_with_borders.borders = Borders()
    blue_with_borders.borders.left = 1
    blue_with_borders.borders.right = 1
    blue_with_borders.borders.top = 1
    blue_with_borders.borders.bottom = 1

    red_with_border = copy.deepcopy(red)
    red_with_border.borders = Borders()
    red_with_border.borders.left = 1
    red_with_border.borders.right = 1

    kit_red_with_border = easyxf(
        'font: italic off, color red, height 160, height 160; align: horiz right; pattern: pattern solid, fore-colour gold; borders: left thin, right thin',
        num_format_str=u'€#,##0.00')

    kit_grey_with_border = easyxf(
        'font: italic off, color grey_ega, height 160, height 160; align: horiz right; pattern: pattern solid, fore-colour gold; borders: left thin, right thin',
        num_format_str=u'#,##0.00')

    kit_green_with_border = easyxf(
        'font: italic off, color green, height 160, height 160; align: horiz right; pattern: pattern solid, fore-colour gold; borders: left thin, right thin',
        num_format_str=u'€#,##0.00')

    grey_with_border = copy.deepcopy(grey)
    grey_with_border.num_format_str = u'0.0'
    grey_with_border.borders = Borders()
    grey_with_border.borders.left = 1
    grey_with_border.borders.right = 1

    green_with_border = copy.deepcopy(green)
    green_with_border.borders = Borders()
    green_with_border.borders.left = 1
    green_with_border.borders.right = 1


def lengthmonth(year, month):
    if month == 2 and ((year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))):
        return 29
    return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]


class PosHistoryPrint(orm.TransientModel):
    _name = "pos.history.print"

    def _get_shop(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        sale_shop_obj = self.pool['sale.shop']
        sale_shop_ids = sale_shop_obj.search(cr, uid, [('pos_user_id', '=', uid)], context=context)
        return sale_shop_ids and sale_shop_ids[0] or False

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True, domain=[('pos_user_id', '!=', False)]),
        'month': fields.selection([(x, datetime.date(2000, x, 1).strftime('%B')) for x in range(1, 13)],
                                  'Month', required=True),
        'year': fields.integer('Year', required=True),
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 32, readonly=True),
        'state': fields.selection((
            ('choose', 'choose'),  # choose
            ('get', 'get'),  # get the file
        )),
    }

    _defaults = {
        'shop_id': _get_shop,
        'month': lambda *a: (datetime.date.today() - relativedelta(months=1)).month,
        'year': lambda *a: datetime.date.today().year,
        'state': lambda *a: 'choose',
    }

    table_layout = collections.OrderedDict({
        0: {'name': 'Data.', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        1: {'name': 'Method of payment', 'width': 3500, 'header': Style.bold, 'row': Style.main_cell_left},
        2: {'name': 'Not Taxable Revenues', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        3: {'name': 'Total Taxable Revenues and Sales Tax', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        4: {'name': 'Taxable Revenues', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        5: {'name': 'Sales Tax', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        6: {'name': 'Shipment Re-charges', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        7: {'name': 'Frees', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        8: {'name': 'Total Amount Sold (Incl.Taxes)', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        9: {'name': 'Amount Received', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
        10: {'name': 'Net Shop', 'width': 3500, 'header': Style.bold, 'row': Style.euro},
    })

    def write_header(self, ws, wizard, shop_name):

        ws.write(0, 0, _(u'Totale complessivo'), Style.bold)

        ws.write(1, 0, _(u'Anno'), Style.bold)
        ws.write(1, 1, wizard.year, Style.black)

        ws.write(2, 0, _(u'Mese'), Style.bold)
        ws.write(2, 1, datetime.date(wizard.year, wizard.month, 1).strftime('%B'), Style.black)

        ws.write(3, 0, _(u'Negozio'), Style.bold)
        ws.write(3, 1, shop_name, Style.black)

        row = 4
        for column, value in self.table_layout.iteritems():
            h_style = copy.copy(value['header'])
            h_style.borders = Borders()
            h_style.borders.bottom = 1
            ws.write(row, column, value['name'], h_style)

        row += 1
        return ws, row

    def write_line(self, ws, row, values, style):
        for column, value in values.iteritems():
            ws.write(row, column, value, self.table_layout[column][style])
        return ws


    def print_report(self, cr, uid, ids, context=None):
        pos_order_obj = self.pool['pos.order']
        pos_history_obj = self.pool['pos.history']
        bank_statement_obj = self.pool['account.bank.statement']
        for wizard in self.browse(cr, uid, ids, context):
            name = wizard.shop_id.name
            file_name = 'Report_{0}_{1}.xls'.format(wizard.year, wizard.month)

            book = Workbook(encoding='utf-8')
            # ws = book.add_sheet(name, cell_overwrite_ok=True)
            ws = book.add_sheet(name)

            for index, column in self.table_layout.iteritems():
                ws.col(index).width = column['width']

            ws, row = self.write_header(ws, wizard, name)
            bom_delta = 0
            from_date = datetime.date(wizard.year, wizard.month, 1)
            to_date = (from_date + datetime.timedelta(lengthmonth(from_date.year, from_date.month)-1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
            from_date = from_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

            history_ids = pos_history_obj.search(cr, uid, [('date', '>=', from_date), ('date', '<=', to_date), ('shop_id', '=', wizard.shop_id.id)], order="date asc", context=context)

            for row, history_line in enumerate(pos_history_obj.browse(cr, uid, history_ids, context), row):
                daily_payments = {}
                for pos_order in history_line.pos_order_ids:
                    if not pos_order.statement_ids:
                        continue
                    payment = pos_order.statement_ids[0]
                    payment_type = payment.statement_id.journal_id.name
                    if payment_type not in daily_payments:
                        daily_payments.update({payment_type: {
                                'amount_total': 0.0,
                                'amount_tax': 0.0,
                                'amount_paid': 0.0,
                        }})
                    daily_payments[payment_type]['amount_total'] += pos_order.amount_total
                    daily_payments[payment_type]['amount_tax'] += pos_order.amount_tax
                    daily_payments[payment_type]['amount_paid'] += pos_order.amount_paid

                for s_row, payment_type in enumerate(daily_payments.keys(), row + bom_delta):
                    amount_total = daily_payments[payment_type]['amount_total']
                    amount_tax = daily_payments[payment_type]['amount_tax']
                    amount_paid = daily_payments[payment_type]['amount_paid']
                    # for line in payment.line_ids:
                    #     pos_order = line.pos_statement_id
                    #     amount_total += pos_order.amount_total
                    #     amount_tax += pos_order.amount_tax
                    #     amount_paid += pos_order.amount_paid

                    xls_line = {
                        0: history_line.date,
                        1: payment_type,
                        2: '',
                        3: amount_total,
                        4: amount_total,
                        5: amount_tax,
                        6: '',
                        7: '',
                        8: amount_total,
                        9: amount_paid,
                        10: amount_total-amount_tax,
                    }
                    self.write_line(ws, s_row, xls_line, 'row')
                    bom_delta = s_row - row

            """PARSING DATA AS STRING """
            file_data = StringIO()
            book.save(file_data)
            """STRING ENCODE OF DATA IN WKSHEET"""
            out = file_data.getvalue()
            out = out.encode("base64")
            return self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': file_name}, context=context)




