# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2015 Didotech Srl <http://www.didotech.com>
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

{
    'name': 'Google Maps distance and duration',
    'version': '4.1.1.1',
    'category': 'Tools',
    'summary': 'Google Maps distance and duration between 2 points',
    'description': """
Google Maps distance and duration
=================================

Enter 2 addresses and the system will return a distance and a duration

Courtesy limit: 2,500 requests/day (based on Key or IP)

You need an API key to identify your application. API keys are managed through the Google APIs console. To create your key:

    - Visit the APIs console at Google APIs Console and log in with your Google Account.
    - Click the Services link from the left-hand menu in the APIs Console, then activate the Distance Matrix API service.
    - Once the service has been activated, your API key is available from the API Access page, in the Simple API Access section. Distance Matrix API applications use the Key for server apps
(https://developers.google.com/maps/documentation/distancematrix/)

https://code.google.com/apis/console/

    """,
    'author': 'Julius Network Solutions, Didotech srl',
    'website': 'http://www.julius.fr, http://www.didotech.com',
    'depends': [
        'base',
    ],
    'data': [
        'company_view.xml'
    ],
    'test': [],
    'installable': True,
    'active': False,
}
