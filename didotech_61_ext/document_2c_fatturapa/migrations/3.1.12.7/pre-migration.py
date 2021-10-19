# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
#
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
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

import logging
logger = logging.getLogger()


def migrate(cr, version):
    if not version:
        return
    try:
        cr.execute(
        """
            UPDATE fatturapa_attachment_out SET state = 'sent' WHERE state = 'draft'
        """)
    except Exception as e:
        # Annulla le modifiche fatte
        print e
        # UPDATE stock_picking SET sale_id = pos_id;
# UPDATE stock_move SET sale_line_id = pos_line_id;