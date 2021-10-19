# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from openerp.osv import fields, orm
from collections import OrderedDict
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import datetime
from tools.translate import _
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class AccountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def get_index(self, cr, uid, account_id, remote_models, config, context=None):
        invoice = self.browse(cr, uid, account_id, context)

        if remote_models.get(invoice.type, False):
            document_type = remote_models[invoice.type].document_type
            date_invoice = datetime.datetime.strptime(invoice.date_invoice, DEFAULT_SERVER_DATE_FORMAT)

            if invoice.type == 'out_invoice':
                return {'Documento': OrderedDict((
                    ("NomeFile", {'@Value': ""}),
                    ("PathCompletoFile", {'@Value': ""}),
                    ("NumeroTipologia", {'@Value': document_type}),
                    ("Indice1", {'@Value': invoice.number}),
                    ("Indice2", {'@Value': date_invoice.strftime("%d/%m/%Y")}),
                    ("Indice3", {'@Value': invoice.partner_id.name}),
                    ("Indice4", {'@Value': invoice.partner_id.cf or invoice.partner_id.vat}),
                    ("Indice5", {'@Value': invoice.partner_id.vat}),
                    ("Indice6", {'@Value': ""}),
                    ("Indice7", {'@Value': ""}),
                    ("Indice8", {'@Value': ""}),
                    ("Indice9", {'@Value': ""}),
                    ("Indice10", {'@Value': ""}),
                    ("FullText", {'@Value': ""}),
                    ("Sostituzione", {'@Value': "0"}),
                    ("MantieniLock", {'@Value': "0"}),
                    ("Cancellare", {'@Value': "1"}),
                    ("AnnoArchiviazioneFile", {'@Value': date_invoice.year}),
                    ("AbilitaEspressioneCartellina", {'@Value': "1"}),
                    ("AbilitaRinominaFile", {'@Value': "0"}),
                    ("PathCartelline", {"Path": {
                        "PathCartellina": {'@Value': "{root}\{year}\{client}".format(
                            root=config.document_root,
                            year=date_invoice.year, client=invoice.partner_id.name
                        )}
                    }})
                ))}
            elif invoice.type == 'in_invoice':
                return {'Documento': OrderedDict((
                    ("NomeFile", {'@Value': ""}),
                    ("PathCompletoFile", {'@Value': ""}),
                    ("NumeroTipologia", {'@Value': document_type}),
                    ("Indice1", {'@Value': invoice.number}),
                    ("Indice2", {'@Value': date_invoice.strftime("%d/%m/%Y")}),
                    ("Indice3", {'@Value': ""}),  # Numero protocollo IVA
                    ("Indice4", {'@Value': ""}),  # Data registrazione protocollo IVA
                    ("Indice5", {'@Value': invoice.partner_id.name}),
                    ("Indice6", {'@Value': invoice.partner_id.cf or invoice.partner_id.vat}),
                    ("Indice7", {'@Value': invoice.partner_id.vat}),
                    ("Indice8", {'@Value': ""}),
                    ("Indice9", {'@Value': ""}),
                    ("Indice10", {'@Value': ""}),
                    ("FullText", {'@Value': ""}),
                    ("Sostituzione", {'@Value': "0"}),
                    ("MantieniLock", {'@Value': "0"}),
                    ("Cancellare", {'@Value': "1"}),
                    ("AnnoArchiviazioneFile", {'@Value': date_invoice.year}),
                    ("AbilitaEspressioneCartellina", {'@Value': "1"}),
                    ("AbilitaRinominaFile", {'@Value': "0"}),
                    ("PathCartelline", {"Path": {
                        "PathCartellina": {'@Value': "{root}\{year}\{client}".format(
                            root=config.document_root,
                            year=date_invoice.year, client=invoice.partner_id.name
                        )}
                    }})
                ))}
        else:
            _logger.warning(_(u"Please set Document Code for '{}'").format(invoice.type))
            raise orm.except_orm('Warning', _(u"Please set Document Code for '{}'").format(invoice.type))



