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

class account_cee_intrastat_flows(orm.Model):

    _name = "account.cee.intrastat.flows"

    def _get_write_date(self, cr, uid, ids, field_name,
                                arg, context=None):
        result = {}
        res = self.perm_read(cr, uid, ids)[0].get('write_date', None)
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = res
        return result

    def _get_write_uid(self, cr, uid, ids, field_name,
                                arg, context=None):
        result = {}
        res = self.perm_read(cr, uid, ids, details=True)[0].get('write_uid',
                                                                None)
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = res
        return result

    def _get_create_date(self, cr, uid, ids, field_name,
                                arg, context=None):
        result = {}
        res = self.perm_read(cr, uid, ids)[0].get('create_date', None)
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = res
        return result

    def _get_create_uid(self, cr, uid, ids, field_name,
                                arg, context=None):
        result = {}
        res = self.perm_read(cr, uid, ids, details=True)[0].get('create_uid', None)
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = res
        return result

    _columns = {
        'flow_number': fields.integer('Numero del flusso', size=6,
                                             required=True, readonly=True),
        'flow_year': fields.integer('Anno di riferimento', size=4,
                                             required=True, readonly=True),
        'flow_month_quarter': fields.integer('Mese o trimestre', size=2,
                                             required=True, readonly=True),
        'flow_period_type': fields.char('M=Mensile T=Trimest.', size=1,
                                             required=True, readonly=True),
        'flow_type': fields.char('A=Acquisti V=Vendite', size=1,
                                             required=True, readonly=True),
        'flow_rows_count1': fields.integer('Righe sezione 1', size=5,
                                             required=True, readonly=True),
        'flow_total_1': fields.integer('Totale sezione 1', size=13,
                                             required=True, readonly=True),
        'flow_rows_count2': fields.integer('Righe sezione 2', size=5,
                                             required=True, readonly=True),
        'flow_total_2': fields.integer('Totale sezione 2', size=13,
                                             required=True, readonly=True),
        'flow_rows_count3': fields.integer('Righe sezione 3', size=5,
                                             required=True, readonly=True),
        'flow_total_3': fields.integer('Totale sezione 3', size=13,
                                             required=True, readonly=True),
        'flow_rows_count4': fields.integer('Righe sezione 4', size=5,
                                             required=True, readonly=True),
        'flow_total_4': fields.integer('Totale sezione 4', size=13,
                                             required=True, readonly=True),

        'write_date': fields.function(_get_write_date,
                                             type="date",
                                             readonly=True,
                                             string='Write date'),
        'write_uid': fields.function(_get_write_uid,
                                             type="char",
                                             readonly=True,
                                             string='Write user'),
        'create_date': fields.function(_get_create_date,
                                             type="date",
                                             readonly=True,
                                             string='Create date'),
        'create_uid': fields.function(_get_create_uid,
                                             type="char",
                                             readonly=True,
                                             string='Create user'),
        }
