# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import fields, orm


class DocumentModelMap(orm.Model):
    _name = 'document.model.map'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'name': fields.char('Model', size=32),
        'code': fields.char('Type Code', size=32),
        'description': fields.char('Type Description', size=32),
        'document_type': fields.char('Type', size=8)
    }

    def get_models(self, cr, uid, company_id, model_name, context=None):
        model_ids = self.search(cr, uid, [('company_id', '=', company_id), ('name', '=', model_name)], context=context)
        models = self.browse(cr, uid, model_ids, context)
        return {model.code: model for model in models}
