# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016-2020 Didotech srl
##############################################################################
import base64
from openerp.osv import orm, fields
from openerp.addons.l10n_it_ade.bindings.fatturapa_v_1_2 import (
    AllegatiType,
)


class WizardExportFatturapa(orm.TransientModel):
    _inherit = "wizard.export.fatturapa"
    _description = "Export E-invoice"

    def _attachment_list(self, cr, uid, ids, context):
        active_id = context.get('active_id', False)
        active_model = context.get('active_model', False)
        if not (active_id and active_model):
            raise orm.except_orm(
                'Error',
                'Missing active_id or active_model')

        model = self.pool[active_model].browse(cr, uid, active_id, context=context)

        description = []
        if model.company_id:
            for attachement in model.company_id.fatturapa_doc_attachments:
                description.append("* {name}".format(name=attachement.datas_fname))

        if description:
            attachment_list = "ATTENZIONE CONTIENE I SEGUENTI ALLEGATI GLOBALI \n" + '\n'.join(description)
        else:
            attachment_list = ''
        return attachment_list

    def _get_attachement_list(self, cr, uid, ids, name, unknow_none, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        ret = {}
        attachment_list = self._attachment_list(cr, uid, ids, context)
        for att in self.browse(cr, uid, ids, context):
            ret[att.id] = attachment_list
        return ret

    _columns = {
        'attachment_list': fields.function(_get_attachement_list, string="Allegati", type="text")
    }

    def default_get(self, cr, uid, fields, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(WizardExportFatturapa, self).default_get(cr, uid, fields, context=context)
        res['attachment_list'] = self._attachment_list(cr, uid, [], context)
        return res

    def setAttachments(self, cr, uid, invoice, body, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        res = super(WizardExportFatturapa, self).setAttachments(cr, uid, invoice, body, context)
        if invoice.company_id.fatturapa_doc_attachments:
            for doc_id in invoice.company_id.fatturapa_doc_attachments:
                # Field Attachment is of Base64 type, so data is encoded automatically when put inside
                # Our attachments are already Base64 encoded, so we should decode them
                AttachDoc = AllegatiType(
                    NomeAttachment=doc_id.datas_fname,
                    Attachment=base64.b64decode(doc_id.datas)
                )
                body.Allegati.append(AttachDoc)

        return True
