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


class hr_contractor_address(orm.Model):
    _description = "Contractor Address"
    _inherit = 'res.partner.address'
    _columns = {
        'contract_type_id': fields.many2one('hr.contract.agreement.type', 'Contratto Richiesto', select=True),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'is_employee_address': fields.boolean('Is Employee Address ?'),
    }
    _defaults = {
        'is_employee_address': 1,
    }
