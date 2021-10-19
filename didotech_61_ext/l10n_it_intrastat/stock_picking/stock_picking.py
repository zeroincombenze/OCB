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


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'country_provenance': fields.many2one('res.country', 'Provenance Country'),
        'province_destination': fields.many2one('res.province', 'Province origin/destination'),
        'way_of_freight': fields.many2one('account.cee.way.of.freight', 'Way of freight'),
    }
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        res = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id,
            invoice_vals, context=context)
        partner_id = picking.partner_id
        if picking.country_provenance or partner_id.property_account_position and partner_id.property_account_position.intrastat:
            res['country_provenance'] = picking.country_provenance and picking.country_provenance.id or partner_id.country_provenance.id
        
        if partner_id.property_account_position and partner_id.property_account_position.intrastat:
            if move_line.product_id.country_origin:
                res['country_origin'] = move_line.product_id.country_origin.id
            else:
                raise orm.except_orm(_('Error'), _('Country origin missing'))

        if picking.province_destination or partner_id.property_account_position and partner_id.property_account_position.intrastat:
            res['province_destination'] = picking.province_destination and picking.province_destination.id or partner_id.province_destination.id
        if picking.way_of_freight or partner_id.property_account_position and partner_id.property_account_position.intrastat:
            res['way_of_freight'] = picking.way_of_freight and picking.way_of_freight.id or partner_id.way_of_freight.id
        return res
