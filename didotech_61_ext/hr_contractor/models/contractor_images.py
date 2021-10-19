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
from openerp.osv import orm, fields
import base64
import urllib


class contractor_images(orm.Model):
    "HR Contractors Image gallery"
    _name = "contractor.images"
    _description = __doc__
    _table = "contractor_images"
    
    def get_image(self, cr, uid, id):
        context = self.pool['res.users'].context_get(cr, uid)
        if not id:
            return {}
        each = self.browse(cr, uid, id, context=context)
        if each['link']:
            try:
                (filename, header) = urllib.urlretrieve(each['filename'])
                f = open(filename, 'rb')
                img = base64.encodestring(f.read())
                f.close()
            except:
                img = ''
        else:
            img = each['image']
        return img
    
    def _get_image(self, cr, uid, ids, field_name, arg, context={}):
        res = {}
        for each in ids:
            res[each] = self.get_image(cr, uid, each)
        return res
    
    _columns = {
        'name': fields.char('Image Title', size=100, required=True),
        'link': fields.boolean('Link?', help="Images can be linked from files on your file system or remote (Preferred)"),
        'image': fields.binary('Image', filters='*.png,*.jpg,*.gif'),
        'filename': fields.char('File Location', size=250),
        'preview': fields.function(_get_image, type="binary", method=True),
        'comments': fields.text('Comments'),
        'contractor_id': fields.many2one('hr.contractor', 'HR Contractor')
    }

    _defaults = {
        'link': lambda *a: True,
    }
