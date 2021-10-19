##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#    Copyright (C) 2014 Didotech srl
#    (<http://www.didotech.com>).
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

from openerp.osv import fields, orm
#from openerp.tools.translate import _


class res_partner(orm.Model):

    _inherit = "res.partner"

#     def create(self, cr, uid, vals, context=None):
#         if context is None:
#             context = {}
# 
#         if vals.get('property_account_position', False):
#             account_fiscal_position_obj = self.pool.get('account.fiscal.position')
#             account_fiscal_position = account_fiscal_position_obj.browse(cr, uid, vals['property_account_position'])
#             if account_fiscal_position and account_fiscal_position.intrastat:
#                 if not vals.get('incoterm_id', False):
#                     raise orm.except_orm(_('Error!'),
#                                          _('Campo Incoterm ("Condizioni di Consegna") obbligatorio se si imposta una posizione fiscale intra comunitaria!'))
#                 if not vals.get('way_of_freight', False):
#                     raise orm.except_orm(_('Error!'),
#                                          _('Campo "Metodo di Trasporto" obbligatorio se si imposta se si imposta una posizione fiscale intra comunitaria!'))
#                 if not vals.get('payment_methods', False):
#                     raise orm.except_orm(_('Error!'),
#                                          _('Campo "Metodi di Pagamento" obbligatorio se si imposta se si imposta una posizione fiscale intra comunitaria!'))
#                 if not vals.get('country_provenance', False):
#                     raise orm.except_orm(_('Error!'),
#                                          _('Campo "Paese di Provenienza" obbligatorio se si imposta se si imposta una posizione fiscale intra comunitaria!'))
# 
#         res = super(res_partner, self).create(cr, uid, vals, context)
# 
#         return res
# 
#     def write(self, cr, uid, ids, vals, context=None):
#         if context is None:
#             context = {}
#         if isinstance(ids, (long,int)):
#             ids = [ids]
#         partner = self.browse(cr, uid, ids, context=context)[0]
#         account_fiscal_position_obj = self.pool.get('account.fiscal.position')
# 
#         if partner.property_account_position and partner.property_account_position.intrastat or \
#             vals.get('property_account_position', False) and account_fiscal_position_obj.browse(
#                 cr, uid,[int(vals.get('property_account_position').split(',')[1])]):
#             
#             if not vals.get('incoterm_id', False) and not partner.incoterm_id:
#                 raise orm.except_orm(_('Error!'),
#                                      _('Campo "Condizioni di Consegna" obbligatorio se si imposta una posizione fiscale intra comunitaria!'))
#             if not vals.get('way_of_freight', False) and not partner.way_of_freight:
#                 raise orm.except_orm(_('Error!'),
#                                      _('Campo "Metodo di Trasporto" obbligatorio se si imposta una posizione fiscale intra comunitaria!'))
#             if not vals.get('payment_methods', False) and not partner.payment_methods:
#                 raise orm.except_orm(_('Error!'),
#                                      _('Campo "Metodi di Pagamento" obbligatorio se si imposta una posizione fiscale intra comunitaria!'))
#             if not vals.get('country_provenance', False) and not partner.country_provenance:
#                 raise orm.except_orm(_('Error!'),
#                                      _('Campo "Paese di Provenienza o di destinazione" obbligatorio se si imposta una posizione fiscale intra comunitaria!'))
# 
#         res = super(res_partner, self).write(cr, uid, ids, vals, context)
#         return res

    _columns = {
        'incoterm_id': fields.many2one('stock.incoterms',
                                    'Condizione di consegna',
                                    help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        'way_of_freight': fields.many2one('account.cee.way.of.freight',
                                          'Way of freight'),  # Modo trasporto - alfa 1
        'payment_methods': fields.many2one('account.cee.payment.methods',
                                           'Payment Methods'),  # Modalita incasso servizi - alfa 1
        'country_provenance': fields.many2one('res.country',
                                              'Provenance/Destination Country'),
        'province_destination': fields.many2one('res.province', # todo DA TOGLIERE E PRENDERE DALL'INDIRIZZO NEL PICKING/ORDER
                                                'Origin/Destination Province'),
        }