# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
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
from openerp.tools.translate import _


class sale_order(orm.Model):
    _inherit = "sale.order"

    _columns = {
        'country_provenance': fields.many2one('res.country', 'Provenance Country'),
        'province_destination': fields.many2one('res.province', 'Province destination'),
        'way_of_freight': fields.many2one('account.cee.way.of.freight', 'Way of freight'),
    }


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def _prepare_order_line_invoice_line(self, cr, uid, order_line, account_id=False, context=None):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, order_line, account_id=False, context=context)
        partner_id = order_line.order_id.partner_id

        # check and pass the 4 fields
        if order_line.order_id.country_provenance:
            res['country_provenance'] = order_line.order_id.country_provenance.id
        elif partner_id.property_account_position and partner_id.property_account_position.intrastat:
            if partner_id.country_provenance:
                res['country_provenance'] = partner_id.country_provenance.id
            else:
                raise orm.except_orm(_('Error'), _('Country provenance missing'))
        #2nd field
        if order_line.product_id and partner_id.property_account_position and partner_id.property_account_position.intrastat:
            if order_line.product_id.country_origin:
                res['country_origin'] = order_line.product_id.country_origin.id
            else:
                raise orm.except_orm(_('Error'), _('Country origin missing'))

        #3rd field - same code
        if order_line.order_id.way_of_freight:
            res['way_of_freight'] = order_line.order_id.way_of_freight.id
        elif partner_id.property_account_position and partner_id.property_account_position.intrastat:
            if partner_id.way_of_freight:
                res['way_of_freight'] = partner_id.way_of_freight.id
            else:
                raise orm.except_orm(_('Error'), _('Way of freight missing'))
        #4th field - same code
        if order_line.order_id.province_destination:
            res['province_destination'] = order_line.order_id.province_destination.id
        elif partner_id.property_account_position and partner_id.property_account_position.intrastat:
            if partner_id.province_destination:
                res['province_destination'] = partner_id.province_destination.id
        #5th field - same code
        if order_line.order_id.incoterm:
            res['incoterm'] = order_line.order_id.incoterm.id
        elif partner_id.property_account_position and partner_id.property_account_position.intrastat:
            if partner_id.incoterm_id:
                res['incoterm'] = partner_id.incoterm_id.id
            else:
                raise orm.except_orm(_('Error'), _('Incoterm condition missing'))

        return res
