# -*- coding: utf-8 -*-
# © 2019 Carlo Vettore - Didotech srl (www.didotech.com)

import logging
from datetime import datetime
from io import BytesIO

import lxml.etree as ET
from openerp.modules.module import get_module_resource
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

from .document_2c_fatturapa import FatturaPA_2C


class FatturapaAttachmentIn(orm.Model):
    _inherit = "fatturapa.attachment.in"

    _columns = {
        'sdi_id': fields.integer('IdSdi', readonly=True),
        'sdi_date': fields.datetime('DataSdi', readonly=True),
    }

