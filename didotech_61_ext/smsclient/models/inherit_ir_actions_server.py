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
import time

from openerp.osv import orm, fields

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class ServerAction(orm.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    _columns = {
        'sms_server': fields.many2one(
            'sms.smsclient', 'SMS Server', help='Select the SMS Gateway configuration to use with this action'
        ),
    }

    def run(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        act_ids = []
        for action in self.browse(cr, uid, ids, context=context):
            obj_pool = self.pool.get(action.model_id.model)
            obj = obj_pool.browse(cr, uid, context['active_id'], context=context)
            cxt = {
                'context': context,
                'object': obj,
                'time': time,
                'cr': cr,
                'pool': self.pool,
                'uid': uid
            }

            expr = eval(str(action.condition), cxt)
            if not expr:
                continue

            if action.state == 'sms':
                _logger.info('send SMS')
                sms_pool = self.pool['sms.smsclient']
                mobile = str(action.mobile)
                to = None
                try:
                    cxt = {
                        'context': context,
                        'object': obj,
                        'gateway': action.sms_server,
                        'time': time,
                        'cr': cr,
                        'pool': self.pool,
                        'uid': uid
                    }
                    if mobile:
                        to = eval(action.mobile, cxt)
                    else:
                        _logger.error('Mobile number not specified !')

                    text = eval(action.sms, cxt)
                    if sms_pool.send_message(cr, uid, action.sms_server.id, to, text):
                        _logger.info(u'SMS successfully send to : {to}'.format(to=to))
                    else:
                        _logger.error(u'Failed to send SMS to : {to}'.format(to=to))
                except Exception, e:
                    _logger.error('Failed to send SMS : %s' % repr(e))
            else:
                act_ids.append(action.id)

        if act_ids:
            return super(ServerAction, self).run(cr, uid, act_ids, context=context)
        return False
