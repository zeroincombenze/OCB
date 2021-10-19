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
{
    'name': 'Human Resource on Contract',
    'version': '3.7.15.10',
    'category': 'Human Resource/Contractor',
    'description': """
        A generic module to manage on contract employees
    """,
    'author': "Didotech",
    'website': "http://www.didotech.com",
    'depends': [
        "base",
        "sale",
        "hr",
        "partner_pos_address",
        'l10n_it_base',
        "base_contact",
        "project"
    ],
    'data': [
        'security/ir.model.access.csv',
        'workflow/hr_contractor_workflow.xml',
        'wizard/hr_contractor_assign_task_view.xml',
        'wizard/confirm_engagement_deleting.xml',
        'views/hr_contractor_view.xml',
        'views/hr_department_view.xml',
        'views/hr_employee_category_view.xml',
        'views/product_product_view.xml',
        'views/res_partner_address_view.xml',
        'views/res_partner_brand_view.xml',
        'views/res_partner_contact_view.xml',
        'views/res_partner_view.xml',
        'views/hr_contract_agreement_view.xml',
        'data/hr_employee_sequence.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
