# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import fields, orm


class ResCompany(orm.Model):
    _inherit = 'res.company'
    _columns = {
        'document_host': fields.char('Document Host', size=128),
        'document_company_id': fields.char('Company ID', size=8),
        'document_user_id': fields.char('User ID', size=8),
        'document_username': fields.char('Username', size=32),
        'document_password': fields.char('Password', size=32),
        'document_models': fields.one2many('document.model.map', 'company_id', 'Models'),
        'document_root': fields.char('Root directory', size=32),
    }
