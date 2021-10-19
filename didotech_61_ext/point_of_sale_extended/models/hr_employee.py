# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Didotech SRL. (<http://www.didotech.com>)
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
##############################################################################.

from random import randrange

from openerp.osv import orm


def generate_12_random_numbers():
    numbers = [9]
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


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    def create_employee_pos(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for hr_employee in self.browse(cr, uid, ids, context):
            numbers = generate_12_random_numbers()
            numbers.append(calculate_checksum(numbers))
            product_vals = {
                'name': hr_employee.name,
                'default_code': hr_employee.name.upper().replace(' ', '').replace('A', '').replace('E', '').replace('I', '').replace('O', '').replace('U', '')[:6],
                'ean13': ''.join(map(str, numbers)),
                'list_price': 0.0,
                'type': 'service',
            }
            product_id = self.pool['product.product'].create(cr, uid, product_vals, context)
            user_vals = {
                'name': hr_employee.name,
                'login': hr_employee.name.lower().replace(' ', '.'),
                'password': hr_employee.name.lower().split(' ')[0],
            }
            user_id = self.pool['res.users'].create(cr, uid, user_vals, context)
            hr_employee.write({'product_id': product_id, 'user_id': user_id})
        return True

