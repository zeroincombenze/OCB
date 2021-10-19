# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Didotech SRL
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

import logging
import urllib

from openerp.osv import orm, fields
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class SMSClient(orm.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    _columns = {
        'name': fields.char('Gateway Name', size=256, required=True),
        'url': fields.char('Gateway URL', size=256, required=True, help='Base url for message'),
        'property_ids': fields.one2many('sms.smsclient.parms', 'gateway_id', 'Parameters'),
        'history_line': fields.one2many('sms.smsclient.history', 'gateway_id', 'History'),
        'method': fields.selection([
            ('http', 'HTTP Method'),
            ('smpp', 'SMPP Method')
        ], 'API Method', select=True),
        'state': fields.selection([
            ('new', 'Not Verified'),
            ('waiting', 'Waiting for Verification'),
            ('confirm', 'Verified'),
        ], 'Gateway Status', select=True, readonly=True),
        'users_id': fields.many2many('res.users', 'res_smsserver_group_rel', 'sid', 'uid', 'Users Allowed'),
        'code': fields.char('Verification Code', size=256),
        'body': fields.text('Message', help="The message text that will be send along with the email which is send through this server"),
    }

    _defaults = {
        'state': lambda *a: 'new',
        'method': lambda *a: 'http',
    }

    def check_permissions(self, cr, uid, id):
        cr.execute('select * from res_smsserver_group_rel where sid=%s and uid=%s' % (id, uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    @staticmethod
    def clean(text):
        # pulitura momentanea del testo
        text = text.replace(u"è ", "e'")
        text = text.replace(u"ò ", "o'")
        text = text.replace(u"à ", "a'")
        text = text.replace(u"ì ", "i'")
        text = text.replace(u"é ", "e'")
        text = text.replace(u"ù ", "u'")
        text = text.replace(u"è", "e")
        text = text.replace(u"ò", "o")
        text = text.replace(u"à", "a")
        text = text.replace(u"ì", "i")
        text = text.replace(u"é", "e")
        text = text.replace(u"ù", "u")
        return text

    def send_message(self, cr, uid, gateway, to, text, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        gate = self.browse(cr, uid, gateway, context=context)
        if not self.check_permissions(cr, uid, gateway):
            raise orm.except_orm(_('Permission Error!'), _('You have no permission to access %s ') % (gate.name,))

        if gate.method != 'http':
            raise orm.except_orm(_('Error'), _('This method is not implemented (%s)') % (gate.name,))

        url = gate.url

        text = self.clean(text)
        # This is the same but result is unicode
        # text = text.decode('utf-8')
        text = text.replace(u'€', 'E')
        text = text.encode('ascii')

        to = to.replace(" ", "")
        to = to.replace("/", "")
        to = to.replace("-", "")

        prms = {}
        for p in gate.property_ids:
            if p.type == 'to':
                prms[p.name] = to
            elif p.type == 'sms':
                prms[p.name] = text
            else:
                prms[p.name] = p.value

        params = urllib.urlencode(prms)
        req = url + "?" + params
        _logger.info(u'create sms req : {sms}'.format(sms=req))

        self.pool['sms.smsclient.queue'].create(cr, uid, {
            'name': req,
            'gateway_id': gateway,
            'state': 'draft',
            'mobile': to,
            'msg': text
        }, context)
        return True

    def _check_queue(self, cr, uid, ids=False, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        queue_obj = self.pool['sms.smsclient.queue']
        history_obj = self.pool['sms.smsclient.history']

        sids = queue_obj.search(cr, uid, [('state', 'not in', ('send', 'sending', 'error'))], limit=30, context=context)
        queue_obj.write(cr, uid, sids, {'state': 'sending'}, context)
        error_ids = []
        sent_ids = []
        for sms in queue_obj.browse(cr, uid, sids, context=context):
            _logger.info(u'Sending {sms}'.format(sms=sms.name))
            f = urllib.urlopen(sms.name)
            if len(sms.msg) > 160:
                error_ids.append(sms.id)
                continue

            history_obj.create(cr, uid, {
                'name': _('SMS Sent'),
                'gateway_id': sms.gateway_id.id,
                'sms': sms.msg,
                'to': sms.mobile
            }, context=context)
            sent_ids.append(sms.id)

        if sent_ids:
            queue_obj.write(cr, uid, sent_ids, {'state': 'send'}, context)
        if error_ids:
            queue_obj.write(cr, uid, error_ids, {'state': 'error', 'error': 'Size of SMS should not be more then 160 char'}, context)
        return True
