# -*- coding: utf-8 -*-
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

class account_cee_payment_methods(orm.Model):

    _name = "account.cee.payment.methods"

# Modalità di incasso
# a) Indicare il codice B (bonifico) nel caso in cui il servizio ricevuto venga pagato mediante bonifico bancario.
# b) Indicare il codice A (accredito) nel caso in cui il servizio ricevuto venga pagato mediante accredito in conto corrente bancario.
# c) Indicare il codice X (altro) nel caso in cui il servizio ricevuto venga pagato in modalità diverse da quelle previste nei punti a) e b). 

    _columns = {
        'code_alpha': fields.char('Code Alpha', size=1,
                                  required=True),
        'description': fields.text('Description',
                                   required=True),
        }

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for item in self.browse(cr, uid, ids, context=context):
            item_desc = (item.code_alpha or '') + ' - ' + (item.description or '')
            res.append((item.id, item_desc))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                                                context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}

        req_ids = self.search(cr, uid, args +
                              ['|',
                               ('code_alpha', operator, name),
                               ('description', operator, name)],
                              limit=limit,
                              context=context)
        return self.name_get(cr, uid, req_ids, context=context)
