# -*- coding: utf-8 -*-
# © 2018 Nicola Gramola - Didotech srl (www.didotech.com)
# © 2019 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import orm, fields
import platform


class CompanyConfig(orm.Model):
    _inherit = "res.company"

    def _get_node(self, cr, uid, ids, field_name, arg, context):
        node = platform.node()
        return {company_id: node for company_id in ids}

    _columns = {
        'fpa_2c_username': fields.char('Username', 255),
        'fpa_2c_password': fields.char('Password', 50),
        'fpa_2c_formato_storage': fields.selection([('xml', 'XML'), ('p7m', 'P7M')],
                                                   'Invoice format'),
        'fpa_2c_sent_to_sdi': fields.boolean('Sent to SDI'),
        'fpa_2c_node': fields.char('Node', 64, required=True),
        'node': fields.function(_get_node, string='Node', method=True, type="char")
    }

    _defaults = {
        'fpa_2c_formato_storage': 'xml'
    }
