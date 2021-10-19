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
    "name": "Supplier Pricelist Import",
    "version": "3.2.5.5",
    "author": "Carlo Vettore, Andrei Levin",
    "category": "Generic Modules/Others",
    "description": '''Import CSV or Excel formatted pricelist of a selected supplier
        Attention! This module requires module xlrd''',
    "depends": [
        "profile_welld"
    ],
    'data': [
        "wizard/product_import_view.xml",
        "views/partner_properties_view.xml",
    ],
    "active": False,
    "installable": True,
    "auto_install": True,
}
