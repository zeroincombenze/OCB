# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2014 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import datetime
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class wizard_download__repair_attachments(orm.TransientModel):
    _name = "wizard.download.repair.attachments"
    _description = 'Download products attachments'

    _columns = {
        'data': fields.binary("File", readonly=True),
        'name': fields.char('Filename', 32, readonly=True),
        'state': fields.selection((
            ('choose', 'choose'),   # choose
            ('get', 'get'),         # get the file
        )),
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }

    def download_attachment(self, cr, uid, ids, context={}):
        attachment_obj = self.pool['ir.attachment']
        
        name = context.get('name', 'Repair')
        file_name = '{0}_{1}.zip'.format(name, datetime.datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT))
        
        repair_id = context.get('active_id', False)
        repair_order = self.pool['repair.order'].browse(cr, uid, repair_id, context)
        attachment_ids = set()
        attachment_ids = attachment_ids.union(attachment_obj.search(cr, uid, [('res_model', '=', 'product.product'),
                                                                                  ('res_id', '=', repair_order.product_id.id),
                                                                             ], context=context))

        out = attachment_obj.get_as_zip(cr, uid, attachment_ids, log=True)
        return self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': file_name}, context=context)
