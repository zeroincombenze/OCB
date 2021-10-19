##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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
from openerp.tools.translate import _


class account_cee_service_codes(orm.Model):
    _inherit = "res.company"

    _columns = {
        # CodiceUA (codice utente abilitato) 4 alfa
        'code_ua': fields.char('Enabled User Code', size=4),

        # Periodicita flusso acquisto beni 1 alfa (M o T)
        'period_purchase_goods': fields.selection([('M', _('Monthly')),
                                                   ('T', _('Quarterly')),
                                                   ], 'Periodicity flow purchase goods', size=1),
        # Periodicita flusso acquisto servizi 1 alfa (M o T)
        'period_purchase_services': fields.selection([
            ('M', _('Monthly')),
            ('T', _('Quarterly')),
        ], 'Periodicity flow purchase services', size=1),
        # Periodicita flusso cessione beni 1 alfa (M o T)
        'period_disposals_goods': fields.selection([
            ('M', _('Monthly')),
            ('T', _('Quarterly')),
        ], 'Periodicity flow disposals goods', size=1),
        # Periodicita flusso cessione servizi 1 alfa (M o T)
        'period_disposals_services': fields.selection([
            ('M', _('Monthly')),
            ('T', _('Quarterly')),
        ], 'Periodicity flow disposals services', size=1),
        'province_origin': fields.many2one('res.province',
                                           'Province origin'),
        'province_destination': fields.many2one('res.province',
                                                'Province destination'),
        'vat_delegated_person': fields.char('VAT delegated person', size=16),
        }
