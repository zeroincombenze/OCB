# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class res_company(orm.Model):
    _inherit = 'res.company'
    _columns = {
        'style_sheet_mode': fields.selection([
            ('standard', 'Standard'),
            ('asso_software', 'Asso Software'),
        ], string="Style Sheet Mode"),
        'fatturapa_fiscal_position_id': fields.many2one(
            'fatturapa.fiscal_position', 'Fiscal Position',
            help="Fiscal position used by FatturaPA",
        ),
        'fatturapa_format_id': fields.many2one(
            'fatturapa.format', 'Format',
            help="FatturaPA Format",
        ),
        'fatturapa_sequence_id': fields.many2one(
            'ir.sequence', 'Sequence',
            help="il progressivo univoco del file è rappresentato da una "
                 "stringa alfanumerica di lunghezza massima di 5 caratteri "
                 "e con valori ammessi da “A” a “Z” e da “0” a “9”.",
        ),
        'fatturapa_art73': fields.boolean('Art73'),
        'fatturapa_pub_administration_ref': fields.char(
            'Public Administration Reference Code', size=20,
        ),
        'fatturapa_rea_office': fields.related(
            'partner_id', 'rea_office', type='many2one',
            relation='res.province', string='REA office'),
        'fatturapa_rea_number': fields.related(
            'partner_id', 'rea_code', type='char',
            size=20, string='Rea Number'),
        'fatturapa_rea_capital': fields.related(
            'partner_id', 'rea_capital', type='float',
            string='Rea Capital'),
        'fatturapa_rea_partner': fields.related(
            'partner_id', 'rea_member_type', type='selection',
            selection=[
                ('SU', 'Unique Member'),
                ('SM', 'Multiple Members'),
            ],
            string='Member Type'),
        'fatturapa_rea_liquidation': fields.related(
            'partner_id', 'rea_liquidation_state', type='selection',
            selection=[
                ('LS', 'In liquidation'),
                ('LN', 'Not in liquidation'),
            ],
            string='Liquidation State'),
        'fatturapa_tax_representative': fields.many2one(
            'res.partner', 'Legal Tax Representative'
        ),
        'fatturapa_sender_partner': fields.many2one(
            'res.partner', 'Third Party/Sender'
            ),
        'fatturapa_stabile_organizzazione': fields.many2one(
            'res.partner', 'Stabile Organizzazione',
            help='Blocco da valorizzare nei casi di cedente / prestatore non '
                 'residente, con stabile organizzazione in Italia'
        ),
        'product_stamp_ids': fields.many2many('product.product', string='Bolli in Fattura', domain=[('type', '=', 'service')]),
    }

    _defaults = {
        'style_sheet_mode': 'standard'
    }

    def _check_fatturapa_sequence_id(self, cr, uid, ids, context=None):
        for company in self.browse(cr, uid, ids, context):
            if company.fatturapa_sequence_id:
                journal = self.pool.get('account.journal').search(cr, uid, [
                    ('sequence_id', '=', company.fatturapa_sequence_id.id)
                ], limit=1)
                if journal:
                    return False
        return True
