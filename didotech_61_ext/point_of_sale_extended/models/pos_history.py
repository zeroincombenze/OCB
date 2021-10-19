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
import threading
from datetime import date, datetime

import decimal_precision as dp
import netsvc
import pooler
from dateutil.relativedelta import relativedelta
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class CreateHystoryProcess(threading.Thread):

    def __init__(self, cr, uid, anticipation, context=None):
        self.cr = pooler.get_db(cr.dbname).cursor()
        self.pos_order_obj = pooler.get_pool(self.cr.dbname).get('pos.order')
        self.pos_history_obj = pooler.get_pool(self.cr.dbname).get('pos.history')
        self.bank_statement_obj = pooler.get_pool(self.cr.dbname).get('account.bank.statement')
        self.cron_obj = pooler.get_pool(self.cr.dbname).get('ir.cron')

        self.uid = uid
        self.anticipation = anticipation
        self.context = context
        threading.Thread.__init__(self)

    def run(self):
        try:
            if self.context and 'anticipation' in self.context:
                cron_ids = self.cron_obj.search(self.cr, self.uid, [('function', '=', 'create_history')], context=self.context, limit=1)
                if cron_ids:
                    cron = self.cron_obj.browse(self.cr, self.uid, cron_ids[0], self.context)
                    anticipate = relativedelta(days=int(cron.args.strip("(',)")))
                else:
                    anticipate = relativedelta(days=0)
            elif self.anticipation.isdigit():
                anticipate = relativedelta(days=int(self.anticipation))
            else:
                anticipate = datetime.timedelta(days=0)
            from_date = (datetime.now() - anticipate).strftime('%Y-%m-%d 00:00:00')
            to_date = (datetime.now() - anticipate).strftime('%Y-%m-%d 23:59:59')

            pos_order_domain = self.pos_history_obj._get_domain(from_date, to_date)

            pos_order_ids = self.pos_order_obj.search(self.cr, self.uid, pos_order_domain, context=self.context)
            if pos_order_ids:
                res = self.pos_order_obj.read_group(self.cr, self.uid, [('id', 'in', pos_order_ids)],
                                                        ['shop_id', 'company_id'], ['shop_id'], offset=0, limit=None,
                                                        context=self.context, orderby='shop_id')
                for shop in res:
                    pos_order_shop_ids = self.pos_order_obj.search(self.cr, self.uid, [('id', 'in', pos_order_ids),
                                                                  ('shop_id', '=', shop['shop_id'][0])],
                                                        context=self.context)
                    if pos_order_shop_ids:
                        history_ids = self.pos_history_obj.search(self.cr, self.uid, [
                            ('date', '=', (datetime.now() - anticipate).strftime(DEFAULT_SERVER_DATE_FORMAT)),
                            ('shop_id', '=', shop['shop_id'][0])], context=self.context)
                        if history_ids:
                            self.pos_order_obj.write(self.cr, self.uid, pos_order_shop_ids, {'history_id': history_ids[0]}, context=self.context)
                        else:
                            history_vals = {
                                'date': (datetime.now() - anticipate).strftime(DEFAULT_SERVER_DATE_FORMAT),
                                'pos_order_ids': [(6, 0, pos_order_shop_ids)],
                                'company_id': 1,
                                'shop_id': shop['shop_id'][0]
                            }
                            self.pos_history_obj.create(self.cr, self.uid, history_vals, context=self.context)
                        self.cr.commit()
            # now also update all the old pos
            pos_order_domain = self.pos_history_obj._get_domain_old(from_date, to_date)
            pos_order_old_ids = self.pos_order_obj.search(self.cr, self.uid, pos_order_domain, context=self.context)
            for pos_order_id in pos_order_old_ids:
                pos_order = self.pos_order_obj.browse(self.cr, self.uid, pos_order_id, self.context)
                if pos_order.history_id:
                    continue

                history_ids = self.pos_history_obj.search(self.cr, self.uid, [('date', '=', pos_order.date_order_tz), ('shop_id', '=', pos_order.shop_id.id)], context=self.context)

                date_order = datetime.strptime(pos_order.date_order_tz, DEFAULT_SERVER_DATETIME_FORMAT)
                from_date = date_order.strftime('%Y-%m-%d 00:00:00')
                to_date = date_order.strftime('%Y-%m-%d 23:59:59')

                pos_order_shop_ids = self.pos_order_obj.search(self.cr, self.uid, [('date_order_tz', '>', from_date),
                                                                                ('date_order_tz', '<', to_date),
                                                                                ('shop_id', '=', pos_order.shop_id.id),
                                                                                ('state', 'not in', ['draft']),
                                                                                ('history_id', '=', False)],
                                                         context=self.context)

                if history_ids:
                    self.pos_order_obj.write(self.cr, self.uid, pos_order_shop_ids, {'history_id': history_ids[0]}, self.context)
                else:
                    # create history other
                    user_ids = [user_id.id for user_id in pos_order.shop_id.member_ids]
                    user_ids.append(pos_order.shop_id.pos_user_id.id)

                    bank_statement_ids = self.bank_statement_obj.search(self.cr, self.uid,
                                                                        [('journal_id.journal_user', '=', True),
                                                                         ('history_id', '=', False),
                                                                         ('date', '=', pos_order.date_order_tz), (
                                                                             'user_id', 'in', user_ids)],
                                                                        context=self.context)
                    history_vals = {
                        'date': pos_order.date_order_tz,
                        'pos_order_ids': [(6, 0, pos_order_shop_ids)],
                        'company_id': 1,
                        'shop_id': pos_order.shop_id.id,
                        'statement_ids': [(6, 0, bank_statement_ids)],
                    }
                    self.pos_history_obj.create(self.cr, self.uid, history_vals, context=self.context)
                pos_order_old_ids = list(set(pos_order_old_ids) - set(pos_order_shop_ids))
                self.cr.commit()

            bank_statement_ids = self.bank_statement_obj.search(self.cr, self.uid, [('journal_id.journal_user', '=', True),
                                                                     ('history_id', '=', False)], context=self.context)

            for bank_statement in self.bank_statement_obj.browse(self.cr, self.uid, bank_statement_ids, self.context):
                history_ids = self.pos_history_obj.search(self.cr, self.uid, [('date', '=', bank_statement.date),
                                                    ('shop_id.pos_user_id', '=', bank_statement.user_id.id)],
                                          context=self.context)
                if history_ids:
                    bank_statement.write({'history_id': history_ids[0]})

            self.cr.commit()

        except Exception as e:
            # Annulla le modifiche fatte
            _logger.error(u'Error: {error}'.format(error=e))
            self.cr.rollback()
            self.cr.commit()

        return True

    def __del__(self):
        if not self.cr.closed:
            self.cr.close()
        return True

    # def terminate(self):
    #     if not self.cr.closed:
    #         self.cr.close()
    #     return super(CreateHystoryProcess, self).terminate()


class pos_history(orm.Model):
    _name = 'pos.history'
    _description = 'Point of Sale History'
    _order = "date desc"
    _rec_name = "name"

    WEEKDAYS = [
        ('1', _(u'Monday')),
        ('2', _(u'Tuesday')),
        ('3', _(u'Wednesday')),
        ('4', _(u'Thursday')),
        ('5', _(u'Friday')),
        ('6', _(u'Saturday')),
        ('7', _(u'Sunday')),
    ]

    def _get_domain(self, from_date, to_date):
        return [('date_order_tz', '>', from_date), ('date_order_tz', '<', to_date), ('state', 'not in', ['draft']),
                ('history_id', '=', False)]

    def _get_domain_old(self, from_date, to_date):
        return [('date_order_tz', '<', from_date), ('state', 'not in', ['draft']), ('history_id', '=', False)]

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for pos_history in self.read(cr, uid, ids, ['id', 'shop_id', 'date'], context=context):
            res.append((pos_history['id'], pos_history['shop_id'][1] + ' : ' + pos_history['date']))
        return res

    def _get_history(self, cr, uid, ids, context=None):
        return self.pool['pos.history'].search(cr, uid, [('pos_order_ids', 'in', ids)], context=context)

    def _get_day_of_week(self, day):
        return datetime.strptime(day, DEFAULT_SERVER_DATE_FORMAT).weekday()

    def get_color(self, cr, uid, ids, field_name, arg, context):
        value = {}
        precision_get = self.pool['decimal.precision'].precision_get(cr, uid, 'Account')
        for order in self.read(cr, uid, ids, ['date', 'cash_register_amount', 'amount_total'], context=context):
            if datetime.strptime(order['date'], DEFAULT_SERVER_DATE_FORMAT).weekday() in [6]:
                value[order['id']] = 'red'
            else:
                value[order['id']] = 'black'
            if order['cash_register_amount'] != 0 and \
                            round(order['amount_total'], precision_get) != order['cash_register_amount']:
                value[order['id']] = 'fuchsia'

        return value

    def _get_day(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = self._get_day_of_week(order.date) + 1
        return res

    def _amount_difference(self, cr, uid, ids, name, args, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = {}

        for order in self.browse(cr, uid, ids, context=context):
            if order.cash_register_amount:
                res[order.id] = order.cash_register_amount - order.amount_total
            else:
                res[order.id] = 0.0

        return res

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        # _logger.info(u'_amount_all: ids {ids}, name {name}'.format(ids=ids, name=name))
        res = {}

        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                # 'day_of_week': self._get_day_of_week(order.date),
                'amount_untax': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'number_sale': 0,
                'number_line': 0,
                'avarage_line': 0,
                'avarage_sale': 0,
                'pos_discount': False,
                'last_week_difference': 0.0,
                'pce_sell': 0
            }

            for pos_order in order.pos_order_ids:
                res[order.id]['amount_tax'] += pos_order.amount_tax
                res[order.id]['amount_total'] += pos_order.amount_total
                if pos_order.amount_total != 0.0:
                    res[order.id]['number_sale'] += 1
                    res[order.id]['number_line'] += len(pos_order.lines)
                if pos_order.pos_discount:
                    res[order.id]['pos_discount'] = True
                for line in pos_order.lines:
                    res[order.id]['pce_sell'] += line.qty

            res[order.id]['amount_untax'] = res[order.id]['amount_total'] - res[order.id]['amount_tax']

            # day = datetime.strptime(order.date, DEFAULT_SERVER_DATE_FORMAT)
            # last_day = day + relativedelta(days=-7)
            # last_history_ids = self.search(cr, uid, [('date', '=', last_day.strftime(DEFAULT_SERVER_DATE_FORMAT)), ('shop_id', '=', order.shop_id.id)], context=context)
            # if last_history_ids:
            #     import pdb; pdb.set_trace()
            #     last_amount = self.browse(cr, uid, last_history_ids[0]).amount_total
            #     res[order.id] = {
            #         'last_week_difference': last_amount
            #     }

            if res[order.id].get('number_sale', False):
                res[order.id].update({
                    'avarage_sale': res[order.id]['amount_total'] / res[order.id]['number_sale'],
                    'avarage_line': float(res[order.id]['pce_sell']) / float(res[order.id]['number_sale'])
                })

        return res

    def _set_week_number(self, cr, uid, ids, field_name, arg, context=None):
        if not len(ids):
            return []
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            if not record.date:
                res.append((record.id, 0))
                continue
            start_date = datetime.strptime(record.date, '%Y-%m-%d')
            start_date = date(start_date.year, start_date.month, start_date.day)
            week_number = start_date.isocalendar()[1]
            res.append((record.id, int(week_number)))
        return dict(res)

    _columns = {
        'state': fields.selection([('draft', 'Draft'), ('valid', 'Valid')], 'State', readonly=True,),
        'row_color': fields.function(get_color, 'Row color', type='char', readonly=True, method=True,),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date from"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Date to"),
        'company_id': fields.many2one('res.company', 'Company', required=True, readonly=True),
        'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, required=True),
        'note': fields.text('Note'),
        'date': fields.date('Date', readonly=True, select=True),
        'day_of_week': fields.function(_get_day, type='selection', string='Week Day', selection=WEEKDAYS, store={
                'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['date'], 30),
            }),
        'week_nbr': fields.function(_set_week_number, method=True, type="integer", string="Week Number", store={
                'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['date'], 30),
            }),
        'amount_untax': fields.function(_amount_all, string='Un Tax', multi='all', type='float', digits_compute=dp.get_precision('Account'), store={
            'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
            'pos.order': (_get_history, ['history_id', 'active'], 10),
        }),
        'amount_tax': fields.function(_amount_all, string='Tax', multi='all', type='float', digits_compute=dp.get_precision('Account'), store={
            'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
            'pos.order': (_get_history, ['history_id', 'active'], 10),
        }),
        'amount_total': fields.function(_amount_all, string='Total', multi='all', type='float', digits_compute=dp.get_precision('Account'), store={
            'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
            'pos.order': (_get_history, ['history_id', 'active'], 10),
        }),
        'cash_register_amount': fields.float('Cash Register Amount'),
        'amount_difference': fields.function(_amount_difference, string='Difference', type='float', digits_compute=dp.get_precision('Account'), store=False),
        'pos_order_ids': fields.one2many('pos.order', 'history_id', 'Order Lines', readonly=True),
        'statement_ids': fields.one2many('account.bank.statement', 'history_id', 'Payments', readonly=True),
        'pos_discount': fields.function(_amount_all, string='Discount', multi='all', type='boolean', store={
            'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
            'pos.order': (_get_history, ['history_id', 'active'], 10),
        }),
        'pce_sell': fields.function(_amount_all, string='PCE Sell', multi='all', type='integer', store={
            'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
            'pos.order': (_get_history, ['history_id', 'active'], 10),
        }),
        'number_sale': fields.function(_amount_all, string='Number of Sale', multi='all', type='integer', store={
            'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
            'pos.order': (_get_history, ['history_id', 'active'], 10),
        }),

        'number_line': fields.function(_amount_all, string='Number of Line', multi='all', type='integer', store={
                'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
                'pos.order': (_get_history, ['history_id'], 20),
        }),
        'avarage_sale': fields.function(_amount_all, string='Avarage Sale', multi='all', type='float', store={
                'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
                'pos.order': (_get_history, ['history_id'], 20),
        }),
        'avarage_line': fields.function(_amount_all, string='Avarage Line', multi='all', type='float', store={
                'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
                'pos.order': (_get_history, ['history_id'], 20),
        }),
        'last_week_difference': fields.function(_amount_all, string='Last week', multi='all', type='float', store={
                'pos.history': (lambda self, cr, uid, ids, c={}: ids, ['pos_order_ids'], 20),
                'pos.order': (_get_history, ['history_id'], 20),
        }),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool['res.company']._company_default_get(cr, uid, 'pos.history', context=c),
        'state': 'draft',
    }

    def create_history(self, cr, uid, anticipation, context=None):
        """
        This Function is call by scheduler.
        """
        context = context or self.pool['res.users'].context_get(cr, uid)
        # c = list()
        final_process = CreateHystoryProcess(cr, uid, anticipation, context)
        final_process.start()
        # c.append(final_process)
        # for p in reversed(c):
        #     p.join()

        return True

    def unlink(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for history in self.browse(cr, uid, ids, context):
            if history.state != 'draft':
                raise orm.except_orm(
                    _('Error'),
                    _('Is impossible to delete an History with state not draft'))
        return super(pos_history, self).unlink(cr, uid, ids, context)

    def action_confirm(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        wf_service = netsvc.LocalService("workflow")
        order_obj = self.pool['pos.order']
        statement_obj = self.pool['account.bank.statement']
        account_move_obj = self.pool['account.move']
        account_period_obj = self.pool['account.period']

        for history in self.browse(cr, uid, ids, context):
            pos_order_ids = [x.id for x in history.pos_order_ids]
            date = history.date[:10]
            period = account_period_obj.find(cr, uid, dt=date,
                                             context=dict(context or {}, company_id=history.company_id.id,
                                                          account_period_prefer_normal=True))[0]
            journal_id = order_obj._default_sale_journal(cr, history.shop_id.pos_user_id.id)
            if pos_order_ids:
                move_id = account_move_obj.create(cr, uid, {
                    'ref': u'{0} {1}'.format(history.shop_id.name,  history.date),
                    'journal_id': journal_id,
                    'date': date,
                    'period_id': period,
                }, context=context)
                self.pool['pos.order']._create_account_move_line(cr, uid, pos_order_ids, session=None, move_id=move_id, context=context)

            for order in history.pos_order_ids:
                for line in order.statement_ids:
                    if line.statement_id.state != 'confirm':
                        # here i need to validate statement
                        statement_obj.button_confirm_cash(cr, uid, [line.statement_id.id], context=context)
                wf_service.trg_validate(uid, 'pos.order', order.id, 'done', cr)

            # close or delete bank_statement
            statement_to_unlink = []
            for statement in history.statement_ids:
                if statement.state == 'open':
                    if statement.line_ids:
                        statement.button_confirm_cash()
                    else:
                        statement.button_cancel()
                        statement_to_unlink.append(statement.id)
            if statement_to_unlink:
                statement_obj.unlink(cr, 1, statement_to_unlink, context)

        self.write(cr, uid, ids, {'state': 'valid'}, context)
        return True
