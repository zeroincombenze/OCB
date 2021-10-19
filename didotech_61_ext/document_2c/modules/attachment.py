# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import fields, orm
from openerp.addons.document_2c.modules.document_2c import SolutionDoc, Document


class Attachment(orm.Model):
    _inherit = 'ir.attachment'

    def _get_data(self, cr, uid, ids, name, arg, context=None):
        attachments = self.browse(cr, uid, ids, context)
        remote_models = self.pool['document.model.map'].get_models(
            cr, uid, attachments[0].company_id.id, attachments[0].res_model, context)
        if remote_models:
            company = self.pool['res.users'].browse(cr, uid, uid, context).company_id
            data = {}
            for attachment in attachments:
                with SolutionDoc(company) as archive:
                    data[attachment.id] = archive.get_data(attachment.store_fname)
            return data
        else:
            return super(Attachment, self)._data_get(cr, uid, ids, name, arg, context=context)

    def _set_data(self, cr, uid, attachment_id, name, value, arg, context=None):
        if value:
            attachment = self.browse(cr, uid, attachment_id, context)
            company = self.pool['res.users'].browse(cr, uid, uid, context).company_id

            remote_models = self.pool['document.model.map'].get_models(
                    cr, uid, attachment.company_id.id, attachment.res_model, context)

            if remote_models:
                document = Document(
                    attachment.datas_fname,
                    data=value
                )

                document_values = self.pool[attachment.res_model].get_index(
                    cr, uid, attachment.res_id, remote_models, company, context)

                document.set_index(document_values)

                with SolutionDoc(company) as archive:
                    archive.set_index()
                    archive.add(document)
                    file_id = archive.upload_data()

                    attachment.write({
                        'store_fname': file_id
                    })

                return True
            else:
                return super(Attachment, self)._data_set(cr, uid, attachment_id, name, value, arg, context=context)
        else:
            return True

    _columns = {
        'datas': fields.function(_get_data, fnct_inv=_set_data, string='File Content', type="binary", nodrop=True)
    }
