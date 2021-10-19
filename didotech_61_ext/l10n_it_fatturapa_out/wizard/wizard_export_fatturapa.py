# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Davide Corio <davide.corio@lsweb.it>
#    Copyright (C) 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#    Copyright (C) 2016-2020 Didotech srl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

import base64
import logging
import re
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import netsvc

_logger = logging.getLogger(__name__)

try:
    import phonenumbers
except ImportError:
    _logger.debug('Cannot `import phonenumbers`.')  # Avoid init error if not installed

try:
    import codicefiscale
except ImportError:
    _logger.debug('Cannot `import codicefiscale`.')  # Avoid init error if not installed

from core_extended.ordereddict import OrderedDict
from openerp.addons.l10n_it_ade.bindings.fatturapa_v_1_2 import (
    IdFiscaleType,
    ContattiTrasmittenteType,
    CedentePrestatoreType,
    AnagraficaType,
    IndirizzoType,
    IscrizioneREAType,
    CessionarioCommittenteType,
    RappresentanteFiscaleType,
    DatiAnagraficiCedenteType,
    DatiAnagraficiCessionarioType,
    DatiAnagraficiRappresentanteType,
    TerzoIntermediarioSoggettoEmittenteType,
    DatiAnagraficiTerzoIntermediarioType,
    FatturaElettronicaBodyType,
    DatiGeneraliType,
    DettaglioLineeType,
    AltriDatiGestionaliType,
    TipoScontoMaggiorazioneType,
    DatiBeniServiziType,
    DatiDDTType,
    DatiRiepilogoType,
    DatiGeneraliDocumentoType,
    DatiRitenutaType,
    DatiBolloType,
    DatiCassaPrevidenzialeType,
    DatiDocumentiCorrelatiType,
    ContattiType,
    DatiPagamentoType,
    DettaglioPagamentoType,
    AllegatiType,
    ScontoMaggiorazioneType,
    CodiceArticoloType,
    FatturaElettronica,
    FatturaElettronicaHeaderType,
    DatiTrasmissioneType,
    String10Type
)
from openerp.addons.l10n_it_fatturapa.models.account import (
    RELATED_DOCUMENT_TYPES)
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from pyxb.exceptions_ import SimpleFacetValueError, SimpleTypeValueError
from unidecode import unidecode
from validate_email import validate_email

VERSIONE_PA = '1.2'
FORMATO_TRASMISSIONE_PA = 'FPA12'  # Valid for Format 1.2 and 1.2.1
FORMATO_TRASMISSIONE_PR = 'FPR12'  # Valid for Format 1.2 and 1.2.1
STYLESHEET = 'fatturapa_v1.2.xsl'
SOFTWARE_IN_USE = String10Type('OpenERP6.1')


class WizardExportFatturapa(orm.TransientModel):
    _name = "wizard.export.fatturapa"
    _description = "Export E-invoice"

    order_model = 'sale.order'

    def __init__(self, cr, uid):
        self.invoice_tree = {}
        return super(WizardExportFatturapa, self).__init__(cr, uid)

    _columns = {
        'report_print_menu': fields.boolean("Attach Invoice Report", help='This report will be automatically included in the created XML')
    }

    _default = {
        'report_print_menu': True
    }

    def u_normalize(self, name, lower=True):
        translation = [
            (u' ', u''),
            (u"'", u""),
            (u"ì", u"i"),
            (u"è", u"e"),
            (u"é", u"e"),
            (u"ò", u"o"),
            (u"à", u"a"),
            (u"á", u"a"),
            (u"ù", u"u"),
            (u'̀', u''),
            (u"°", u" "),
            (u"\t", u"")
        ]

        if lower:
            name = name.lower()
        else:
            translation += [(trans[0].upper(), trans[1].upper()) for trans in translation]
            translation = set(translation)

        for character, substitutor in translation:
            name = name.replace(character, substitutor)

        # faster but less readable:
        # name = reduce(lambda n, t: n.replace(t[0], t[1]), translation, name)
        return name

    def saveAttachment(self, cr, uid, fatturapa, number, context=None):
        if context is None:
            context = {}

        user_obj = self.pool['res.users']
        company = user_obj.browse(cr, uid, uid).company_id

        if not company.vat:
            raise orm.except_orm(
                _('Error!'), _('Company TIN not set.'))
        if company.fatturapa_sender_partner and not company.fatturapa_sender_partner.vat:
            raise orm.except_orm(_('Error!'), _('Partner %s TIN not set.') % company.fatturapa_sender_partner.name)
        vat = company.vat
        if company.fatturapa_sender_partner:
            vat = company.fatturapa_sender_partner.vat
        vat = vat.replace(' ', '').replace('.', '').replace('-', '')

        invoice_xml = fatturapa.toDOM().toprettyxml(encoding="latin1").replace(
            '<?xml version="1.0" encoding="latin1"?>',
            '<?xml version="1.0" encoding="latin1"?>'
            '<?xml-stylesheet type="text/xsl" href="{xsl}"?>'.format(xsl=STYLESHEET))

        attach_vals = {
            'name': '%s_%s.xml' % (vat, str(number)),
            'datas_fname': '%s_%s.xml' % (company.vat, str(number)),
            'datas': base64.encodestring(invoice_xml),
            'type': 'binary'
        }
        return self.pool['fatturapa.attachment.out'].create(cr, uid, attach_vals, context=context or {})

    def setProgressivoInvio(self, cr, uid, fatturapa, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        user_obj = self.pool['res.users']
        company = user_obj.browse(cr, uid, uid).company_id
        sequence_obj = self.pool['ir.sequence']
        fatturapa_sequence = company.fatturapa_sequence_id

        if not fatturapa_sequence:
            raise orm.except_orm(
                _('Error!'), _('E-invoice sequence not configured.'))

        number = sequence_obj.next_by_id(
            cr, uid, fatturapa_sequence.id, context=context)

        try:
            fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
                ProgressivoInvio = number
        except (SimpleFacetValueError, SimpleTypeValueError) as e:
            msg = _(
                'FatturaElettronicaHeader.DatiTrasmissione.'
                'ProgressivoInvio:\n%s'
            ) % unicode(e)
            raise _('Error!'), _(msg)
        return number

    def _setIdTrasmittente(self, cr, uid, company, fatturapa, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if company.fatturapa_sender_partner:
            if not company.fatturapa_sender_partner.address[0].country_id:
                raise orm.except_orm(
                    _('Error!'), _('Company Country not set.'))
            IdPaese = company.fatturapa_sender_partner.address[0].country_id.code

            IdCodice = company.fatturapa_sender_partner.fiscalcode
            if not IdCodice:
                if not company.fatturapa_sender_partner.vat:
                    raise orm.except_orm(
                        _('Error!'), _('Company VAT not set.'))
                IdCodice = company.fatturapa_sender_partner.vat[2:]
            else:
                if IdCodice[0:2] == IdPaese:
                    IdCodice = IdCodice[2:]

            if not IdCodice:
                raise orm.except_orm(
                    _('Error'), _('Company does not have fiscal code or VAT'))
        else:

            if not company.country_id:
                raise orm.except_orm(
                    _('Error!'), _('Company Country not set.'))
            IdPaese = company.country_id.code

            IdCodice = company.partner_id.fiscalcode
            if not IdCodice:
                if not company.vat:
                    raise orm.except_orm(
                        _('Error!'), _('Company VAT not set.'))
                IdCodice = company.vat[2:]
            else:
                if IdCodice[0:2] == IdPaese:
                    IdCodice = IdCodice[2:]

            if not IdCodice:
                raise orm.except_orm(
                    _('Error'), _('Company does not have fiscal code or VAT'))

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
            IdTrasmittente = IdFiscaleType(
                IdPaese=IdPaese, IdCodice=IdCodice)

        return True

    def _setFormatoTrasmissione(self, cr, uid, partner, fatturapa, company, context=None):
        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.FormatoTrasmissione = fatturapa.versione
        return True

    def _setCodiceDestinatario(self, cr, uid, partner, fatturapa, context=None):
        # Nota sito agenzia entrate:
        # Il Codice Destinatario a 7 caratteri, che può essere utilizzato solo per fatture elettroniche destinate ai
        # soggetti privati, potrà essere reperito attraverso un nuovo servizio reso disponibile entro il
        # 9 di Gennaio 2017 sul sito www.fatturapa.gov.it, pagina Strumenti – Gestire il canale.
        # Il codice potrà essere richiesto solo dai quei soggetti titolari di un canale di trasmissione già accreditato
        # presso il Sistema di Interscambio per ricevere le fatture elettroniche. É possibile richiedere più codici fino
        # a un massimo di 100. Per i soggetti che invece intendano ricevere le fatture elettroniche attraverso il canale
        #  PEC, è previsto l’uso del codice destinatario standard ‘0000000’ purché venga indicata la casella PEC di
        # ricezione in fattura nel campo PecDestinatario. Vale la pena ricordare che per le fatture elettroniche
        # destinate ad Amministrazioni pubbliche si continua a prevedere l’uso del codice univoco ufficio a 6 caratteri,
        # purché sia censito su indice delle Pubbliche Amministrazioni (www.indicepa.gov.it )

        if partner.address:
            partner_address = partner.address[0]
            code = partner_address.unique_office_code or partner_address.ipa_code or False
            pec_destinatario = partner_address.pec or False
        else:
            partner_address = False
            code = False
            pec_destinatario = None

        if not code:
            code = partner.codice_destinatario or partner.ipa_code or False
        if not pec_destinatario:
            pec_destinatario = partner.pec_destinatario

        if fatturapa.versione == FORMATO_TRASMISSIONE_PA:
            if not code:
                raise orm.except_orm(
                    _('Error!'), _('IPA Code is not set in partner form.'))
            if len(code) != 6:
                if ' ' in code:
                    raise orm.except_orm(
                        _('Error!'), _('Space char in IPA Code \'{code}\'').format(code=code))
                else:
                    raise orm.except_orm(
                        _('Error!'), _('IPA Code {code} dimension {dimension} in place of 6').format(code=code, dimension=len(code)))
        else:
            if not code:
                # if partner.vat or partner.fiscalcode:
                if partner_address and not partner_address.country_id:
                    raise orm.except_orm(
                        u"Error",
                        u"Mancanza il paese nell'indirizzo")
                if partner_address and partner_address.country_id.code == 'IT':
                    code = '0000000'

                    if pec_destinatario:
                        if validate_email(pec_destinatario):
                            fatturapa.FatturaElettronicaHeader.DatiTrasmissione.PECDestinatario = pec_destinatario
                        else:
                            raise orm.except_orm(_('Error!'),
                                                 _('{pec_email} is not correct').format(pec_email=pec_destinatario))
                    elif partner.vat:
                        raise orm.except_orm(
                            _('Error!'),
                            _('No PEC find for Partner: {partner}').format(partner=partner.name))
                elif partner_address and not partner_address.country_id.code == 'IT':
                    code = 'XXXXXXX'
                else:
                    raise orm.except_orm(
                        _('Error!'),
                        _('No Address find for Partner: {partner}').format(partner=partner.name))
                # else:
                #     raise orm.except_orm(
                #         _('Error!'),
                #         _('Please set Fiscal Code or VAT for partner {}').format(partner.name))
            elif len(code) != 7:
                if ' ' in code:
                    raise orm.except_orm(
                        _('Error!'), _('Space char in Recipient Code \'{code}\'').format(code=code))
                else:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Recipient Code {code} length {dimension} is not 7').format(code=code, dimension=len(code)))

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.CodiceDestinatario = code.upper()

        return True

    def _setContattiTrasmittente(self, cr, uid, company, fatturapa, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if company.fatturapa_sender_partner:
            if not company.fatturapa_sender_partner.address[0].phone:
                raise orm.except_orm(
                    _('Error!'), _('Company Telephone number not set.'))
            Telefono = self.checkSetupPhone(company.fatturapa_sender_partner.address[0].phone)

            Email = company.fatturapa_sender_partner.address[0].email or company.fatturapa_sender_partner.address[0].pec
            if not Email:
                raise orm.except_orm(
                    _('Error!'), _('Email address not set.'))
            elif not validate_email(Email):
                raise orm.except_orm(
                    _('Error!'), _('Email address not valid format.'))
        else:
            if not company.phone:
                raise orm.except_orm(
                    _('Error!'), _('Company Telephone number not set.'))
            Telefono = self.checkSetupPhone(company.phone)

            if not company.email:
                raise orm.except_orm(
                    _('Error!'), _('Email address not set.'))
            elif not validate_email(company.email):
                raise orm.except_orm(
                    _('Error!'), _('Email address not valid format.'))
            Email = company.email

        fatturapa.FatturaElettronicaHeader.DatiTrasmissione.\
            ContattiTrasmittente = ContattiTrasmittenteType(
                Telefono=Telefono, Email=Email)

        return True

    def checkSetupPhone(self, phone_number=False):
        if phone_number and '+' in phone_number:
            phone_number = phonenumbers.format_number(phonenumbers.parse(phone_number), phonenumbers.PhoneNumberFormat.NATIONAL)
        return phone_number

    def setDatiTrasmissione(self, cr, uid, company, partner, fatturapa, partner_address=None, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        fatturapa.FatturaElettronicaHeader.DatiTrasmissione = (DatiTrasmissioneType())
        self._setIdTrasmittente(cr, uid, company, fatturapa, context=context)
        self._setFormatoTrasmissione(cr, uid, partner, fatturapa, company, context=context)
        self._setCodiceDestinatario(cr, uid, partner, fatturapa, context=context)
        self._setContattiTrasmittente(cr, uid, company, fatturapa, context=context)

    def _setDatiAnagraficiCedente(self, cr, uid, CedentePrestatore,
                                  company, context=None):
        if context is None:
            context = {}

        if not company.vat:
            raise orm.except_orm(
                _('Error!'), _('TIN not set.'))
        CedentePrestatore.DatiAnagrafici = DatiAnagraficiCedenteType()
        fatturapa_fp = company.fatturapa_fiscal_position_id
        if not fatturapa_fp:
            raise orm.except_orm(
                _('Error!'), _('FatturaPA fiscal position not set.'))
        CedentePrestatore.DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
            IdPaese=company.country_id.code, IdCodice=company.vat[2:])
        CedentePrestatore.DatiAnagrafici.Anagrafica = AnagraficaType(
            Denominazione=company.name)

        if company.partner_id.fiscalcode:
            CedentePrestatore.DatiAnagrafici.CodiceFiscale = (
                company.partner_id.fiscalcode)
        CedentePrestatore.DatiAnagrafici.RegimeFiscale = fatturapa_fp.code
        return True

    def _setAlboProfessionaleCedente(self, cr, uid, CedentePrestatore,
                                     company, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # TODO Albo professionale, for now the main company is considered
        # to be a legal entity and not a single person
        # 1.2.1.4   <AlboProfessionale>
        # 1.2.1.5   <ProvinciaAlbo>
        # 1.2.1.6   <NumeroIscrizioneAlbo>
        # 1.2.1.7   <DataIscrizioneAlbo>
        return True

    def _setSedeCedente(self, cr, uid, CedentePrestatore,
                        company, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if not company.street:
            raise orm.except_orm(
                _('Error!'), _('Street not set.'))
        if not company.zip:
            raise orm.except_orm(
                _('Error!'), _('ZIP not set.'))
        if not company.city:
            raise orm.except_orm(
                _('Error!'), _('City not set.'))
        if not company.partner_id.address and company.partner_id.address[0].province:
            raise orm.except_orm(
                _('Error!'), _('Province not set.'))
        if not company.country_id:
            raise orm.except_orm(
                _('Error!'), _('Country not set.'))
        # FIXME: manage address number in <NumeroCivico>
        # see https://github.com/OCA/partner-contact/pull/96
        CedentePrestatore.Sede = IndirizzoType(
            Indirizzo=company.street,
            CAP=company.zip,
            Comune=company.city[:60],
            Provincia=company.partner_id.address[0].province.code,
            Nazione=company.country_id.code)

        return True

    def _setStabileOrganizzazione(self, cr, uid, CedentePrestatore,
                                  company, context=None):
        if context is None:
            context = {}
        if company.fatturapa_stabile_organizzazione:
            stabile_organizzazione = company.fatturapa_stabile_organizzazione
            if not stabile_organizzazione.street:
                raise orm.except_orm(_('Error!'),
                    _('Street not set for %s') % stabile_organizzazione.name)
            if not stabile_organizzazione.zip:
                raise orm.except_orm(_('Error!'),
                    _('ZIP not set for %s') % stabile_organizzazione.name)
            if not stabile_organizzazione.city:
                raise orm.except_orm(_('Error!'),
                    _('City not set for %s') % stabile_organizzazione.name)
            if not stabile_organizzazione.country_id:
                raise orm.except_orm(_('Error!'),
                    _('Country not set for %s') % stabile_organizzazione.name)
            CedentePrestatore.StabileOrganizzazione = IndirizzoType(
                Indirizzo=stabile_organizzazione.street,
                CAP=stabile_organizzazione.zip,
                Comune=stabile_organizzazione.city[:60],
                Nazione=stabile_organizzazione.country_id.code)
            if stabile_organizzazione.province:
                CedentePrestatore.StabileOrganizzazione.Provincia = (
                    stabile_organizzazione.province.code)
        return True

    def _setRea(self, cr, uid, CedentePrestatore, company, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        if company.fatturapa_rea_office and company.fatturapa_rea_number:
            CedentePrestatore.IscrizioneREA = IscrizioneREAType(
                Ufficio=(
                    company.fatturapa_rea_office and
                    company.fatturapa_rea_office.code or None),
                NumeroREA=company.fatturapa_rea_number or None,
                CapitaleSociale=(
                    company.fatturapa_rea_capital and
                    '%.2f' % company.fatturapa_rea_capital or None),
                SocioUnico=(company.fatturapa_rea_partner or None),
                StatoLiquidazione=company.fatturapa_rea_liquidation or 'LN'
            )

    def _setContatti(self, cr, uid, CedentePrestatore,
                     company, context=None):
        if context is None:
            context = {}
        CedentePrestatore.Contatti = ContattiType(
            Telefono=self.checkSetupPhone(company.partner_id.phone) or None,
            Fax=self.checkSetupPhone(company.partner_id.address and company.partner_id.address[0].fax) or None,
            Email=company.partner_id.email or None
        )

    def _setPubAdministrationRef(self, cr, uid, CedentePrestatore,
                                 company, context=None):
        if context is None:
            context = {}
        if company.fatturapa_pub_administration_ref:
            CedentePrestatore.RiferimentoAmministrazione = (
                company.fatturapa_pub_administration_ref)

    def setCedentePrestatore(self, cr, uid, company, fatturapa, context=None):
        fatturapa.FatturaElettronicaHeader.CedentePrestatore = (
            CedentePrestatoreType())
        self._setDatiAnagraficiCedente(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setSedeCedente(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setAlboProfessionaleCedente(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setStabileOrganizzazione(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        # FIXME: add Contacts
        self._setRea(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setContatti(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)
        self._setPubAdministrationRef(
            cr, uid, fatturapa.FatturaElettronicaHeader.CedentePrestatore,
            company, context=context)

    def _setDatiAnagraficiCessionario(
            self, cr, uid, partner, fatturapa, context=None):
        if context is None:
            context = {}
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
            DatiAnagrafici = DatiAnagraficiCessionarioType()

        partner_vat = partner.vat or (partner.parent_id and partner.parent_id.vat)
        fiscal_code = partner.fiscalcode or (partner.parent_id and partner.parent_id.fiscalcode)

        if partner.address:
            for address in partner.address:
                if address.type in ('default', 'invoice'):
                    partner_address = address
                    continue
        else:
            raise orm.except_orm(
                _('Error!'),
                _('No Address find for Partner: {partner}').format(partner=partner.name))

        # is_eu_member = partner_address.country_id.eu_member()
        # if not partner_vat and not fiscal_code and is_eu_member:
        #     raise orm.except_orm(
        #         _('Error!'), _('Partner VAT and Fiscalcode are not set.'))
        # elif not is_eu_member:
        #     partner_vat = partner_address.country_id.code + '99999999999'

        # Not all EU customers has VAT or Fiscalcode
        # Unfortunately this way we disable VAT control for all non EU contries
        if not partner_vat and not fiscal_code and partner_address.country_id.code == 'IT':
            raise orm.except_orm(
                _('Error!'), _('Partner VAT and Fiscalcode are not set.'))
        elif not partner_vat and not fiscal_code:
            partner_vat = partner_address.country_id.code + '99999999999'

        if partner_vat:
            partner_vat = partner_vat.upper()
            if partner_vat[0:2] == 'IT' and not partner_vat[2:].isdigit():
                raise orm.except_orm(
                    _('Error!'),
                    _('Partner VAT \'{vat}\' not correct, is possible that there are same space at the end.').format(
                        vat=partner_vat)
                )
        if fiscal_code:
            fiscal_code = fiscal_code.upper()
            if ' ' in fiscal_code:
                raise orm.except_orm(
                    _('Error!'), _('Fiscalcode \'{fiscal_code}\' not correct, is possible that there are same space at the end.').format(fiscal_code=fiscal_code))
            if len(fiscal_code) not in [11, 16]:
                raise orm.except_orm(
                    _('Error!'), _("Partner FiscalCode \'{fiscal_code}\' lenght not correct.").format(fiscal_code=fiscal_code))
            if len(fiscal_code) == 16:
                chk = codicefiscale.control_code(fiscal_code[0:15])
                if chk != fiscal_code[15]:
                    if fiscal_code != (fiscal_code[0:15] + chk):
                        raise orm.except_orm(
                            _('Error!'),
                            _("Partner FiscalCode \'{fiscal_code}\' is not correct.").format(fiscal_code=fiscal_code))

        if fiscal_code and partner_address and partner_address.country_id.code == 'IT':
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.DatiAnagrafici.CodiceFiscale = fiscal_code or partner_vat[2:]

        if partner_vat:
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(IdPaese=partner_vat[0:2], IdCodice=partner_vat[2:])
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.DatiAnagrafici.Anagrafica = AnagraficaType(
            Denominazione=(partner.parent_id and self.u_normalize(partner.parent_id.name[0:80], lower=False)) or self.u_normalize(partner.name[0:80], lower=False)
        )

        # not using for now
        #
        # Anagrafica = DatiAnagrafici.find('Anagrafica')
        # Nome = Anagrafica.find('Nome')
        # Cognome = Anagrafica.find('Cognome')
        # Titolo = Anagrafica.find('Titolo')
        # Anagrafica.remove(Nome)
        # Anagrafica.remove(Cognome)
        # Anagrafica.remove(Titolo)

        if partner.eori_code:
            fatturapa.FatturaElettronicaHeader.CessionarioCommittente.\
                DatiAnagrafici.Anagrafica.CodEORI = partner.eori_code

        return True

    def _setDatiAnagraficiRappresentanteFiscale(self, partner, fatturapa):
        fatturapa.FatturaElettronicaHeader.RappresentanteFiscale = (
            RappresentanteFiscaleType())
        fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
            DatiAnagrafici = DatiAnagraficiRappresentanteType()
        if not partner.vat and not partner.fiscalcode:
            raise orm.except_orm(
                _('Error!'), _('VAT and Fiscalcode not set for %s') % partner.name)
        if partner.fiscalcode:
            fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
                DatiAnagrafici.CodiceFiscale = partner.fiscalcode
        if partner.vat:
            fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
                DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
                    IdPaese=partner.vat[0:2], IdCodice=partner.vat[2:])
        fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
            DatiAnagrafici.Anagrafica = AnagraficaType(
                Denominazione=partner.name)
        if partner.eori_code:
            fatturapa.FatturaElettronicaHeader.RappresentanteFiscale.\
                DatiAnagrafici.Anagrafica.CodEORI = partner.eori_code

        return True

    def _setTerzoIntermediarioOSoggettoEmittente(self, partner, fatturapa):
        fatturapa.FatturaElettronicaHeader.\
            TerzoIntermediarioOSoggettoEmittente = (
                TerzoIntermediarioSoggettoEmittenteType()
            )
        fatturapa.FatturaElettronicaHeader.\
            TerzoIntermediarioOSoggettoEmittente.\
            DatiAnagrafici = DatiAnagraficiTerzoIntermediarioType()
        if not partner.vat and not partner.fiscalcode:
            raise orm.except_orm(
                _('Error!'), _('Partner VAT and Fiscalcode not set.'))
        if partner.fiscalcode:
            fatturapa.FatturaElettronicaHeader.\
                TerzoIntermediarioOSoggettoEmittente.\
                DatiAnagrafici.CodiceFiscale = partner.fiscalcode
        if partner.vat:
            fatturapa.FatturaElettronicaHeader.\
                TerzoIntermediarioOSoggettoEmittente.\
                DatiAnagrafici.IdFiscaleIVA = IdFiscaleType(
                    IdPaese=partner.vat[0:2], IdCodice=partner.vat[2:])
        fatturapa.FatturaElettronicaHeader.\
            TerzoIntermediarioOSoggettoEmittente.\
            DatiAnagrafici.Anagrafica = AnagraficaType(
                Denominazione=partner.name)
        if partner.eori_code:
            fatturapa.FatturaElettronicaHeader.\
                TerzoIntermediarioOSoggettoEmittente.\
                DatiAnagrafici.Anagrafica.CodEORI = partner.eori_code
        fatturapa.FatturaElettronicaHeader.SoggettoEmittente = 'TZ'
        return True

    def _invoice_address(self, cr, uid, partner, context=None):
        address = self.pool['res.partner'].address_get(cr, uid, [partner.parent_id and partner.parent_id.id or partner.id], ['default', 'invoice'])
        return self.pool['res.partner.address'].browse(cr, uid, address['invoice'] or address['default'], context)

    def _setSedeCessionario(self, cr, uid, partner, fatturapa, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        partner_address = self._invoice_address(cr, uid, partner, context)
        if not partner_address.street:
            raise orm.except_orm(
                _('Error!'), _('Customer street not set.'))

        if not partner_address.city:
            raise orm.except_orm(
                _('Error!'), _('Customer city not set.'))

        if partner_address.country_id:
            Nazione = partner_address.country_id.code
        elif partner_address.province:
            Nazione = partner_address.province.region.country_id.code
        else:
            raise orm.except_orm(
                _('Error!'), _('Customer country not set.'))

        if Nazione == 'IT':
            if not partner_address.zip:
                raise orm.except_orm(
                    _('Error!'), _('Customer ZIP not set.'))
            elif len(partner_address.zip) < 5:
                raise orm.except_orm(
                    _('Error!'), _('Customer ZIP wrong.'))

            if not partner_address.province:
                raise orm.except_orm(
                    _('Error!'), _('Customer province not set.'))
        else:
            partner_address.zip = '00000'
            # if not partner_address.zip:
            #     partner_address.zip = '00000'
            # elif len(partner_address.zip) < 5:
            #     partner_address.zip = '{:0<5s}'.format(partner_address.zip)

        #     if not partner_address.province:
        #         partner_address.province = partner_address.city

        # FIXME: manage address number in <NumeroCivico>
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente.Sede = (
            IndirizzoType(
                Indirizzo=partner_address.street.encode('utf-8').decode('latin1'),
                CAP=partner_address.zip.replace('x', '0').replace(' ', '')[0:5],
                Comune=partner_address.city[:60].encode('utf-8').decode('latin1'),
                Provincia=partner_address.province and partner_address.province.code[0:2] or 'EE', # partner_address.city[0:2].upper().encode('utf-8').decode('latin1')[0:2],
                Nazione=Nazione))

        return True

    def setRappresentanteFiscale(
            self, cr, uid, company, fatturapa, context=None):
        if company.fatturapa_tax_representative:
            # TODO: RappresentanteFiscale should be usefull for foreign
            # companies sending invoices to italian PA only
            raise orm.except_orm(
                _("Error"), _("RappresentanteFiscale not handled"))
            # partner = company.fatturapa_tax_representative

        # DatiAnagrafici = RappresentanteFiscale.find('DatiAnagrafici')

        # if not partner.fiscalcode:
            # raise orm.except_orm(
            # _('Error!'), _('RappresentanteFiscale Partner '
            # 'fiscalcode not set.'))

        # DatiAnagrafici.find('CodiceFiscale').text = partner.fiscalcode

        # if not partner.vat:
            # raise orm.except_orm(
            # _('Error!'), _('RappresentanteFiscale Partner VAT not set.'))
        # DatiAnagrafici.find(
            # 'IdFiscaleIVA/IdPaese').text = partner.vat[0:2]
        # DatiAnagrafici.find(
            # 'IdFiscaleIVA/IdCodice').text = partner.vat[2:]
        # DatiAnagrafici.find('Anagrafica/Denominazione').text = partner.name
        # if partner.eori_code:
            # DatiAnagrafici.find(
            # 'Anagrafica/CodEORI').text = partner.codiceEORI
        return True

    def setCessionarioCommittente(self, cr, uid, partner, fatturapa, context=None):
        fatturapa.FatturaElettronicaHeader.CessionarioCommittente = (
            CessionarioCommittenteType())
        self._setDatiAnagraficiCessionario(cr, uid, partner, fatturapa, context=context)
        self._setSedeCessionario(cr, uid, partner, fatturapa, context=context)

    def setTerzoIntermediarioOSoggettoEmittente(
            self, cr, uid, company, fatturapa, context=None):
        if context is None:
            context = {}

        if company.fatturapa_sender_partner:
            self._setTerzoIntermediarioOSoggettoEmittente(
                company.partner_id, fatturapa)
        return True

    def setSoggettoEmittente(self, cr, uid, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        # FIXME: this record is to be checked invoice by invoice
        # so a control is needed to verify that all invoices are
        # of type CC, TZ or internally created by the company

        # SoggettoEmittente.text = 'CC'
        return True

    def _get_stamp_product_ids(self, cr, uid, company, context):

        stamp_ids = []
        for product in company.product_stamp_ids:
            stamp_ids.append(product.id)
        return stamp_ids

    def setDatiGeneraliDocumento(self, cr, uid, invoice, body, context=None):
        if context is None:
            context = {}

        # TODO DatiSAL

        # TODO DatiDDT

        body.DatiGenerali = DatiGeneraliType()
        if not invoice.number:
            raise orm.except_orm(
                _('Error!'),
                _('Invoice does not have a number.'))

        if invoice.doc_type:
            TipoDocumento = invoice.doc_type.code
        else:
            TipoDocumento = 'TD01'
            if invoice.type == 'out_refund':
                TipoDocumento = 'TD04'

        amount_withholding = 0.0
        for line in invoice.tax_line:
            if line.tax_code_id.notprintable:
                amount_withholding += line.tax_amount
        if amount_withholding != 0.0:
            if invoice.type in ['out_invoice', 'in_invoice']:
                invoice_amount = invoice.amount_total - amount_withholding
            else:
                invoice_amount = invoice.amount_total + amount_withholding
        else:
            invoice_amount = invoice.amount_total

        body.DatiGenerali.DatiGeneraliDocumento = DatiGeneraliDocumentoType(
            TipoDocumento=TipoDocumento,
            Divisa=invoice.currency_id.name,
            Data=invoice.date_invoice,
            Numero=invoice.number,
            ImportoTotaleDocumento='%.2f' % invoice_amount,
        )

        # TODO: DatiBollo,

        # [2.1.1.5] DatiRitenuta
        # wht_code_line = []
        causale_pagamento = ''
        aliquota_ritenuta = 0
        importo_ritenuta = 0
        al_cassa = 0

        for line in invoice.invoice_line:
            for tax in line.invoice_line_tax_id:
                if tax.withholding_tax:
                    # wht_code_line.append(wht.causale_pagamento_id)
                    if causale_pagamento and not causale_pagamento == tax.causale_pagamento_id:
                        raise orm.except_orm(
                            _('Error'),
                            u'Non è possibile esportare una fattura con più aliquote della Ritenuta Acconto'
                        )
                    elif not causale_pagamento:
                        causale_pagamento = tax.causale_pagamento_id
                        aliquota_ritenuta = abs(tax.amount) * 100
                        aliquota_ritenuta_e_invoice = abs(tax.amount_e_invoice) or abs(tax.amount) * 100

                    importo_ritenuta += line.price_subtotal * aliquota_ritenuta / 100
                elif tax.social_security and tax.social_security_type:
                    # DatiCassaPrevidenziale

                    # [2.1.1.7.1] TipoCassa
                    tipo_cassa = tax.social_security_type
                    # [2.1.1.7.2] AlCassa
                    # if line.product_id.cassa_previdenziale_aliquota <= 0:
                    #     raise exceptions.ValidationError("Valore Aliquota Cassa Previdenziale non valido")
                    # else:
                    al_cassa = abs(tax.amount) * 100
                    # [2.1.1.7.3] ImportoContributoCassa
                    # importo_contributo_cassa = line.price_subtotal
                    importo_contributo_cassa = line.price_subtotal * al_cassa / 100
                    # [2.1.1.7.4] ImponibileCassa
                    imponibile_cassa = abs(tax.amount)

                    # aliquota_iva =
                    # ritenuta =
                    natura = tax.non_taxable_nature
                    # riferimento_amministrazione =

                    if natura in ('N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'FC'):
                        iva_cassa_previdenziale = 0.0
                    else:
                        raise orm.except_orm(
                            _('Error'),
                            "Natura del IVA non definita"
                        )

                    # [2.1.1.7] DatiCassaPrevidenziale
                    body.DatiGenerali.DatiGeneraliDocumento.DatiCassaPrevidenziale.append(DatiCassaPrevidenzialeType(
                        TipoCassa=tipo_cassa,
                        AlCassa="%.2f" % round(al_cassa, 2),
                        ImportoContributoCassa="%.2f" % round(importo_contributo_cassa, 2),
                        ImponibileCassa="%.2f" % round(invoice.amount_untaxed, 2),
                        AliquotaIVA="{:.2f}".format(iva_cassa_previdenziale),
                        # Ritenuta=False,
                        Natura=natura,
                        # RiferimentoAmministrazione=False
                    ))

                elif tax.social_security:
                    raise orm.except_orm(
                        _('Error'),
                        "Specificare il tipo di cassa previdenziale"
                    )

        if causale_pagamento:
            # if len(wht_code_line) > 1:
            #     raise orm.except_orm(
            #         'Errore',
            #         u'Non è possibile esportare una fattura con più aliquote della Ritenuta Acconto')

            body.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta = DatiRitenutaType(
                CausalePagamento=causale_pagamento,
                AliquotaRitenuta="%.2f" % round(aliquota_ritenuta_e_invoice, 2),
                ImportoRitenuta="%.2f" % round(importo_ritenuta, 2),
                TipoRitenuta=invoice.partner_id.vat and 'RT02' or 'RT01'
            )

        # [2.1.1.6] DatiBollo
        stamp_ids = self._get_stamp_product_ids(cr, uid, invoice.company_id, context)
        stamp_amount = False
        if stamp_ids:
            for line in invoice.invoice_line:
                if line.product_id and line.product_id.id in stamp_ids:
                    stamp_amount = line.price_subtotal
        else:
            stamp_amount = invoice.stamp_amount  # 2

        if stamp_amount:
            ImportoBollo = '%.2f' % stamp_amount
            DatiBolloType(BolloVirtuale='SI', ImportoBollo=ImportoBollo)
            body.DatiGenerali.DatiGeneraliDocumento.DatiBollo = DatiBolloType(BolloVirtuale='SI', ImportoBollo=ImportoBollo)
            invoice.write({'virtual_stamp': True, 'stamp_amount': stamp_amount})

            #     if line.product_id.electronic_invoice_type_special_product == 1 and line.product_id.special_type_einvoice == 'CP':
            #         FatturaElettronicaBody_DatiGenerali_DatiGeneraliDocumento_DatiCassaPrevidenziale = SubElement(
            #             FatturaElettronicaBody_DatiGenerali_DatiGeneraliDocumento, 'DatiCassaPrevidenziale')

        # 2.1.1.11 Causale
        if invoice.fiscal_position.note:
            caus_list = invoice.fiscal_position.note.split('\n')
            for causale in caus_list:
                # Remove non latin chars, but go back to unicode string,
                # as expected by String200LatinType
                causale = causale.encode('latin', 'ignore').decode('latin')
                body.DatiGenerali.DatiGeneraliDocumento.Causale.append(causale)

        if invoice.fiscal_position.is_tax_exemption and invoice.fiscal_position.number:
            body.DatiGenerali.DatiGeneraliDocumento.Causale.append(u'Numero Dichiarazione: {0}'.format(invoice.fiscal_position.number))

        # ScontoMaggiorazione, ImportoTotaleDocumento, Arrotondamento,

        if invoice.comment:
            # max length of Causale is 200
            comment = invoice.comment.replace('\t', '    ')
            caus_list = self._text_to_array(comment, 200)

            for causale in caus_list:
                # Remove non latin chars, but go back to unicode string,
                # as expected by String200LatinType
                if causale:
                    causale = causale.encode(
                        'latin', 'ignore').decode('latin')
                    body.DatiGenerali.DatiGeneraliDocumento.Causale.append(causale)

        if invoice.company_id.fatturapa_art73:
            body.DatiGenerali.DatiGeneraliDocumento.Art73 = 'SI'

        return True

    def setRelatedDocumentTypes(self, cr, uid, invoice, body,
                                context=None):
        linecount = 1
        for line in invoice.invoice_line:
            for related_document in line.related_documents:
                doc_type = RELATED_DOCUMENT_TYPES[related_document.type]
                documento = DatiDocumentiCorrelatiType()
                if related_document.name:
                    documento.IdDocumento = related_document.name.replace(u'\xb0', u'.')
                if related_document.lineRef:
                    documento.RiferimentoNumeroLinea.append(linecount)
                if related_document.date:
                    documento.Data = related_document.date
                if related_document.numitem:
                    documento.NumItem = related_document.numitem
                if related_document.code:
                    documento.CodiceCommessaConvenzione = related_document.code
                if related_document.cup:
                    documento.CodiceCUP = related_document.cup
                if related_document.cig:
                    documento.CodiceCIG = related_document.cig
                eval(
                    "body.DatiGenerali." +
                    doc_type + ".append(documento)")
            linecount += 1
        for related_document in invoice.related_documents:
            doc_type = RELATED_DOCUMENT_TYPES[related_document.type]
            documento = DatiDocumentiCorrelatiType()
            if related_document.name:
                documento.IdDocumento = related_document.name
            if related_document.date:
                documento.Data = related_document.date
            if related_document.numitem:
                documento.NumItem = related_document.numitem
            if related_document.code:
                documento.CodiceCommessaConvenzione = related_document.code
            if related_document.cup:
                if ' ' in related_document.cup:
                    raise orm.except_orm(_('Error'),
                        _("On invoice {invoice} CUP of id {document_id} have blank space").format(invoice=invoice.number, document_id=related_document.name))
                documento.CodiceCUP = related_document.cup
            if related_document.cig:
                if ' ' in related_document.cig:
                    raise orm.except_orm(_('Error'),
                        _("On invoice {invoice} CIG of id {document_id} have blank space").format(invoice=invoice.number, document_id=related_document.name))
                documento.CodiceCIG = related_document.cig
            eval(
                "body.DatiGenerali." +
                doc_type + ".append(documento)")
        return True

    def get_description(self, cr, uid, ddt_name, order_name, context=None):
        ddt_obj = self.pool['stock.picking']
        ddt_number = []
        ddt_date = []
        carrier = []
        tracking = []

        if ddt_name:
            ddt_ids = ddt_obj.search(cr, uid, [('name', '=', ddt_name)], context=context)
            if len(ddt_ids) == 1:
                ddt = ddt_obj.browse(cr, uid, ddt_ids[0], context)
                if ddt.ddt_number:
                    datetime.strptime(ddt.ddt_date, DEFAULT_SERVER_DATE_FORMAT).strftime("%Y-%m-%d")
                    ddt_number.append(ddt.ddt_number)
                    ddt_date.append(ddt.ddt_date)

                if ddt.carrier_id:
                    carrier.append(ddt.carrier_id.name)
                else:
                    carrier.append('')
                tracking.append(ddt.carrier_tracking_ref or '')

        return [ddt_number, ddt_date, carrier, tracking]

    def AutoSetDati(self, cr, uid, inv, body, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        _logger.info('>>> Order model: {}'.format(self.order_model))
        self.invoice = {}
        keys = {}
        okeys = {}
        picking_obj = self.pool['stock.picking']
        order_model = self.pool[self.order_model]
        sale_orders = {}
        no_tree = False
        for line in inv.invoice_line:
            if line.origin:
                if ':' in line.origin:
                    split_list = line.origin.split(':')
                    ddt, sale_order = split_list[0], split_list[1]
                elif line.origin[:4] == 'OUT/':
                    ddt = line.origin
                    sale_order = False
                elif line.origin[:4] == 'IN/':
                    ddt = False
                    sale_order = False
                else:
                    ddt = False
                    sale_order = line.origin
            else:
                ddt = False
                sale_order = False

            if ddt:
                if ddt in keys:
                    key = keys[ddt]
                else:
                    picking_ids = picking_obj.search(cr, uid, [('name', '=', ddt)], context=context)
                    if picking_ids:
                        picking = picking_obj.browse(cr, uid, picking_ids[0], context=context)
                        key = "{0}_{1}".format(picking.ddt_date, ddt)
                    else:
                        key = ddt
            else:
                key = False

            if sale_order:
                if sale_order not in okeys:
                    sale_order_ids = order_model.search(cr, uid, [('name', '=', sale_order)], context=context)
                    if sale_order_ids:
                        sale = order_model.browse(cr, uid, sale_order_ids[0], context)
                        key = "{0}_{1}".format(sale.date_order, sale.name)
                        sale_orders[key] = {
                            'origin': sale.name.upper(),
                            'customer_ref': sale.client_order_ref,
                            'date': sale.date_order[0:10],
                            'cig': sale.cig,
                            'cup': sale.cup,
                        }

            if key in self.invoice:
                self.invoice[key]['lines'].append(line)
            else:
                [ddt_number, ddt_date, carrier, tracking] = self.get_description(cr, uid, ddt, sale_order, context)
                self.invoice[key] = {
                    'ddt_number': ddt_number,
                    'ddt_date': ddt_date,
                    'carrier': carrier,
                    'tracking': tracking,
                    'lines': [line]
                }

        if not no_tree:

            # for ddt in OrderedDict(sorted(invoice.items(), key=lambda t: t[0])).values():
            #     dati_ddt = DatiDDTType()
            #     if ddt['ddt_number']:
            #         dati_ddt.NumeroDDT = ddt['ddt_number'][0]
            #         dati_ddt.DataDDT = ddt['ddt_date'][0]
            #         body.DatiGenerali.DatiDDT.append(dati_ddt)

            for order in OrderedDict(sorted(sale_orders.items(), key=lambda t: t[0])).values():
                if order['origin']:
                    doc_type = RELATED_DOCUMENT_TYPES['contract']
                    documento = DatiDocumentiCorrelatiType()
                    documento.IdDocumento = order['origin'][:20]
                    documento.Data = order['date']
                    eval("body.DatiGenerali." + doc_type + ".append(documento)")

                if order.get('cig', False) or order.get('cup', False) or inv.cig or inv.cup:
                    doc_type = RELATED_DOCUMENT_TYPES['order']
                    documento = DatiDocumentiCorrelatiType()
                    documento.IdDocumento = self.u_normalize(
                        order['customer_ref'] and order['customer_ref'][0:20] or order['origin'][0:20])
                    documento.Data = order['date']
                    if order.get('cup', False) or inv.cup:
                        documento.CodiceCUP = self.u_normalize(order['cup'] or inv.cup).replace(' ', '')[0:15]
                    if order.get('cig', False) or inv.cig:
                        documento.CodiceCIG = self.u_normalize(order['cig'] or inv.cig).replace(' ', '')[0:15]
                    eval("body.DatiGenerali." + doc_type + ".append(documento)")

        return True

    def setDatiTrasporto(self, cr, uid, invoice, body, context=None):
        if context is None:
            context = {}

        return True

    def setDatiDDT(self, cr, uid, invoice, body):
        return True

    def _get_prezzo_unitario(self, cr, uid, line):
        res = line.price_unit
        if (
            line.invoice_line_tax_id and
            line.invoice_line_tax_id[0].price_include
        ):
            res = line.price_unit / (
                    1 + (line.invoice_line_tax_id[0].amount))
        return res

    def _line_to_array(self, text, size=60):
        text_array = []

        for k in range(0, len(text), size):
            text_array.append(text[k:k+size])
        return text_array

    def _text_to_array(self, text, max_length=60):
        return_description = []
        if text:
            text_latin1 = text.encode('utf-8').decode('latin1')
            for line in text_latin1.split('\n'):
                line = line.strip()
                if len(line) > max_length:
                    return_description += self._line_to_array(line, max_length)
                elif line:
                    return_description.append(line)
        else:
            return_description = ['']
        return return_description

    def _set_AltriDatiGestionali_line(self, cr, uid, DettaglioLinea, line, context):
        if line.origin_document:
            if line.origin_document._name == 'sale.order.line':
                order = line.origin_document.order_id
                order_date = datetime.strptime(order.date_order, DEFAULT_SERVER_DATE_FORMAT)
                if order.client_order_ref:
                    description = u'Rif. Ns. Conferma Ordine {order} del {order_date}, Vs. Ordine {client_order}'.format(
                        order=order.name, order_date=order_date.strftime("%d/%m/%Y"),
                        client_order=order.client_order_ref)
                else:
                    description = u'Rif. Ns. Conferma Ordine {order} del {order_date}'.format(order=order.name, order_date=order_date.strftime("%d/%m/%Y"))

                return_description = self._text_to_array(description, 60)
                for single_line in return_description:
                    AltriDatiGestionali = AltriDatiGestionaliType(TipoDato='GENERICO', RiferimentoTesto=single_line)
                    DettaglioLinea.AltriDatiGestionali.append(AltriDatiGestionali)
        if line.note:
            return_description = self._text_to_array(line.note, 60)
            for single_line in return_description:
                AltriDatiGestionali = AltriDatiGestionaliType(TipoDato='NOTE', RiferimentoTesto=single_line)
                DettaglioLinea.AltriDatiGestionali.append(AltriDatiGestionali)

        return True

    def setDettaglioLinee(self, cr, uid, invoice, body, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)

        body.DatiBeniServizi = DatiBeniServiziType()
        # TipoCessionePrestazione not handled

        # TODO CodiceArticolo

        line_no = 1
        price_precision = max(2, self.pool['decimal.precision'].precision_get(cr, uid, 'Account') + 3)
        uom_precision = max(2, self.pool['decimal.precision'].precision_get(cr, uid, 'Product UoM'))

        product_manufacturer = 'attribute_ids' in self.pool['product.product']._columns
        for ddt in OrderedDict(sorted(self.invoice.items(), key=lambda t: t[0])).values():
            dati_ddt = False
            if ddt['ddt_number']:
                dati_ddt = DatiDDTType()
                dati_ddt.NumeroDDT = ddt['ddt_number'][0]
                dati_ddt.DataDDT = ddt['ddt_date'][0]

            for line in ddt['lines']:
                ritenuta = False
                social_security = False
                if not line.invoice_line_tax_id:
                    raise orm.except_orm(
                        _('Error'),
                        _("Invoice line %s does not have tax") % line.name)
                aliquota = 0.0
                for tax in line.invoice_line_tax_id:
                    if tax.withholding_tax:
                        ritenuta = True
                    elif tax.social_security:
                        social_security = True
                    else:
                        aliquota = abs(tax.amount * 100)

                if len(line.invoice_line_tax_id) > 2 and not (ritenuta or social_security):
                    raise orm.except_orm(
                        _('Error'),
                        _("Too many taxes for invoice line %s") % line.name)

                AliquotaIVA = '%.2f' % aliquota

                prezzo_unitario = self._get_prezzo_unitario(cr, uid, line)
                quantity = line.quantity
                if quantity < 0:
                    quantity = - quantity
                    prezzo_unitario = - prezzo_unitario

                DettaglioLinea = DettaglioLineeType(
                    NumeroLinea=str(line_no),
                    Descrizione=re.compile(r'\[.*\]\ ').sub('', unidecode(line.name)).replace('\n', ' ').replace('\t', ' '),
                    # There is no need to limit digits after .
                    # PrezzoUnitario='%.2f' % line.price_unit,
                    PrezzoUnitario=('%.' + str(
                        price_precision
                    ) + 'f') % prezzo_unitario,
                    Quantita=('%.' + str(
                        uom_precision
                    ) + 'f') % quantity,
                    UnitaMisura=line.uos_id and (
                        unidecode(line.uos_id.name)) or None,
                    PrezzoTotale=('%.' + str(
                        price_precision
                    ) + 'f') % line.price_subtotal,
                    AliquotaIVA=AliquotaIVA)

                if ritenuta:
                    DettaglioLinea.Ritenuta = 'SI'
                # todo CARLO ERRORE VDIF2019/0894
                if False: #line._model._columns.get('string_discount'):
                    if line.string_discount:
                        discount_value = line.string_discount.split("+")
                        for discount_str in discount_value:
                            discount_str = discount_str.replace(',', '.')
                            discount = float(discount_str)
                            tipo_sconto_magggiorazione = TipoScontoMaggiorazioneType(discount > 0 and 'SC' or 'MG')
                            ScontoMaggiorazione = ScontoMaggiorazioneType(
                                Tipo=tipo_sconto_magggiorazione,
                                Percentuale='%.2f' % discount
                            )
                            DettaglioLinea.ScontoMaggiorazione.append(ScontoMaggiorazione)

                elif line.discount != 0.0:
                    tipo_sconto_magggiorazione = TipoScontoMaggiorazioneType(line.discount > 0 and 'SC' or 'MG')
                    ScontoMaggiorazione = ScontoMaggiorazioneType(
                        Tipo=tipo_sconto_magggiorazione,
                        Percentuale='%.2f' % line.discount
                    )
                    DettaglioLinea.ScontoMaggiorazione.append(ScontoMaggiorazione)
                if aliquota == 0.0:
                    if not line.invoice_line_tax_id[0].non_taxable_nature:
                        raise orm.except_orm(
                            _('Error'),
                            _("No 'nature' field for tax %s") %
                            line.invoice_line_tax_id[0].name)
                    DettaglioLinea.Natura = line.invoice_line_tax_id[
                        0
                    ].non_taxable_nature
                if line.admin_ref:
                    DettaglioLinea.RiferimentoAmministrazione = line.admin_ref
                if line.product_id:
                    if line.product_id.default_code:
                        CodiceArticolo = CodiceArticoloType(
                            CodiceTipo=invoice.company_id.name.upper().split(' ')[0].replace('.', ''),
                            CodiceValore=line.product_id.default_code
                        )
                        DettaglioLinea.CodiceArticolo.append(CodiceArticolo)
                    if line.product_id.ean13:
                        CodiceArticolo = CodiceArticoloType(
                            CodiceTipo='EAN',
                            CodiceValore=line.product_id.ean13
                        )
                        DettaglioLinea.CodiceArticolo.append(CodiceArticolo)
                    # product_manufacturer
                    if product_manufacturer:
                        for attribute in line.product_id.attribute_ids:
                            if attribute.value and attribute.name:
                                CodiceArticolo = CodiceArticoloType(
                                    CodiceTipo=attribute.name,
                                    CodiceValore=attribute.value
                                )
                                DettaglioLinea.CodiceArticolo.append(CodiceArticolo)

                self._set_AltriDatiGestionali_line(cr, uid, DettaglioLinea, line, context)

                if dati_ddt:
                    dati_ddt.RiferimentoNumeroLinea.append(line_no)
                line_no += 1

                # not handled

                # el.remove(el.find('DataInizioPeriodo'))
                # el.remove(el.find('DataFinePeriodo'))
                # el.remove(el.find('Ritenuta'))

                body.DatiBeniServizi.DettaglioLinee.append(DettaglioLinea)

            if dati_ddt:
                body.DatiGenerali.DatiDDT.append(dati_ddt)

        return True

    def setDatiRiepilogo(self, cr, uid, invoice, body, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        tax_obj = self.pool['account.tax']
        # patch for find EsigibilitaIVA, normaly is equal for all the tax

        context['type'] = invoice.type

        payability = 'I'
        for tax_line in invoice.tax_line:
            tax_id = self.pool['account.tax'].get_tax_by_invoice_tax(
                cr, uid, tax_line.name, context=context)
            tax = tax_obj.browse(cr, uid, tax_id, context=context)
            if tax.payability and tax.payability != 'I':
                payability = tax.payability

        for tax_line in invoice.tax_line:
            tax_id = tax_obj.get_tax_by_invoice_tax(
                cr, uid, tax_line.name, context=context)
            tax = tax_obj.browse(cr, uid, tax_id, context=context)

            if not tax.tax_code_id.notprintable:

                if tax.non_taxable_nature and tax_line.tax_amount:
                    riepilogo = DatiRiepilogoType(
                        AliquotaIVA='0.00',
                        Natura=tax.non_taxable_nature,
                        ImponibileImporto='%.2f' % abs(tax_line.tax_amount),
                        Imposta='0.00',
                        RiferimentoNormativo=tax.law_reference
                    )
                elif tax.non_taxable_nature:
                    riepilogo = DatiRiepilogoType(
                        AliquotaIVA='0.00',
                        Natura=tax.non_taxable_nature,
                        ImponibileImporto='%.2f' % tax_line.base,
                        Imposta='0.00',
                        RiferimentoNormativo=tax.law_reference
                    )
                else:
                    riepilogo = DatiRiepilogoType(
                        AliquotaIVA='%.2f' % abs(tax.amount * 100),
                        ImponibileImporto='%.2f' % tax_line.base,
                        Imposta='%.2f' % tax_line.amount
                    )

                if tax.amount == 0.0:
                    if not tax.non_taxable_nature:
                        raise orm.except_orm(
                            _('Error'),
                            _("No 'nature' field for tax %s") % tax.name)
                    riepilogo.Natura = tax.non_taxable_nature
                    if not tax.law_reference:
                        raise orm.except_orm(
                            _('Error'),
                            _("No 'law reference' field for tax %s") % tax.name)
                    riepilogo.RiferimentoNormativo = tax.law_reference

                riepilogo.EsigibilitaIVA = payability
                # TODO

                # el.remove(el.find('SpeseAccessorie'))
                # el.remove(el.find('Arrotondamento'))

                body.DatiBeniServizi.DatiRiepilogo.append(riepilogo)

        return True

    def setDatiPagamento(self, cr, uid, invoice, body, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if invoice.payment_term:
            DatiPagamento = DatiPagamentoType()
            if not invoice.payment_term.fatturapa_pt_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Payment term %s does not have a linked e-invoice '
                      'payment term') % invoice.payment_term.name)
            if not invoice.payment_term.fatturapa_pm_id:
                raise orm.except_orm(
                    _('Error'),
                    _('Payment term %s does not have a linked e-invoice '
                      'payment method') % invoice.payment_term.name)
            DatiPagamento.CondizioniPagamento = (
                invoice.payment_term.fatturapa_pt_id.code)
            move_line_pool = self.pool['account.move.line']
            invoice_pool = self.pool['account.invoice']
            payment_line_ids = invoice_pool.move_line_id_payment_get(
                cr, uid, [invoice.id])
            for move_line_id in payment_line_ids:
                move_line = move_line_pool.browse(
                    cr, uid, move_line_id, context=context)
                ImportoPagamento = '%.2f' % move_line.debit

                date_maturity = datetime.strptime(invoice.date_invoice, DEFAULT_SERVER_DATE_FORMAT)
                date_invoice = datetime.strptime(move_line.date_maturity, DEFAULT_SERVER_DATE_FORMAT)
                payment_days = abs((date_maturity - date_invoice).days)

                DettaglioPagamento = DettaglioPagamentoType(
                    ModalitaPagamento=invoice.payment_term.fatturapa_pm_id.code,
                    DataScadenzaPagamento=move_line.date_maturity,
                    DataRiferimentoTerminiPagamento=invoice.date_invoice,
                    GiorniTerminiPagamento=payment_days,
                    ImportoPagamento=ImportoPagamento
                    )
                if invoice.partner_bank_id:
                    DettaglioPagamento.IstitutoFinanziario = (
                        invoice.partner_bank_id.bank_name)
                    if invoice.partner_bank_id.acc_number:
                        DettaglioPagamento.IBAN = (
                            ''.join(
                                invoice.partner_bank_id.acc_number.split()
                            )
                        )
                    if invoice.partner_bank_id.bank_bic:
                        try:
                            DettaglioPagamento.BIC = invoice.partner_bank_id.bank_bic
                        except (SimpleFacetValueError, SimpleTypeValueError) as e:
                            raise orm.except_orm(
                                "Errore nel codice BIC della banca:", "{bic}".format(
                                    bic=invoice.partner_bank_id.bank_bic))
                DatiPagamento.DettaglioPagamento.append(DettaglioPagamento)
            body.DatiPagamento.append(DatiPagamento)
        return True

    def setAttachments(self, cr, uid, invoice, body, context=None):
        # if context is None:
        #     context = {}

        # if invoice.company_id.fatturapa_doc_attachments:
        #     for doc_id in invoice.company_id.fatturapa_doc_attachments:
        #         # Field Attachment is of Base64 type, so data is encoded automatically when put inside
        #         # Our attachments are already Base64 encoded, so we should decode them
        #         AttachDoc = AllegatiType(
        #             NomeAttachment=doc_id.datas_fname,
        #             Attachment=base64.b64decode(doc_id.datas)
        #         )
        #         body.Allegati.append(AttachDoc)

        if invoice.fatturapa_doc_attachments:
            for doc_id in invoice.fatturapa_doc_attachments:
                # Field Attachment is of Base64 type, so data is encoded automatically when put inside
                # Our attachments are already Base64 encoded, so we should decode them
                AttachDoc = AllegatiType(
                    NomeAttachment=doc_id.datas_fname,
                    Attachment=base64.b64decode(doc_id.datas)
                )
                body.Allegati.append(AttachDoc)
        return True

    def setFatturaElettronicaHeader(self, cr, uid, company,
                                    partner, fatturapa, context=None):
        if context is None:
            context = {}
        fatturapa.FatturaElettronicaHeader = (
            FatturaElettronicaHeaderType())
        self.setDatiTrasmissione(cr, uid, company, partner, fatturapa, context=context)
        self.setCedentePrestatore(cr, uid, company, fatturapa, context=context)
        self.setRappresentanteFiscale(cr, uid, company, fatturapa, context=context)
        self.setCessionarioCommittente(cr, uid, partner, fatturapa, context=context)
        self.setTerzoIntermediarioOSoggettoEmittente(cr, uid, company, fatturapa, context=context)
        self.setSoggettoEmittente(cr, uid, context=context)

    def setFatturaElettronicaBody(
        self, cr, uid, inv, FatturaElettronicaBody, context=None
    ):
        if context is None:
            context = {}

        self.setDatiGeneraliDocumento(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setRelatedDocumentTypes(cr, uid, inv, FatturaElettronicaBody,
                                     context=context)

        self.AutoSetDati(cr, uid, inv, FatturaElettronicaBody, context=context)

        self.setDatiTrasporto(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setDettaglioLinee(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setDatiRiepilogo(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setDatiPagamento(
            cr, uid, inv, FatturaElettronicaBody, context=context)
        self.setAttachments(
            cr, uid, inv, FatturaElettronicaBody, context=context)

    def getPartnerId(self, cr, uid, invoices, context=None):
        partner = False
        for invoice in invoices:
            if not partner:
                partner = invoice.partner_id
            if invoice.partner_id != partner:
                raise orm.except_orm(
                    _('Error!'),
                    _('Invoices must belong to the same partner'))

        return partner

    def exportFatturaPA(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        # obj = self.browse(cr, uid, ids[0])
        model_data_obj = self.pool['ir.model.data']
        invoice_obj = self.pool['account.invoice']
        # attachments = self.pool['fatturapa.attachment.out']
        user_obj = self.pool['res.users']
        attachment_ids = []
        invoices_by_partner = self.group_invoices_by_partner(cr, uid, ids, context)
        journal_fattura_pa_ids = self.pool['account.journal'].search(cr, uid, [('fattura_pa', '=', True)], context=context)
        fiscal_position_pa_ids = self.pool['account.fiscal.position'].search(cr, uid, [('fattura_pa', '=', True)], context=context)
        for partner_id in invoices_by_partner:
            invoice_browse_ids = invoices_by_partner[partner_id]
            invoice_ids = [inv.id for inv in invoice_browse_ids]
            partner = self.getPartnerId(cr, uid, invoice_browse_ids, context=context)
            if invoice_obj.search(cr, uid, [('id', 'in', invoice_ids), ('journal_id', 'in', journal_fattura_pa_ids)], context=context):
                fatturapa = FatturaElettronica(versione=FORMATO_TRASMISSIONE_PA)
            elif invoice_obj.search(cr, uid, [('id', 'in', invoice_ids), ('fiscal_position', 'in', fiscal_position_pa_ids)], context=context):
                fatturapa = FatturaElettronica(versione=FORMATO_TRASMISSIONE_PA)
            else:
                fatturapa = FatturaElettronica(versione=FORMATO_TRASMISSIONE_PR)

            company = user_obj.browse(cr, uid, uid).company_id
            context_partner = context.copy()
            context_partner.update({'lang': partner.lang})
            user_obj = self.pool['res.users']

            try:
                self.setFatturaElettronicaHeader(cr, uid, company,
                                                 partner, fatturapa, context=context_partner)
                for inv in invoice_browse_ids:
                    _logger.info('Generating E-Invoice for invoice {}'.format(inv.number))
                    if inv.fatturapa_attachment_out_id:
                        error = _("Invoice %s has E-invoice Export File already") % (
                                inv.number)
                        _logger.error(error)
                        raise orm.except_orm(_("Error"), error)
                    if True:  # obj.report_print_menu:
                        self.generate_attach_report(cr, uid, ids, inv)
                    invoice_body = FatturaElettronicaBodyType()
                    # invoice_obj.preventive_checks(cr, uid, inv.id)
                    self.setFatturaElettronicaBody(
                        cr, uid, inv, invoice_body, context=context_partner)
                    fatturapa.FatturaElettronicaBody.append(invoice_body)
                    # TODO DatiVeicoli
    
                number = self.setProgressivoInvio(cr, uid, fatturapa, context=context)
            except (SimpleFacetValueError, SimpleTypeValueError) as e:
                if len(context['active_ids']) == 1:
                    _logger.error(_("XML SDI validation error"))
                    _logger.error(unicode(e))
                    raise orm.except_orm(
                        _("XML SDI validation error"),
                        (unicode(e)))

            attach_id = self.saveAttachment(cr, uid, fatturapa, number, context=context)
            attachment_ids.append(attach_id)

            for invoice_id in invoice_ids:
                inv = invoice_obj.browse(cr, uid, invoice_id)
                inv.write({'fatturapa_attachment_out_id': attach_id})

        view_rec = model_data_obj.get_object_reference(
            cr, uid, 'l10n_it_fatturapa_out',
            'view_fatturapa_out_attachment_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        action_to_return = {
            'view_type': 'form',
            'name': "Export FatturaPA",
            'res_model': 'fatturapa.attachment.out',
            'type': 'ir.actions.act_window',
            'context': context
        }
        if len(attachment_ids) == 1:
            action_to_return['view_mode'] = 'page'
            action_to_return['res_id'] = attachment_ids[0]
        else:
            action_to_return['view_mode'] = 'tree,page'
            action_to_return['domain'] = [('id', 'in', attachment_ids)]
        return action_to_return

    def generate_attach_report(self, cr, uid, ids, inv):
        attachment_model = self.pool['ir.attachment']
        if not self.pool['fatturapa.attachments'].search(cr, uid, [('invoice_id', '=', inv.id), ('is_pdf_invoice_print', '=', True)]):
            res = self.pool['account.invoice'].print_report(cr, uid, inv.id, 'account.account_invoices')
            data = {'model': 'account.invoice', 'id': inv.id, 'report_type': 'aeroo'}
            res2 = netsvc.Service._services['report.%s' % res['report_name']].create(cr, uid, [inv.id], data, context={})

            filename = u'{0}.{1}'.format(inv.number, res2[1])
            data_attach = {
                'name': filename,
                'datas': base64.b64encode(res2[0]),
                'datas_fname': filename,
                'type': 'binary',
                'res.model': 'account.invoice',
                'res_name': inv.number,
                'res_id': inv.id
            }
            attachment_id = attachment_model.create(cr, uid, data_attach)
            inv.write({
                'fatturapa_doc_attachments': [(0, 0, {
                    'is_pdf_invoice_print': True,
                    'ir_attachment_id': attachment_id,
                    'description': _("Attachment generated by "
                                     "Electronic invoice export")})]
            })
        return True

    def group_invoices_by_partner(self, cr, uid, ids, context={}):
        invoice_ids = context.get('active_ids', [])
        res = {}
        for invoice in self.pool.get('account.invoice').browse(cr, uid, invoice_ids, context):
            if invoice.partner_id.id not in res:
                res[invoice.partner_id.id] = []
            res[invoice.partner_id.id].append(invoice)
        return res
