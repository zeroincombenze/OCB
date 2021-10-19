# -*- coding: utf-8 -*-
# Copyright 2016-19 Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>
#
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#
from osv import fields, osv


class MideaNoCompany(osv.osv):
    _name = 'midea.no_company'

    _columns = {
        'name': fields.char('Name',
                            required=True,
                            translate=True,
                            index=1),
        'active': fields.boolean('Active',
                                 default=True),
        'state': fields.selection([('draft', 'Draft'),
                                   ('confirmed', 'Confirmed')],
                                  'State',
                                  required=True,
                                  readonly=True,
                                  index=1,
                                  default='draft')
    }
