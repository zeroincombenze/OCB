# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Didotech SRL
#
#                          All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from random import randrange

from openerp.osv import orm, fields
from tools.translate import _


def generate_12_random_numbers(number):
    numbers = [number] # start_with_number 7
    for x in range(11):
        numbers.append(randrange(10))
    return numbers


def calculate_checksum(ean):
    """Calculates the checksum for EAN13-Code.
    @param list ean: List of 12 numbers for first part of EAN13
    :returns: The checksum for `ean`.
    :rtype: Integer
    """
    assert len(ean) == 12, "ean must be a list of 12 numbers for the first part of the EAN13"
    sum_ = lambda x, y: int(x) + int(y)
    evensum = reduce(sum_, ean[::2])
    oddsum = reduce(sum_, ean[1::2])
    return (10 - ((evensum + oddsum * 3) % 10)) % 10


class sale_shop(orm.Model):

    def _auto_init(self, cr, context={}):
        super(sale_shop, self)._auto_init(cr, context)

        cr.execute("SELECT 1 FROM pg_indexes WHERE indexname='sale_shop_pos_user_id_index'")
        if not cr.fetchone():
            cr.execute('CREATE INDEX sale_shop_pos_user_id_index ON sale_shop (pos_user_id)')

    _inherit = "sale.shop"
    _columns = {
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True),
        'transfert_product_id': fields.many2one('product.product', 'Transfert Product', domain=[('type', '=', 'service')]),
        'transfert_journal_id': fields.many2one('stock.journal', 'Stock Journal'),
        'ddt_sequence': fields.many2one('ir.sequence', 'Sequenza DDT', domain=[('code', '=', 'stock.ddt')]),
        'inventory_product_id': fields.many2one('product.product', 'Inventory Product', domain=[('type', '=', 'service')]),
    }

    _order = "name asc"

    def create_transfert_pos(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for sale_shop in self.browse(cr, uid, ids, context):
            numbers = generate_12_random_numbers(7)
            numbers.append(calculate_checksum(numbers))
            product_vals = {
                'name': _('Transfert to {shop}').format(shop=sale_shop.name),
                'default_code': sale_shop.name.upper().replace(' ', '').replace('A', '').replace('E', '').replace('I', '').replace('O', '').replace('U', '')[:6],
                'ean13': ''.join(map(str, numbers)),
                'list_price': 0.0,
                'type': 'service',
            }

            product_id = self.pool['product.product'].create(cr, uid, product_vals, context)
            journal_vals = {
                'name': _('Transfert from {shop}').format(shop=sale_shop.name),
                'default_invoice_state': 'none',
                'reopen_posted': True,
                'user_id': uid,
                'warehouse_id': sale_shop.warehouse_id.id,
                'lot_input_id': sale_shop.warehouse_id.lot_stock_id and sale_shop.warehouse_id.lot_stock_id.id or False,
                'member_ids': [(6, 0, [user.id for user in sale_shop.member_ids])] or []
            }
            stock_journal_id = self.pool['stock.journal'].create(cr, uid, journal_vals, context)
            sale_shop.write({'transfert_product_id': product_id, 'transfert_journal_id': stock_journal_id})
        return True
