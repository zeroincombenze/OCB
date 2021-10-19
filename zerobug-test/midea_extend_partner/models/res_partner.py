# -*- coding: utf-8 -*-
#
# Copyright 2018-20 - SHS-AV s.r.l. <https://www.zeroincombenze.it/>
#
# Contributions to development, thanks to:
# * Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>
#
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from openerp.osv import orm, fields


class ResPartner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'zone': fields.char('Zona')
    }

    def onchange_zone(self, cr, uid, ids, zone, context=None):
        res = {}
        if zone.lower() == 'torino':
            res['value'] = {
                    'phone': '0111234567',
                    'email': 'io@example.com'
                }
            res['warning'] = 'Telefono modificato!'
        return res

    def create(self, cr, uid, vals, context=None):
        if vals.get('zone', False):
            vals['comment'] = 'Soggetto zona %s' % vals['zone']
        return super(ResPartner, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('zone', False):
            vals['comment'] = 'Soggetto zona %s' % vals['zone']
        return super(ResPartner, self).write(cr, uid, ids, vals, context)

