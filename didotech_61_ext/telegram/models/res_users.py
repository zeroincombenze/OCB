# -*- encoding: utf-8 -*-

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID


class res_users(orm.Model):
    _inherit = 'res.users'

    _columns = {
        'telegram_id': fields.integer('Telegram ID'),
        'telegram_username': fields.char('Telegram Username'),
        'latitude': fields.float('Latitude', digits=(16, 4)),
        'longitude': fields.float('Longitude', digits=(16, 4)),
    }

    _sql_constraints = [
        ('telegram_id_name_uniq', 'unique (telegram_id)', 'Telegram ID must be unique!'),
        ('telegram_username_name_uniq', 'unique (telegram_username)', 'Telegram Username must be unique!'),
    ]

    def get_position(self, cr, uid, cancel_data=False, context=None):
        context = context or self.context_get(cr, uid)
        position = self.browse(cr, uid, uid, context)
        latitude = position.latitude
        longitude = position.longitude
        if cancel_data:
            self.write(cr, SUPERUSER_ID, uid, {'latitude': False, 'longitude': False}, context)

        return (latitude, longitude)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if context is None:
            context = {}
        default.update({'telegram_id': False, 'telegram_username': False, 'latitude': False, 'longitude': False})
        return super(res_users, self).copy(cr, uid, id, default, context=context)
