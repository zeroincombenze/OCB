# -*- coding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

import json
import logging
import threading

import pooler
from openerp.osv import orm, fields
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
try:
    import telepot
except ImportError:
    _logger.debug('Cannot `import telepot`')


def json_dump(v):
    return json.dumps(v, separators=(',', ':'))


class TelegramThread(orm.Model):

    _name = 'telegram.thread'

    THREAD = True
    THREAD_START = False

    _columns = {
        'create_date': fields.datetime('Create date'),
        'channel': fields.text('Channel'),
        'message': fields.text('Message'),
        'message_id': fields.integer('Message ID'),
        'update_id': fields.integer('Update ID'),
        'user_id': fields.many2one('res.users', 'Users')
    }

    _order = "update_id desc, message_id desc"

    def __init__(self, registry, cr):
        # Inizializzazione superclasse
        super(TelegramThread, self).__init__(registry, cr)
        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.users_cache = {}  # cache for user

    def fetch_telegram(self, cr, uid, context=None):

        def handle(msg):
            cr2 = pooler.get_db(self.dbname).cursor()
            telegram_command_obj = self.pool['telegram.command']
            if not msg.get('message', False):  # for have same code if i use thread or cron
                msg = {'message': msg}

            telegram_thread_vals = {
                'message_id': int(msg['message']['message_id']),
                'message': json_dump(msg['message']),
                'channel': json_dump(msg['message']['from']),
            }

            if msg.get('update_id', False):
                telegram_thread_ids.update({'update_id': int(msg['update_id'])})

            telegram_user_id = msg['message']['from']['id']

            # find users
            _logger.debug(u'User cache: {0}'.format(self.users_cache))
            if not self.users_cache.get(telegram_user_id, False):
                user_telegram_ids = res_user_obj.search(cr2, uid, [('telegram_id', '=', telegram_user_id)], context=context)
                if not user_telegram_ids and msg['message']['from'].get('username', False):
                    user_telegram_ids = res_user_obj.search(cr2, uid, [
                        ('telegram_username', '=', msg['message']['from']['username'])], context=context)
                    if user_telegram_ids:
                        if len(user_telegram_ids) > 1:
                            rendered = {'html': _('Hey, there are more then one user for your ID {0}').format(telegram_user_id)}
                            telegram_command_obj.send(bot, rendered, telegram_user_id)
                        else:
                            user = res_user_obj.browse(cr2, uid, user_telegram_ids[0], context)
                            user_telegram_ids = [user.id]
                            user.write({'telegram_id': telegram_user_id})

                if user_telegram_ids:
                    self.users_cache[telegram_user_id] = user_telegram_ids[0]
                else:
                    self.users_cache[telegram_user_id] = False
                    rendered = {'html': _('Hey! There are no User defined for your ID {0}').format(telegram_user_id)}
                    telegram_command_obj.send(bot, rendered, telegram_user_id)

                    telegram_id = res_user_obj.browse(cr2, uid, 1, context).telegram_id
                    if telegram_id:
                        rendered = {
                            'html': _('Hey! There are new request from ID {0} of {1} {2}').format(
                                telegram_user_id,
                                msg['message']['from'].get('first_name'),
                                msg['message']['from'].get('last_name'),
                            )}
                        telegram_command_obj.send(bot, rendered, telegram_id)
                    cr2.commit()
                    cr2.close()
                    return False

            telegram_thread_vals.update({'user_id': self.users_cache[telegram_user_id]})

            # i know user, so can add position if exist

            if msg.get('message', False) and msg['message'].get('location', False):
                location_vals = {
                    'latitude': msg['message']['location'].get('latitude'),
                    'longitude': msg['message']['location'].get('longitude'),
                }
                res_user_obj.write(cr2, uid, self.users_cache[telegram_user_id], location_vals, context)

            if not self.search(cr2, uid, [('message_id', '=', telegram_thread_vals['message_id'])], context=context):
                self.create(cr2, uid, telegram_thread_vals, context)
                thread = TelegramDispatch(cr2, self.users_cache[telegram_user_id] or uid, [msg['message']], bot, telegram_user_id, context)
                thread.start()
            cr2.commit()
            cr2.close()
            return True

        """
        This Function is call by scheduler.
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)

        res_user_obj = self.pool['res.users']

        token = self.pool['ir.config_parameter'].get_param(cr, uid, 'telegram.token', default=None, context=context)
        if token == 'null' or not token:
            return False

        bot = telepot.Bot(token.encode('ascii'))
        # add also web command for be secure to be on webhook
        if bot.getWebhookInfo().get('url') != '':
            bot.setWebhook()

        if self.THREAD and not self.THREAD_START:
            self.THREAD_START = True
            bot.message_loop(handle)
        else:
            # get last message to download
            telegram_thread_ids = self.search(cr, uid, [], context=context, limit=1)
            if telegram_thread_ids:
                update_id = self.browse(cr, uid, telegram_thread_ids[0], context).update_id
                response = bot.getUpdates(offset=update_id + 1)
            else:
                response = bot.getUpdates()

            for msg in response:
                handle(msg)

        return True


class TelegramDispatch(threading.Thread):
    def __init__(self, cr, uid, messages, bot, chat_id, context=None):
        self.cr = pooler.get_db(cr.dbname).cursor()
        self.telegram_command_obj = pooler.get_pool(self.cr.dbname).get('telegram.command')
        self.uid = uid
        self.messages = messages
        self.context = context
        self.bot = bot
        self.chat_id = chat_id
        threading.Thread.__init__(self)

    def run(self):
        self.telegram_command_obj.telegram_listener(self.cr, self.uid, self.messages, self.bot, self.chat_id, self.context)
        self.cr.commit()
        self.cr.close()

    def send(self, text):
        self.telegram_command_obj.send(self.bot, text, self.chat_id)
        return True
