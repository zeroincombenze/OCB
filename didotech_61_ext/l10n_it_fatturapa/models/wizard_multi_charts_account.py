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


class wizard_multi_charts_accounts(orm.TransientModel):
    _inherit = "wizard.multi.charts.accounts"

    def generate_journals(self, cr, uid, chart_template_id, acc_template_ref, company_id, context=None):
        res = super(wizard_multi_charts_accounts, self).generate_journals(cr, uid, chart_template_id, acc_template_ref, company_id, context)
        journal_data = self._prepare_all_journals_PA(cr, uid, chart_template_id, acc_template_ref, company_id, context=context)
        for vals_journal in journal_data:
            self.check_created_journals(cr, uid, vals_journal, company_id, context=context)
        return True

    def _prepare_all_journals_PA(self, cr, uid, chart_template_id, acc_template_ref, company_id, context=None):

        def _get_analytic_journal(journal_type):
            # Get the analytic journal
            data = obj_data.get_object_reference(cr, uid, 'account', 'analytic_journal_sale')
            return data and data[1] or False

        def _get_default_account(journal_type, type='debit'):
            # Get the default accounts
            default_account = False
            if journal_type in ('sale', 'sale_refund'):
                default_account = acc_template_ref.get(template.property_account_income_categ.id)
            return default_account

        def _get_view_id(journal_type):
            # Get the journal views
            if journal_type == 'sale_refund':
                data = obj_data.get_object_reference(cr, uid, 'account', 'account_sp_refund_journal_view')
            else:
                data = obj_data.get_object_reference(cr, uid, 'account', 'account_sp_journal_view')
            return data and data[1] or False

        journal_names = {
            'sale': 'Fatture PA',
            'sale_refund': 'Note Accredito PA',
        }
        journal_codes = {
            'sale': 'FPA',
            'sale_refund': 'NCPA',
        }

        obj_data = self.pool['ir.model.data']
        template = self.pool['account.chart.template'].browse(cr, uid, chart_template_id, context=context)

        journal_data = []
        for journal_type in journal_names.keys():
            vals = {
                'type': journal_type,
                'name': journal_names[journal_type],
                'code': journal_codes[journal_type],
                'company_id': company_id,
                'centralisation': journal_type == 'situation',
                'view_id': _get_view_id(journal_type),
                'group_invoice_lines': True,
                'analytic_journal_id': _get_analytic_journal(journal_type),
                'default_credit_account_id': _get_default_account(journal_type, 'credit'),
                'default_debit_account_id': _get_default_account(journal_type, 'debit'),
            }
            journal_data.append(vals)

        return journal_data
