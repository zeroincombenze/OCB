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
    "name": "SMS Client",
    "version": "3.0.6.4",
    "depends": ["base"],
    "author": "Didotech SRL",
    "website": "http://www.didotech.com",
    "description": """SMS Client module that provides:
    Sending SMS
    Use Multiple Gateways
    To validate Gateway, code is send to a mobile phone, when received enter it to confirm SMS account
    """,
    "category": "Tools",
    "data": [
        "views/smsclient_view.xml",
        "views/serveraction_view.xml",
        "views/smsclient_history_view.xml",
        "views/smsclient_queue_view.xml",
        "security/groups.xml",
        "security/ir.model.access.csv",
        "wizard/smsclient_wizard.xml",
        "data/smsclient_data.xml"
    ],
    "active": False,
    "installable": True
}
