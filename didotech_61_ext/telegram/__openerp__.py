# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) 2016 Didotech srl (<http://www.didotech.com>).
#
#                       All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": """Telegram Bot""",
    "summary": """Telegram Integration""",
    "category": "Telegram",
    "version": "3.0.1.0",

    "author": "Didotech SRL",
    "website": "https://www.didotech.com",
    "description": """
        Add Telegram bot api key on
        Setting / Customization / Low Lever Object / System Parameters
    """,
    "depends": [
        "base",
    ],

    "data": [
        "security/ir.model.access.csv",
        "security/telegram_security.xml",
        "data/config_parameter.xml",
    #    "data/commands.xml",
        "data/fetchtelegram_data.xml",
        "views/telegram_views.xml",
        "views/telegram_command_views.xml",
        "views/res_user_view.xml",
        "views/telegram_thread_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "external_dependencies": {
        "python": ['telepot'],
        "bin": []
    },
}
