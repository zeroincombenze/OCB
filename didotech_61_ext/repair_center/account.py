# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech Inc. (<http://www.didotech.com>)
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
from openerp.osv import orm


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'
    
    def get_customer_products(self, cr, uid, partner_id, context):
        picking_ids = self.search(cr, uid, [('partner_id', '=', partner_id)])
        if picking_ids:
            return [order.product_id.id for order in self.browse(cr, uid, picking_ids, context)]
        else:
            return []
