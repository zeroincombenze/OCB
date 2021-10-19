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
    'name': 'POS Store Management',
    'version': '3.2.2.12',
    'category': 'Generic Modules/POS Store Manager',
    'description': """
        A generic module to manage customer's POS Store.
    """,
    'author': "Didotech SRL",
    "website": "http://www.didotech.com",
    'depends': [
        "base", "sale", "hr", 'l10n_it_base'
    ],
    "data": [
        'data/res_partner_director_sequence.xml',
        'security/ir.model.access.csv',
        'views/res_partner_address_view.xml',
        'views/res_partner_banner_view.xml',
        'views/res_partner_competitor_view.xml',
        'views/res_partner_department_view.xml',
        'views/res_partner_director_view.xml',
        # 'views/res_partner_job_view.xml',
        'views/res_partner_view.xml'
    ],
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
