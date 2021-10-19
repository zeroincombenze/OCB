# -*- coding: utf-8 -*-
import datetime
import json
import logging
import random

import openerp
from openerp.osv import orm, fields
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

# longpolling timeout connection
TIMEOUT = 50


def json_dump(v):
    return json.dumps(v, separators=(',', ':'))


def hashable(key):
    if isinstance(key, list):
        key = tuple(key)
    return key


class TelegramBus(orm.Model):

    _name = 'telegram.bus'

    _columns = {
        'create_date': fields.datetime('Create date'),
        'channel': fields.char('Channel'),
        'message': fields.char('Message'),
    }

    # #@api.model
    def gc(self, cr, uid, context):
        timeout_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=TIMEOUT * 2)
        domain = [('create_date', '<', timeout_ago.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
        for bus in self.search_browse(cr, 1, domain, context):
            bus.unlink()
        return True

    # @api.model
    def sendmany(self, cr, uid, notifications, context):
        channels = set()
        for channel, message in notifications:
            channels.add(channel)
            values = {
                "channel": json_dump(channel),
                "message": json_dump(message)
            }
            self.create(cr, uid, values, context)
            if random.random() < 0.01:
                self.gc(cr, uid, context)
        if channels:
            cr.commit()

    # @api.model
    def sendone(self, cr, uid, channel, message, context):
        import pdb;pdb.set_trace()
        self.sendmany(cr, uid, [[channel, message]], context)
