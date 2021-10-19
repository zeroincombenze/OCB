# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 AgileBG SAGL <http://www.agilebg.com>
#    Copyright (C) 2015 innoviu Srl <http://www.innoviu.com>
#    Copyright (C) 2018-2019 Didotech Srl <http://www.didotech.com>
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
import os
from openerp.osv import orm
from openerp.tools.translate import _
from openerp.osv import fields
import logging

from openerp.addons.l10n_it_ade.bindings import fatturapa_v_1_2 as fatturapa
# from openerp.addons.l10n_it_fatturapa.bindings import fatturapa_v_1_2 as fatturapa
from openerp.addons.base_iban import base_iban
from openerp.osv.osv import except_osv
from openerp.addons.l10n_it_ade.models.account_tax import SOCIAL_SECURITY_TYPE
from collections import defaultdict

_logger = logging.getLogger(__name__)


class WizardImportFatturapa(orm.TransientModel):
    _name = "wizard.import.fatturapa"
    _description = "Import FatturaPA"

    _columns = {
        'e_invoice_detail_level': fields.selection(
            [
                ('0', 'Minimo'),
                # ('1', 'Aliquote'),
                ('2', 'Massimo'),
            ],
            string="Livello di dettaglio Fatture elettroniche",
            help="Livello minimo: La fattura passiva viene creata senza righe; "
                 "sara' l'utente a doverle creare in base a quanto indicato dal "
                 "fornitore nella fattura elettronica\n"
                 # "Livello Aliquote: viene creata una riga fattura per ogni "
                 # "aliquota presente nella fattura elettronica\n"
                 "Livello Massimo: tutte le righe presenti nella fattura "
                 "elettronica vengono create come righe della fattura passiva",
            required=True
        )
    }

    def default_get(self, cr, uid, fields, context=None):
        context = context or {}
        res = super(WizardImportFatturapa, self).default_get(cr, uid, fields, context)
        res['e_invoice_detail_level'] = '2'
        fatturapa_attachment_ids = context.get('active_ids', False)
        fatturapa_attachment_obj = self.pool.get('fatturapa.attachment.in')
        partnerList = []
        for fatturapa_attachment_id in fatturapa_attachment_ids:
            fatturapa_attachment = fatturapa_attachment_obj.browse(cr, uid,
                fatturapa_attachment_id)
            if fatturapa_attachment.in_invoice_ids:
                raise except_osv(_('Error'),
                                 _("File %s is linked to invoices yet") % fatturapa_attachment.name)
            if fatturapa_attachment.xml_supplier_id not in partnerList:
                partnerList.append(fatturapa_attachment.xml_supplier_id)
            if len(partnerList) == 1:
                res['e_invoice_detail_level'] = partnerList[0].e_invoice_detail_level or '2'

        return res

    def CountryByCode(self, cr, uid, CountryCode, context=None):
        country_model = self.pool['res.country']
        return country_model.search(
            cr, uid, [('code', '=', CountryCode)], context=context)

    def ProvinceByCode(self, cr, uid, provinceCode, context=None):
        province_model = self.pool['res.province']
        return province_model.search(
            cr, uid, [('code', '=', provinceCode)], context=context)
        
    def check_partner_base_data(
        self, cr, uid, partner_id, DatiAnagrafici, context=None
    ):
        if context is None:
            context = {}
        context['inconsistencies'] = ''
        partner = self.pool['res.partner'].browse(
            cr, uid, partner_id, context=context)
        if (
            DatiAnagrafici.Anagrafica.Denominazione and
            partner.name != DatiAnagrafici.Anagrafica.Denominazione
        ):
            if context.get('inconsistencies'):
                context['inconsistencies'] += '\n'
            context['inconsistencies'] += (
                _(
                    "DatiAnagrafici.Anagrafica.Denominazione contains \"%s\"."
                    " Your System contains \"%s\""
                )
                % (DatiAnagrafici.Anagrafica.Denominazione, partner.name)
            )
        if DatiAnagrafici.Anagrafica.Nome and partner.fiscalcode_firstname != DatiAnagrafici.Anagrafica.Nome:
            if context.get('inconsistencies'):
                context['inconsistencies'] += '\n'
            context['inconsistencies'] += (
                _(
                    "DatiAnagrafici.Anagrafica.Nome contains \"%s\"."
                    " Your System contains \"%s\""
                )
                % (DatiAnagrafici.Anagrafica.Nome, partner.fiscalcode_firstname)
            )
        if DatiAnagrafici.Anagrafica.Cognome and partner.fiscalcode_surname != DatiAnagrafici.Anagrafica.Cognome:
            if context.get('inconsistencies'):
                context['inconsistencies'] += '\n'
            context['inconsistencies'] += (
                _(
                    "DatiAnagrafici.Anagrafica.Cognome contains \"%s\"."
                    " Your System contains \"%s\""
                )
                % (DatiAnagrafici.Anagrafica.Cognome, partner.fiscalcode_surname)
            )

    def getPartnerBase(self, cr, uid, DatiAnagrafici, address_data, context=None):
        if not DatiAnagrafici:
            return False
        partner_model = self.pool['res.partner']
        cf = DatiAnagrafici.CodiceFiscale or False
        vat = False
        if DatiAnagrafici.IdFiscaleIVA:
            vat = "%s%s" % (
                DatiAnagrafici.IdFiscaleIVA.IdPaese,
                DatiAnagrafici.IdFiscaleIVA.IdCodice
            )
        partner_ids = partner_model.search(
            cr, uid,
            [
                '|',
                ('vat', '=', vat or 0),
                ('fiscalcode', '=', cf or 0),
            ],
            context=context)

        if len(partner_ids) > 1:
            partner_ids = partner_model.search(cr, uid, [('vat', '=', vat)], context=context)

            if len(partner_ids) > 1:
                partner_ids = partner_model.search(cr, uid, [('vat', '=', vat), ('supplier', '=', True)], context=context)

        commercial_partner = False
        if len(partner_ids) > 1:
            for partner in partner_model.browse(
                cr, uid, partner_ids, context=context
            ):
                if (
                    commercial_partner and
                    hasattr(partner, 'commercial_partner_id') and
                    partner.commercial_partner_id.id != commercial_partner
                ):
                    raise orm.except_orm(
                        _('Error !'),
                        _("Two distinct partners with "
                          "Vat %s and Fiscalcode %s already present in db" %
                          (vat, cf))
                        )
                commercial_partner = hasattr(partner, 'commercial_partner_id') and partner.commercial_partner_id.id
        elif not partner_ids:
            if DatiAnagrafici.Anagrafica.Denominazione:
                partner_ids = partner_model.search(
                    cr, uid,
                    [('name', '=', DatiAnagrafici.Anagrafica.Denominazione)],
                    context=context)
            elif (
                DatiAnagrafici.Anagrafica.Nome and
                DatiAnagrafici.Anagrafica.Cognome
            ):
                partner_ids = partner_model.search(
                    cr, uid,
                    [
                        ('fiscalcode_firstname', '=', DatiAnagrafici.Anagrafica.Nome),
                        ('fiscalcode_surname', '=', DatiAnagrafici.Anagrafica.Cognome),
                    ],
                    context=context)

        if partner_ids:
            commercial_partner = partner_ids[0]
            self.check_partner_base_data(
                cr, uid, commercial_partner, DatiAnagrafici, context=context)
            return commercial_partner
        else:
            # partner to be created
            country_id = False
            if DatiAnagrafici.IdFiscaleIVA:
                CountryCode = DatiAnagrafici.IdFiscaleIVA.IdPaese
                country_ids = self.CountryByCode(
                    cr, uid, CountryCode, context=context)
                if country_ids:
                    country_id = country_ids[0]
                else:
                    raise orm.except_orm(
                        _('Error !'),
                        _("Country Code %s not found in system") % CountryCode
                    )

            default_partner_address_vals = self.get_partner_address(cr, uid, address_data)

            vals = {
                'vat': vat,
                'fiscalcode': cf,
                'customer': False,
                'supplier': True,
                'is_company': (
                    DatiAnagrafici.Anagrafica.Denominazione and True or False),
                'eori_code': DatiAnagrafici.Anagrafica.CodEORI or '',
                'country_id': country_id,
                'address': [[0, 0, default_partner_address_vals]]
            }
            if DatiAnagrafici.Anagrafica.Nome:
                vals['firstname'] = DatiAnagrafici.Anagrafica.Nome
            if DatiAnagrafici.Anagrafica.Cognome:
                vals['lastname'] = DatiAnagrafici.Anagrafica.Cognome
            if DatiAnagrafici.Anagrafica.Denominazione:
                vals['name'] = DatiAnagrafici.Anagrafica.Denominazione
            else:
                vals['name'] = DatiAnagrafici.Anagrafica.Cognome + ' ' + DatiAnagrafici.Anagrafica.Nome

            return partner_model.create(cr, uid, vals, context=context)

    def get_partner_address(self, cr, uid, address):
        partner_address_vals = {
            'type': 'default',
            'street': '',
            'city': '',
            'zip': '',
        }

        if address:
            partner_address_vals.update({
                'street': address.Indirizzo,
                'city': address.Comune,
                'zip': address.CAP
            })

        city_vals = self.pool.get('res.partner.address').on_change_city(
            cr, uid, [], partner_address_vals['city'], partner_address_vals['zip']).get('value', {})
        partner_address_vals.update(city_vals)

        return partner_address_vals

    def getCedPrest(self, cr, uid, cedPrest, context=None):
        partner_model = self.pool['res.partner']
        fiscalPosModel = self.pool['fatturapa.fiscal_position']

        partner_id = self.getPartnerBase(cr, uid, cedPrest.DatiAnagrafici, cedPrest.Sede, context=context)

        if partner_id:
            country_ids = self.pool['res.country'].search(
                cr, uid,
                [('code', '=', cedPrest.Sede.Nazione)],
                context=context
            )
            address_vals = {
                'partner_id': partner_id,
                'type': 'default',
                'street': cedPrest.Sede.Indirizzo,
                'zip': cedPrest.Sede.CAP,
                'city': cedPrest.Sede.Comune,
                'country_id': len(country_ids) == 1 and country_ids[0] or None
            }

            if cedPrest.Contatti:
                address_vals.update({
                    'phone': cedPrest.Contatti.Telefono,
                    'email': cedPrest.Contatti.Email,
                    'fax': cedPrest.Contatti.Fax
                })

            partner = partner_model.browse(cr, uid, partner_id, context=context)
            if not partner.address:
                self.pool['res.partner.address'].create(cr, uid, address_vals)

        vals = {
            'register': cedPrest.DatiAnagrafici.AlboProfessionale or ''
        }

        if cedPrest.DatiAnagrafici.ProvinciaAlbo:
            ProvinciaAlbo = cedPrest.DatiAnagrafici.ProvinciaAlbo
            prov_ids = self.ProvinceByCode(
                cr, uid, ProvinciaAlbo, context=context)
            if not prov_ids:
                raise orm.except_orm(
                    _('Error !'),
                    _('ProvinciaAlbo ( %s ) not present in system') %
                    ProvinciaAlbo
                )
            vals['register_province'] = prov_ids[0]

        if cedPrest.Sede.Provincia:
            Provincia = cedPrest.Sede.Provincia
            prov_sede = self.ProvinceByCode(cr, uid, Provincia, context)
            if not prov_sede:
                # self.log_inconsistency
                _logger.warning(
                    _('Provincia ( %s ) not present in system')
                    % Provincia
                )
            else:
                vals['province'] = prov_sede[0]

        vals['register_code'] = (
            cedPrest.DatiAnagrafici.NumeroIscrizioneAlbo)
        vals['register_regdate'] = (
            cedPrest.DatiAnagrafici.DataIscrizioneAlbo)

        if cedPrest.DatiAnagrafici.RegimeFiscale:
            rfPos = cedPrest.DatiAnagrafici.RegimeFiscale
            FiscalPosIds = fiscalPosModel.search(
                cr, uid,
                [('code', '=', rfPos)],
                context=context
            )
            if not FiscalPosIds:
                raise orm.except_orm(
                    _('Error!'),
                    _('RegimeFiscale %s is not present in your system')
                    % rfPos
                )
            else:
                vals['register_fiscalpos'] = FiscalPosIds[0]

        if cedPrest.IscrizioneREA:
            REA = cedPrest.IscrizioneREA
            vals['rea_code'] = REA.NumeroREA
            # office_id = False
            office_ids = self.ProvinceByCode(
                cr, uid, REA.Ufficio, context=context)

            if office_ids:
                office_id = office_ids[0]
                vals['rea_office'] = office_id
                vals['rea_capital'] = REA.CapitaleSociale or 0.0
                vals['rea_member_type'] = REA.SocioUnico or False
                vals['rea_liquidation_state'] = REA.StatoLiquidazione or False
            else:
                _logger.warning(
                    _('REA Office Code ( %s ) is not present in system') %
                    REA.Ufficio
                )

        # todo CARLO CAPIRE SE AGGIORNARE
        # partner_model.write(cr, uid, partner_id, vals, context=context)
        return partner_id

    def getCarrierPartner(self, cr, uid, Carrier, context=None):
        partner_model = self.pool['res.partner']
        try:
            partner_id = self.getPartnerBase(cr, uid, Carrier.DatiAnagraficiVettore, Carrier.DatiAnagraficiVettore.Anagrafica, context)
        except:
            partner_id = False
        # vals = {}
        if partner_id:
            vals = {
                'license_number':
                Carrier.DatiAnagraficiVettore.NumeroLicenzaGuida or '',
            }
            partner_model.write(cr, uid, partner_id, vals, context=context)
        return partner_id

    def _get_nature_tax(self, cr, uid, line, context):
        # if line.Natura == 'N2':
        #     # TODO: non soggette
        #     domain = [
        #         ('type_tax_use', 'in', ('purchase', 'all')),
        #         ('non_taxable_nature', '=', line.Natura),
        #         ('amount', '=', 1.0),
        #     ]
        # el
        if line.Natura == 'N6':
            # Reverse Charge
            domain = [
                ('type_tax_use', 'in', ('purchase', 'all')),
                ('non_taxable_nature', '=', line.Natura),
                ('amount', '=', 1.0),
            ]
        else:
            domain = [
                ('type_tax_use', 'in', ('purchase', 'all')),
                ('non_taxable_nature', '=', line.Natura),
                ('amount', '=', 0.0),
            ]

        account_tax_ids = self.pool['account.tax'].search(cr, uid, domain, context=context)
        if not account_tax_ids:
            if context.get('inconsistencies'):
                context['inconsistencies'] += '\n'
            context['inconsistencies'] += (_('No tax with percentage '
                                             '%s and nature %s found')
                                           % (line.AliquotaIVA, line.Natura))

        return account_tax_ids

    def _prepareInvoiceLine(self, cr, uid, credit_account_id, line, invoice_body, invoice_data, context=None):
        account_tax_model = self.pool['account.tax']
        fiscal_position_model = self.pool['account.fiscal.position']
        # check if a default tax exists and generate def_purchase_tax object
        ir_values = self.pool.get('ir.values')
        # company_id = self.pool.get('res.company')._company_default_get(
        #     cr, uid, 'account.invoice.line', context=context
        # )

        supplier_taxes_ids = ir_values.default_get(cr, uid, ['account_id', 'invoice_line_tax_id'])
        ctx = context.copy()
        ctx['type'] = 'in_invoice'
        retLine = self.pool['account.invoice.line'].default_get(cr, uid, ['account_id', 'invoice_line_tax_id', 'quantity'], ctx)

        product_ids = False
        if line.CodiceArticolo:
            for caline in line.CodiceArticolo:
                product_ids = self.pool['product.product'].search(cr, uid, [('supplier_code', '=', caline.CodiceValore)])
                if product_ids:
                    continue
                product_ids = self.pool['product.product'].search(cr, uid, [('ean13', '=', caline.CodiceValore)])
                if product_ids:
                    continue
                product_ids = self.pool['product.product'].search(cr, uid, [('default_code', '=', caline.CodiceValore)])
        if product_ids:
            retLine['product_id'] = product_ids[0]

        def_purchase_tax = False
        if supplier_taxes_ids:
            def_purchase_tax = account_tax_model.browse(
                cr, uid, supplier_taxes_ids, context=context)[0]

        if float(line.AliquotaIVA) == 0.0 and line.Natura:
            account_tax_ids = self._get_nature_tax(cr, uid, line, context)
            if len(account_tax_ids) > 1 and line.PrezzoTotale > 0:
                message = _('Too many taxes with percentage {} and nature {} found').format(
                    line.AliquotaIVA, line.Natura)
                # raise orm.except_orm(_('Error!'), message)
                if context.get('inconsistencies'):
                    context['inconsistencies'] += '\n {}\n'.format(message)
                else:
                    context['inconsistencies'] = '{}\n'.format(message)

                tax_codes = [tax.description for tax in
                             self.pool['account.tax'].browse(cr, uid, account_tax_ids, context)]
                context['inconsistencies'] += '\n'.join(tax_codes)

                account_tax_ids = [account_tax_ids[0]]
        else:
            res = self.pool['account.invoice.line'].onchange_account_id(
                cr, uid, False,
                retLine.get('product_id', False),
                invoice_data['partner_id'],
                invoice_data['type'],
                invoice_data.get('fiscal_position'),
                credit_account_id)

            if res.get('value', False) and res['value'].get('invoice_line_tax_id', False):
                tax = self.pool['account.tax'].browse(cr, uid, res['value']['invoice_line_tax_id'][0], context)
            else:
                tax = False

            if tax and int(tax.amount * 100000) == int(float(line.AliquotaIVA) * 1000):
                account_tax_ids = res['value']['invoice_line_tax_id']
            elif res.get('value', False) and len(res['value'].get('invoice_line_tax_id', [])) > 1:
                account_tax_ids = res['value']['invoice_line_tax_id']
            else:
                account_tax_ids = account_tax_model.search(
                    cr, uid,
                    [
                        ('type_tax_use', 'in', ('purchase', 'all')),
                        ('amount', '=', float(line.AliquotaIVA) / 100),
                        ('price_include', '=', False),
                        # partially deductible VAT must be set by user
                        ('child_ids', '=', False),
                    ], context=context)

                if not account_tax_ids:
                    if context.get('inconsistencies'):
                        context['inconsistencies'] += '\n'
                    context['inconsistencies'] += (
                            _(
                                'XML contains tax with percentage "%s" '
                                'but it does not exist in your system'
                            ) % line.AliquotaIVA
                    )
                # check if there are multiple taxes with
                # same percentage
                elif len(account_tax_ids) > 1:
                    default_account_tax_ids = self.pool['product.product'].default_get(
                        cr, uid, ['supplier_taxes_id']).get('supplier_taxes_id', False)

                    if default_account_tax_ids:
                        default_account_taxes = self.pool['account.tax'].browse(cr, uid, default_account_tax_ids, context)

                        if 'fiscal_position' in invoice_data:
                            fpos = fiscal_position_model.browse(cr, uid, invoice_data['fiscal_position'], context)
                            default_account_tax_ids = fiscal_position_model.map_tax(cr, uid, fpos, default_account_taxes)

                    if len(default_account_tax_ids) == 1 and default_account_tax_ids[0] in account_tax_ids:
                        account_tax_ids = default_account_tax_ids

                    # just logging because this is an usual case: see split payment
                    _logger.warning(_(
                        "Line '%s': Too many taxes with percentage equals "
                        "to \"%s\"\nfix it if required"
                    ) % (line.Descrizione, line.AliquotaIVA))
                    # if there are multiple taxes with same percentage
                    # and there is a default tax with this percentage,
                    # set taxes list equal to supplier_taxes_id, loaded before
                    if (
                            def_purchase_tax and
                            def_purchase_tax.amount == (float(line.AliquotaIVA) / 100)
                    ):
                        account_tax_ids = supplier_taxes_ids
                    else:
                        account_tax_ids = [account_tax_ids[0]]

        if line.Ritenuta == 'SI' and len(account_tax_ids) == 1:
            withholding_tax = account_tax_model.search(
                cr, uid,
                [
                    ('withholding_tax', '=', True),
                    '|',
                    ('amount', '=', - float(
                        invoice_body.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta.AliquotaRitenuta) / 100),
                    ('amount_e_invoice', '=', float(
                        invoice_body.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta.AliquotaRitenuta))
                ], context=context)

            if withholding_tax and len(withholding_tax) == 1:
                account_tax_ids += withholding_tax
            elif withholding_tax:
                _logger.warning(_(
                    """Too many withholing taxes with amount {}
                    """
                ).format(invoice_body.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta.AliquotaRitenuta))
                account_tax_ids.append(withholding_tax[0])
            else:
                message = _("Please configure withholing taxes")
                raise orm.except_orm(_('Error!'), message)

        retLine.update({
            'name': line.Descrizione,
            'sequence': int(line.NumeroLinea),
        })
        if credit_account_id:
            retLine['account_id'] = credit_account_id
        if account_tax_ids:
            retLine['invoice_line_tax_id'] = [(6, 0, account_tax_ids)]
        if line.PrezzoUnitario:
            retLine['price_unit'] = float(line.PrezzoUnitario)
        if line.Quantita:
            retLine['quantity'] = float(line.Quantita)
        if line.TipoCessionePrestazione:
            retLine['service_type'] = line.TipoCessionePrestazione
        if line.UnitaMisura:
            retLine['ftpa_uom'] = line.UnitaMisura
        if line.DataInizioPeriodo:
            retLine['service_start'] = line.DataInizioPeriodo
        if line.DataFinePeriodo:
            retLine['service_end'] = line.DataFinePeriodo
        if (
            line.PrezzoTotale and line.PrezzoUnitario and line.Quantita and
            line.ScontoMaggiorazione
        ):
            retLine['discount'] = self._computeDiscount(
                cr, uid, line, context=context)
        if line.RiferimentoAmministrazione:
            retLine['admin_ref'] = line.RiferimentoAmministrazione

        return retLine

    def get_line_product(self, cr, uid, line, partner):
        product = None
        supplier_info = self.pool['product.supplierinfo']
        if len(line.CodiceArticolo) == 1:
            supplier_code = line.CodiceArticolo[0].CodiceValore
            supplier_infos = supplier_info.search(cr, uid, [
                ('product_code', '=', supplier_code),
                ('name', '=', partner.id)
            ])
            if supplier_infos:
                products = supplier_infos.mapped('product_id')
                if len(products) == 1:
                    product = products[0]
                else:
                    templates = supplier_infos.mapped('product_tmpl_id')
                    if len(templates) == 1:
                        product = templates.product_variant_ids[0]
        if not product and partner.e_invoice_default_product_id:
            product = partner.e_invoice_default_product_id
        return product

    def adjust_accounting_data(self, cr, uid, product, line_vals, context=None):
        context = context or {}
        if product.product_tmpl_id.property_account_expense_id:
            line_vals['account_id'] = (
                product.product_tmpl_id.property_account_expense_id.id)
        elif (
            product.product_tmpl_id.categ_id.property_account_expense_categ_id
        ):
            line_vals['account_id'] = (
                product.product_tmpl_id.categ_id.
                property_account_expense_categ_id.id
            )
        account = self.pool['account.account'].browse(cr, uid, line_vals['account_id'], context)
        new_tax = None
        if len(product.product_tmpl_id.supplier_taxes_id) == 1:
            new_tax = product.product_tmpl_id.supplier_taxes_id[0]
        elif len(account.tax_ids) == 1:
            new_tax = account.tax_ids[0]
        if new_tax:
            line_tax_id = (
                line_vals.get('invoice_line_tax_ids') and
                line_vals['invoice_line_tax_ids'][0][2][0]
            )
            line_tax = self.pool['account.tax'].browse(cr, uid, line_tax_id)
            if new_tax.id != line_tax_id:
                if new_tax._get_tax_amount() != line_tax._get_tax_amount():
                    if context.get('inconsistencies'):
                        context['inconsistencies'] += '\n'
                    context['inconsistencies'] += (
                        _(
                        "XML contains tax %s. Product %s has tax %s. Using "
                        "the XML one"
                    ) % (line_tax.name, product.name, new_tax.name))
                else:
                    # If product has the same amount of the one in XML,
                    # I use it. Typical case: 22% det 50%
                    line_vals['invoice_line_tax_ids'] = [
                        (6, 0, [new_tax.id])]

    def _prepareRelDocsLine(
        self, cr, uid, invoice_id, line, type, context=None
    ):
        res = []
        lineref = line.RiferimentoNumeroLinea or False
        IdDoc = line.IdDocumento or 'Error'
        Data = line.Data or False
        NumItem = line.NumItem or ''
        Code = line.CodiceCommessaConvenzione or ''
        Cig = line.CodiceCIG or ''
        Cup = line.CodiceCUP or ''
        invoice_lineid = False
        if lineref:
            for numline in lineref:
                invoice_lineid = False
                invoice_line_model = self.pool['account.invoice.line']
                invoice_line_ids = invoice_line_model.search(
                    cr, uid,
                    [
                        ('invoice_id', '=', invoice_id),
                        ('sequence', '=', int(numline)),
                    ], context=context)
                if invoice_line_ids:
                    invoice_lineid = invoice_line_ids[0]
                val = {
                    'type': type,
                    'name': IdDoc,
                    'lineRef': numline,
                    'invoice_line_id': invoice_lineid,
                    'invoice_id': invoice_id,
                    'date': Data,
                    'numitem': NumItem,
                    'code': Code,
                    'cig': Cig,
                    'cup': Cup,
                }
                res.append(val)
        else:
            val = {
                'type': type,
                'name': IdDoc,
                'invoice_line_id': invoice_lineid,
                'invoice_id': invoice_id,
                'date': Data,
                'numitem': NumItem,
                'code': Code,
                'cig': Cig,
                'cup': Cup
            }
            res.append(val)
        return res

    def _prepareWelfareLine(self, cr, uid, invoice_id, line, context=None):
        tipo_cassa = line.TipoCassa or False
        al_cassa = line.AlCassa and (float(line.AlCassa)/100) or None
        importo_contributo_cassa = (
            line.ImportoContributoCassa and
            float(line.ImportoContributoCassa) or None)
        imponibile_cassa = (
            line.ImponibileCassa and float(line.ImponibileCassa) or None)
        aliquota_iva = (
            line.AliquotaIVA and (float(line.AliquotaIVA)/100) or None)
        ritenuta = line.Ritenuta or ''
        natura = line.Natura or False
        riferimento_amministrazione = line.RiferimentoAmministrazione or ''

        if not tipo_cassa:
            raise orm.except_orm(
                _('Error!'),
                _('TipoCassa is not defined ')
            )

        welfare_type_id = self.pool['welfare.fund.type'].search(
            cr, uid,
            [('name', '=', tipo_cassa)],
            context=context
        )

        res = {
            'welfare_rate_tax': al_cassa,
            'welfare_amount_tax': importo_contributo_cassa,
            'welfare_taxable': imponibile_cassa,
            'welfare_Iva_tax': aliquota_iva,
            'subjected_withholding': ritenuta,
            'fund_nature': natura or False,
            'pa_line_code': riferimento_amministrazione,
            'invoice_id': invoice_id,
        }
        if welfare_type_id:
            res['name'] = welfare_type_id[0]
        else:
            raise orm.except_orm(
                _('Error'),
                _('TipoCassa %s is not present in your system') % tipo_cassa)
        return res

    def _prepareDiscRisePriceLine(
            self, cr, uid, id, line, context=None
    ):
        res = []
        Tipo = line.Tipo or False
        Percentuale = line.Percentuale and float(line.Percentuale) or 0.0
        Importo = line.Importo and float(line.Importo) or 0.0
        res = {
            'name': Tipo,
            'percentage': Percentuale,
            'amount': Importo,
            context.get('drtype'): id,
        }

        return res

    def _computeDiscount(
        self, cr, uid, DettaglioLinea, context=None
    ):
        discount = 0
        if float(DettaglioLinea.Quantita):
            line_total = float(DettaglioLinea.PrezzoTotale)
            line_unit = line_total / float(DettaglioLinea.Quantita)
            if float(DettaglioLinea.PrezzoUnitario):
                discount = (
                    1 - (line_unit / float(DettaglioLinea.PrezzoUnitario))
                    ) * 100.0
            else:
                discount = 0
        return discount

    def _addGlobalDiscount(
        self, cr, uid, invoice_id, DatiGeneraliDocumento, context=None):

        ir_values = self.pool.get('ir.values')
        discount = 0.0
        if DatiGeneraliDocumento.ScontoMaggiorazione:
            invoice = self.pool['account.invoice'].browse(
                cr, uid, invoice_id, context=context)
            invoice.button_compute(context=context, set_total=True)

            ctx = context.copy()
            ctx.update({
                'type': invoice.type,
                'partner_id': invoice.partner_id.id
            })

            ctx = context.copy()
            ctx['type'] = 'in_invoice'
            supplier_taxes_ids = ir_values.default_get(cr, uid, ['account_id', 'invoice_line_tax_id'])
            line_vals = self.pool['account.invoice.line'].default_get(cr, uid, ['account_id', 'invoice_line_tax_id'], ctx)

            purchase_journal = self.get_purchase_journal(cr, uid, invoice.company_id, type='purchase', context=context)
            partner = invoice.partner_id

            if partner.e_invoice_default_account_id:
                credit_account_id = partner.e_invoice_default_account_id.id
            else:
                credit_account_id = purchase_journal.default_credit_account_id.id
            if credit_account_id:
                line_vals['account_id'] = credit_account_id

            for DiscRise in DatiGeneraliDocumento.ScontoMaggiorazione:
                if DiscRise.Percentuale:
                    amount = (
                        invoice.amount_total * (
                            float(DiscRise.Percentuale) / 100))
                    if DiscRise.Tipo == 'SC':
                        discount -= amount
                    elif DiscRise.Tipo == 'MG':
                        discount += amount
                elif DiscRise.Importo:
                    if DiscRise.Tipo == 'SC':
                        discount -= float(DiscRise.Importo)
                    elif DiscRise.Tipo == 'MG':
                        discount += float(DiscRise.Importo)
            if discount:
                line_vals.update({
                    'invoice_id': invoice_id,
                    'name': _(
                        _("Global invoice discount from DatiGeneraliDocumento")),
                    'price_unit': discount,
                    'quantity': 1,
                    })
                self.pool['account.invoice.line'].create(cr, uid, line_vals, context=context)
        return True

    def _createPayamentsLine(
        self, cr, uid, payment_id, line, partner_id,
        context=None
    ):
        PaymentModel = self.pool['fatturapa.payment.detail']
        PaymentMethodModel = self.pool['fatturapa.payment_method']
        details = line.DettaglioPagamento or False
        if details:
            for dline in details:
                BankModel = self.pool['res.bank']
                PartnerBankModel = self.pool['res.partner.bank']
                method_id = PaymentMethodModel.search(
                    cr, uid,
                    [('code', '=', dline.ModalitaPagamento)],
                    context=context
                )
                if not method_id:
                    raise orm.except_orm(
                        _('Error!'),
                        _(
                            'ModalitaPagamento %s not defined in your system'
                            % dline.ModalitaPagamento
                        )
                    )
                val = {
                    'recipient': dline.Beneficiario,
                    'fatturapa_pm_id': method_id[0],
                    'payment_term_start':
                    dline.DataRiferimentoTerminiPagamento or False,
                    'payment_days':
                    dline.GiorniTerminiPagamento or 0,
                    'payment_due_date':
                    dline.DataScadenzaPagamento or False,
                    'payment_amount':
                    dline.ImportoPagamento or 0.0,
                    'post_office_code':
                    dline.CodUfficioPostale or '',
                    'recepit_surname':
                    dline.CognomeQuietanzante or '',
                    'recepit_name':
                    dline.NomeQuietanzante or '',
                    'recepit_cf':
                    dline.CFQuietanzante or '',
                    'recepit_title':
                    dline.TitoloQuietanzante or '1',
                    'payment_bank_name':
                    dline.IstitutoFinanziario or '',
                    'payment_bank_iban':
                    dline.IBAN or '',
                    'payment_bank_abi':
                    dline.ABI or '',
                    'payment_bank_cab':
                    dline.CAB or '',
                    'payment_bank_bic':
                    dline.BIC or '',
                    'payment_bank': False,
                    'prepayment_discount':
                    dline.ScontoPagamentoAnticipato or 0.0,
                    'max_payment_date':
                    dline.DataLimitePagamentoAnticipato or False,
                    'penalty_amount':
                    dline.PenalitaPagamentiRitardati or 0.0,
                    'penalty_date':
                    dline.DataDecorrenzaPenale or False,
                    'payment_code':
                    dline.CodicePagamento or '',
                    'payment_data_id': payment_id
                }
                bankid = False
                payment_bank_id = False
                if dline.BIC:
                    bankids = BankModel.search(
                        cr, uid,
                        [('bic', '=', dline.BIC.strip())], context=context
                    )
                    if not bankids:
                        if not dline.IstitutoFinanziario:
                            if context.get('inconsistencies'):
                                context['inconsistencies'] += '\n'
                            context['inconsistencies'] += (
                                _("Name of Bank with BIC \"%s\" is not set."
                                  " Can't create bank") % dline.BIC
                            )
                        else:
                            bankid = BankModel.create(
                                cr, uid,
                                {
                                    'name': dline.IstitutoFinanziario,
                                    'bic': dline.BIC,
                                },
                                context=context
                            )
                    else:
                        bankid = bankids[0]
                if dline.IBAN:
                    SearchDom = [
                        ('state', '=', 'iban'),
                        (
                            'acc_number', '=',
                            base_iban._pretty_iban(dline.IBAN.strip())
                        ),
                        ('partner_id', '=', partner_id),
                    ]
                    payment_bank_id = False
                    payment_bank_ids = PartnerBankModel.search(
                        cr, uid, SearchDom, context=context)
                    if not payment_bank_ids and not bankid:
                        if context.get('inconsistencies'):
                            context['inconsistencies'] += '\n'
                        context['inconsistencies'] += (
                            _(
                                'BIC is required and not exist in Xml\n'
                                'Curr bank data is: \n'
                                'IBAN: %s\n'
                                'Bank Name: %s\n'
                            )
                            % (
                                dline.IBAN.strip() or '',
                                dline.IstitutoFinanziario or ''
                            )
                        )

                    elif not payment_bank_ids and bankid:
                        payment_bank_id = PartnerBankModel.create(
                            cr, uid,
                            {
                                'state': 'iban',
                                'acc_number': dline.IBAN.strip(),
                                'partner_id': partner_id,
                                'bank': bankid,
                                'bank_name': dline.IstitutoFinanziario,
                                'bank_bic': dline.BIC
                            },
                            context=context
                        )
                    if payment_bank_ids:
                        payment_bank_id = payment_bank_ids[0]

                if payment_bank_id:
                    val['payment_bank'] = payment_bank_id
                PaymentModel.create(cr, uid, val, context=context)
        return True

    def get_purchase_journal(self, cr, uid, company, type='purchase', context=None):
        journal_model = self.pool['account.journal']
        journal_ids = journal_model.search(
            cr, uid,
            [
                ('type', '=', type),
                ('company_id', '=', company.id)
            ],
            limit=1, context=context)
        if not journal_ids:
            raise orm.except_orm(
                _('Error!'),
                _(
                    'Define a purchase journal '
                    'for this company: "%s" (id:%d).'
                ) % (company.name, company.id)
            )
        purchase_journal = journal_model.browse(
            cr, uid, journal_ids[0], context=context)
        return purchase_journal

    def _prepare_social_security_line(self, cr, uid, social_security, credit_account_id, context):
        account_tax_model = self.pool['account.tax']
        social_security_type = dict(SOCIAL_SECURITY_TYPE)

        line_values = self.pool['account.invoice.line'].default_get(
            cr, uid, ['account_id', 'invoice_line_tax_id'], context)

        if float(social_security.AliquotaIVA) == 0.0 and social_security.Natura:
            account_tax_ids = self._get_nature_tax(cr, uid, social_security, context)

            if len(account_tax_ids) > 0:
                account_tax_ids = [account_tax_ids[0]]
        else:
            default_account_tax_ids = self.pool['product.product'].default_get(
                cr, uid, ['supplier_taxes_id']).get('supplier_taxes_id', False)
            account_tax_ids = [default_account_tax_ids[0]]

            amount_tax = float(social_security.AlCassa) / 100
            social_taxes = account_tax_model.search(cr, uid, [
                ('amount', '=', amount_tax),
                ('type_tax_use', 'in', ('purchase', 'all')),
                ('parent_id', '!=', False)
            ])

            if social_taxes:
                tax = account_tax_model.browse(cr, uid, social_taxes[0])
                account_tax_ids.append(tax.parent_id.id)

        line_values.update({
            'name': social_security_type[str(social_security.TipoCassa)],
            'price_unit': social_security.ImportoContributoCassa,
            'quantity': 1,
            'invoice_line_tax_id': [(6, 0, account_tax_ids)],
            'account_id': credit_account_id
        })

        return line_values

    def invoiceCreate(
        self, cr, uid, ids, fatt, fatturapa_attachment, FatturaBody,
        partner_id, context=None
    ):
        if context is None:
            context = {}
        wizardObj = self.browse(cr, uid, ids[0])
        partner_model = self.pool['res.partner']
        currency_model = self.pool['res.currency']
        invoice_model = self.pool['account.invoice']
        invoice_line_model = self.pool['account.invoice.line']
        ftpa_doctype_poll = self.pool['fatturapa.document_type']
        DiscRisePriceModel = self.pool['discount.rise.price']
        account_tax_model = self.pool['account.tax']

        company = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id
        partner = partner_model.browse(cr, uid, partner_id, context=context)
        pay_acc_id = partner.property_account_payable.id
        # currency 2.1.1.2
        currency_id = currency_model.search(
            cr, uid,
            [
                (
                    'name', '=',
                    FatturaBody.DatiGenerali.DatiGeneraliDocumento.Divisa
                )
            ],
            context=context)
        if not currency_id:
            raise orm.except_orm(
                _('Error!'),
                _(
                    'No currency found with code %s'
                    % FatturaBody.DatiGenerali.DatiGeneraliDocumento.Divisa
                )
            )

        invoice_line_ids = []
        comment = ''
        # 2.1.1
        docType_id = False
        invtype = 'in_invoice'
        docType = FatturaBody.DatiGenerali.DatiGeneraliDocumento.TipoDocumento
        if docType:
            docType_ids = ftpa_doctype_poll.search(
                cr, uid,
                [('code', '=', docType)],
                context=context
            )
            if docType_ids:
                docType_id = docType_ids[0]
            else:
                raise orm.except_orm(
                    _("Error"),
                    _("tipoDocumento %s not handled")
                    % docType)
            if docType == 'TD04':
                # Nota di Credito
                invtype = 'in_refund'
            # Nota di Debito
            # elif docType == 'TD05':
            #     invtype = 'in_invoice'

        if invtype == 'in_refund':
            purchase_journal = self.get_purchase_journal(cr, uid, company, type='purchase_refund', context=context)
        else:
            purchase_journal = self.get_purchase_journal(cr, uid, company, type='purchase', context=context)

        if partner.e_invoice_default_account_id:
            credit_account_id = partner.e_invoice_default_account_id.id
        else:
            credit_account_id = purchase_journal.default_credit_account_id.id

        # 2.1.1.11
        causLst = FatturaBody.DatiGenerali.DatiGeneraliDocumento.Causale
        if causLst:
            for item in causLst:
                comment += item + '\n'
        # 2.2.1
        e_invoice_line_ids = []
        CodeArts = self.pool['fatturapa.article.code']

        ctx = context.copy()
        ctx.update({
            'type': invtype,
            'partner_id': partner_id
        })
        # amount_line = False
        # line_note = []
        minimal_values = defaultdict(lambda: {
            'line_note': [],
            'amount_line': 0
        })

        invoice_vals = invoice_model.onchange_partner_id(cr, uid, False, invtype, partner_id)
        invoice_data = invoice_vals['value']
        invoice_data.update({
            'partner_id': partner_id,
            'type': invtype
        })
        # default_line_values = invoice_line_model.onchange_account_id(
        #     cr, uid, False, False, partner_id, invtype, invoice_data['fiscal_position'], invoice_data['account_id'])

        for line in FatturaBody.DatiBeniServizi.DettaglioLinee:
            invoice_line_data = self._prepareInvoiceLine(cr, uid, credit_account_id, line, FatturaBody, invoice_data, context=ctx)
            if wizardObj.e_invoice_detail_level == '2':
                invoice_line_id = invoice_line_model.create(cr, uid, invoice_line_data, context=context)
    
                if line.CodiceArticolo:
                    for caline in line.CodiceArticolo:
                        CodeArts.create(
                            cr, uid,
                            {
                                'name': caline.CodiceTipo or '',
                                'code_val': caline.CodiceValore or '',
                                'invoice_line_id': invoice_line_id
                            },
                            context=context
                        )
                if line.ScontoMaggiorazione:
                    ctx['drtype'] = 'invoice_line_id'
                    for DiscRisePriceLine in line.ScontoMaggiorazione:
                        DiscRisePriceVals = self._prepareDiscRisePriceLine(
                            cr, uid, invoice_line_id, DiscRisePriceLine,
                            context=ctx
                        )
                        DiscRisePriceModel.create(cr, uid, DiscRisePriceVals, context=ctx)
                invoice_line_ids.append(invoice_line_id)

            elif wizardObj.e_invoice_detail_level == '0':
                key = line.Natura or line.AliquotaIVA or '-'
                minimal_values[key]['line_note'].append(invoice_line_data['name'])
                minimal_values[key]['amount_line'] += (invoice_line_data['price_unit'] * invoice_line_data.get('quantity', 0.0))
                if 'invoice_line_tax_id' not in minimal_values[key]:
                    minimal_values[key]['invoice_line_tax_id'] = invoice_line_data['invoice_line_tax_id']

            einvoiceline_id = self.create_e_invoice_line(cr, uid, line, context)
            e_invoice_line_ids.append(einvoiceline_id)

        # if wizardObj.e_invoice_detail_level == '0' and amount_line:
        if wizardObj.e_invoice_detail_level == '0' and minimal_values:
            for key, values in minimal_values.items():
                invoice_line_data.update({
                    'note': '\n'.join(values['line_note']),
                    'quantity': 1,
                    'price_unit': values['amount_line'],
                    'name': 'Totale',
                    'invoice_line_tax_id': values['invoice_line_tax_id']
                })
                invoice_line_id = invoice_line_model.create(cr, uid, invoice_line_data, context=context)
                invoice_line_ids.append(invoice_line_id)

        # 2.1.1.7 DatiCassaPrevidenziale
        for social_security in FatturaBody.DatiGenerali.DatiGeneraliDocumento.DatiCassaPrevidenziale:
            if not credit_account_id:
                raise orm.except_orm(
                    'Errore',
                    'Manca l\'impostazione del Conto o dentro il Partner o dentro il Sezionale Acquisti')

            invoice_line_data = self._prepare_social_security_line(cr, uid, social_security, credit_account_id, context)

            if social_security.Ritenuta == 'SI' and len(invoice_line_data['invoice_line_tax_id']):
                withholding_tax = account_tax_model.search(
                    cr, uid,
                    [
                        ('withholding_tax', '=', True),
                        (
                            'amount_e_invoice',
                            '=',
                            float(FatturaBody.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta.AliquotaRitenuta)
                        )
                    ], context=context)

                if not withholding_tax:
                    withholding_tax = account_tax_model.search(
                        cr, uid,
                        [
                            ('withholding_tax', '=', True),
                            ('amount', '=', - float(
                                FatturaBody.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta.AliquotaRitenuta) / 100)
                        ], context=context)

                if withholding_tax:
                    # Enasarco
                    if social_security.TipoCassa == 'TC07':
                        # Add tax to every line in invoice
                        for invoice_line in invoice_line_model.browse(cr, uid, invoice_line_ids, context):
                            invoice_line.write({
                                'invoice_line_tax_id': ([(
                                    6,
                                    0,
                                    [tax.id for tax in invoice_line.invoice_line_tax_id] + withholding_tax)])
                            })
                    else:
                        # Add tax to Cassa Previdenziale
                        invoice_line_data['invoice_line_tax_id'] = ([(
                            6,
                            0,
                            invoice_line_data['invoice_line_tax_id'][0][2] + withholding_tax)])

                    if len(withholding_tax) > 1:
                        _logger.warning(_(
                            """Too many withholing taxes with amount {}
                            """
                        ).format(FatturaBody.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta.AliquotaRitenuta))
                else:
                    message = _("Please configure withholing taxes") + ' ' + FatturaBody.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta.AliquotaRitenuta
                    raise orm.except_orm(_('Error!'), message)

            invoice_line_id = invoice_line_model.create(cr, uid, invoice_line_data, context=context)
            invoice_line_ids.append(invoice_line_id)

        invoice_data.update({
            'doc_type': docType_id,
            'date_invoice':
                FatturaBody.DatiGenerali.DatiGeneraliDocumento.Data,
            'supplier_invoice_number':
                FatturaBody.DatiGenerali.DatiGeneraliDocumento.Numero,
            'sender': fatt.FatturaElettronicaHeader.SoggettoEmittente or False,
            'account_id': pay_acc_id,  # We can get it from onchange_partner_id
            # 'type': invtype,
            # 'partner_id': partner_id,
            'address_invoice_id': partner.address[0].id,
            'currency_id': currency_id[0],
            'journal_id': purchase_journal.id,
            'invoice_line': [(6, 0, invoice_line_ids)],
            # 'origin': xmlData.datiOrdineAcquisto,
            # 'fiscal_position': False,
            # 'payment_term': False,
            'company_id': company.id,
            'fatturapa_attachment_in_id': fatturapa_attachment.id,
            'comment': comment,
            'e_invoice_line_ids': [(6, 0, e_invoice_line_ids)]
        })

        # 2.1.1.5 DatiRitenuta
        Withholding = FatturaBody.DatiGenerali.\
            DatiGeneraliDocumento.DatiRitenuta
        if Withholding:
            invoice_data['withholding_amount'] = Withholding.ImportoRitenuta
            invoice_data['ftpa_withholding_type'] = Withholding.TipoRitenuta
            invoice_data['ftpa_withholding_rate'] = float(
                Withholding.AliquotaRitenuta)/100
            invoice_data['ftpa_withholding_payment_reason'] = Withholding.CausalePagamento

        # 2.1.1.6 DatiBollo
        Stamps = FatturaBody.DatiGenerali.\
            DatiGeneraliDocumento.DatiBollo
        if Stamps:
            invoice_data['virtual_stamp'] = Stamps.BolloVirtuale
            invoice_data['stamp_amount'] = float(Stamps.ImportoBollo)
        invoice_id = invoice_model.create(
            cr, uid, invoice_data, context=context)

        self.add_dati_bollo(cr, uid, 
            invoice_id, FatturaBody.DatiGenerali.DatiGeneraliDocumento)

        self.write_additional_invoice_info(cr, uid, FatturaBody, invoice_id, partner_id, context)

        self._addGlobalDiscount(
            cr, uid, invoice_id,
            FatturaBody.DatiGenerali.DatiGeneraliDocumento, context=context)

        # compute the invoice
        invoice_model.button_compute(
            cr, uid, [invoice_id], context=context,
            set_total=True)

        if ctx['inconsistencies']:
            context['inconsistencies'] = ctx['inconsistencies']
        return invoice_id

    def write_additional_invoice_info(self, cr, uid, FatturaBody, invoice_id, partner_id, context):
        invoice_model = self.pool['account.invoice']
        invoice_line_model = self.pool['account.invoice.line']
        rel_docs_model = self.pool['fatturapa.related_document_type']
        WelfareFundLineModel = self.pool['welfare.fund.data.line']
        DiscRisePriceModel = self.pool['discount.rise.price']
        SalModel = self.pool['faturapa.activity.progress']
        DdTModel = self.pool['fatturapa.related_ddt']
        PaymentDataModel = self.pool['fatturapa.payment.data']
        PaymentTermsModel = self.pool['fatturapa.payment_term']
        SummaryDatasModel = self.pool['faturapa.summary.data']

        # invoice = invoice_model.browse(cr, uid, invoice_id, context=context)
        # 2.1.1.7
        Welfares = FatturaBody.DatiGenerali.\
            DatiGeneraliDocumento.DatiCassaPrevidenziale
        if Welfares:
            for welfareLine in Welfares:
                WelferLineVals = self._prepareWelfareLine(
                    cr, uid, invoice_id, welfareLine, context=context)
                WelfareFundLineModel.create(
                    cr, uid, WelferLineVals, context=context)
        # 2.1.1.8
        DiscountRises = FatturaBody.DatiGenerali.\
            DatiGeneraliDocumento.ScontoMaggiorazione
        if DiscountRises:
            context['drtype'] = 'invoice_id'
            for DiscRisePriceLine in DiscountRises:
                DiscRisePriceVals = self._prepareDiscRisePriceLine(
                    cr, uid, invoice_id, DiscRisePriceLine, context=context)
                DiscRisePriceModel.create(
                    cr, uid, DiscRisePriceVals, context=context)
        # 2.1.2
        relOrders = FatturaBody.DatiGenerali.DatiOrdineAcquisto
        if relOrders:
            for order in relOrders:
                doc_datas = self._prepareRelDocsLine(
                    cr, uid, invoice_id, order, 'order', context=context)
                if doc_datas:
                    for doc_data in doc_datas:
                        rel_docs_model.create(
                            cr, uid, doc_data, context=context)
        # 2.1.3
        relContracts = FatturaBody.DatiGenerali.DatiContratto
        if relContracts:
            for contract in relContracts:
                doc_datas = self._prepareRelDocsLine(
                    cr, uid, invoice_id, contract, 'contract', context=context)
                if doc_datas:
                    for doc_data in doc_datas:
                        rel_docs_model.create(
                            cr, uid, doc_data, context=context)
        # 2.1.4
        relAgreements = FatturaBody.DatiGenerali.DatiConvenzione
        if relAgreements:
            for agreement in relAgreements:
                doc_datas = self._prepareRelDocsLine(
                    cr, uid, invoice_id, agreement,
                    'agreement', context=context)
                if doc_datas:
                    for doc_data in doc_datas:
                        rel_docs_model.create(
                            cr, uid, doc_data, context=context)
        # 2.1.5
        relReceptions = FatturaBody.DatiGenerali.DatiRicezione
        if relReceptions:
            for reception in relReceptions:
                doc_datas = self._prepareRelDocsLine(
                    cr, uid, invoice_id, reception,
                    'reception', context=context)
                if doc_datas:
                    for doc_data in doc_datas:
                        rel_docs_model.create(
                            cr, uid, doc_data, context=context)
        # 2.1.6
        RelInvoices = FatturaBody.DatiGenerali.DatiFattureCollegate
        if RelInvoices:
            for invoice in RelInvoices:
                doc_datas = self._prepareRelDocsLine(
                    cr, uid, invoice_id, invoice, 'invoice', context=context)
                if doc_datas:
                    for doc_data in doc_datas:
                        rel_docs_model.create(
                            cr, uid, doc_data, context=context)
        # 2.1.7
        SalDatas = FatturaBody.DatiGenerali.DatiSAL
        if SalDatas:
            for SalDataLine in SalDatas:
                SalModel.create(
                    cr, uid,
                    {
                        'fatturapa_activity_progress': (
                            SalDataLine.RiferimentoFase or 0),
                        'invoice_id': invoice_id
                    }, context=context
                )
        # 2.1.8
        DdtDatas = FatturaBody.DatiGenerali.DatiDDT
        if DdtDatas:
            for DdtDataLine in DdtDatas:
                if not DdtDataLine.RiferimentoNumeroLinea:
                    DdTModel.create(
                        cr, uid,
                        {
                            'name': DdtDataLine.NumeroDDT or '',
                            'date': DdtDataLine.DataDDT or False,
                            'invoice_id': invoice_id
                        }, context=context
                    )
                else:
                    for numline in DdtDataLine.RiferimentoNumeroLinea:
                        invoice_line_ids = invoice_line_model.search(
                            cr, uid,
                            [
                                ('invoice_id', '=', invoice_id),
                                ('sequence', '=', int(numline)),
                            ], context=context)

                        if invoice_line_ids:
                            invoice_lineid = invoice_line_ids[0]
                        else:
                            invoice_lineid = False
                        DdTModel.create(
                            cr, uid,
                            {
                                'name': DdtDataLine.NumeroDDT or '',
                                'date': DdtDataLine.DataDDT or False,
                                'invoice_id': invoice_id,
                                'invoice_line_id': invoice_lineid
                            }, context=context
                        )
        # 2.1.9
        Delivery = FatturaBody.DatiGenerali.DatiTrasporto
        if Delivery:
            # delivery_id = self.getCarrierPartner(cr, uid, Delivery, context=context)
            delivery_dict = {
                # 'carrier_id': delivery_id,
                'transport_vehicle': Delivery.MezzoTrasporto or '',
                'transport_reason': Delivery.CausaleTrasporto or '',
                'number_items': Delivery.NumeroColli or 0,
                'description': Delivery.Descrizione or '',
                'unit_weight': Delivery.UnitaMisuraPeso or 0.0,
                'gross_weight': Delivery.PesoLordo or 0.0,
                'net_weight': Delivery.PesoNetto or 0.0,
                'pickup_datetime': Delivery.DataOraRitiro or False,
                'transport_date': Delivery.DataInizioTrasporto or False,
                'delivery_datetime': Delivery.DataOraConsegna or False,
                'delivery_address': '',
            }

            if Delivery.IndirizzoResa:
                delivery_dict['delivery_address'] = (
                    u'{0}, {1}\n{2} - {3}\n{4} {5}'.format(
                        Delivery.IndirizzoResa.Indirizzo or '',
                        Delivery.IndirizzoResa.NumeroCivico or '',
                        Delivery.IndirizzoResa.CAP or '',
                        Delivery.IndirizzoResa.Comune or '',
                        Delivery.IndirizzoResa.Provincia or '',
                        Delivery.IndirizzoResa.Nazione or ''
                    )
                )
            if Delivery.TipoResa:
                StockModel = self.pool['stock.incoterms']
                stock_incoterm_id = StockModel.search(
                    cr, uid, [('code', '=', Delivery.TipoResa)],
                    context=context
                )
                if stock_incoterm_id:
                    delivery_dict['incoterm'] = stock_incoterm_id[0]
            invoice_model.write(
                cr, uid, invoice_id, delivery_dict, context=context)
        # 2.2.2
        Summary_datas = FatturaBody.DatiBeniServizi.DatiRiepilogo
        if Summary_datas:
            for summary in Summary_datas:
                summary_line = {
                    'tax_rate': summary.AliquotaIVA or 0.0,
                    'non_taxable_nature': summary.Natura or False,
                    'incidental charges': summary.SpeseAccessorie or 0.0,
                    'rounding': summary.Arrotondamento or 0.0,
                    'amount_untaxed': summary.ImponibileImporto or 0.0,
                    'amount_tax': summary.Imposta or 0.0,
                    'payability': summary.EsigibilitaIVA or False,
                    'law_reference': summary.RiferimentoNormativo or '',
                    'invoice_id': invoice_id
                }
                SummaryDatasModel.create(
                    cr, uid, summary_line, context=context)

        # TODO: 2.1.1.5 DatiRitenuta
        if FatturaBody.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta:
            withholding = FatturaBody.DatiGenerali.DatiGeneraliDocumento.DatiRitenuta

            withholding_values = {
                'type': withholding.TipoRitenuta,
                'amount': withholding.ImportoRitenuta,
                'rate': withholding.AliquotaRitenuta,
                'causal': withholding.CausalePagamento,
                'invoice_id': invoice_id
            }
            self.pool['einvoice.withholding.data'].create(
                cr, uid, withholding_values, context=context)

        # 2.1.10
        ParentInvoice = FatturaBody.DatiGenerali.FatturaPrincipale
        if ParentInvoice:
            parentinv_vals = {
                'related_invoice_code':
                ParentInvoice.NumeroFatturaPrincipale or '',
                'related_invoice_date':
                ParentInvoice.DataFatturaPrincipale or False
            }
            invoice_model.write(
                cr, uid, invoice_id, parentinv_vals, context=context)
        # 2.3
        Vehicle = FatturaBody.DatiVeicoli
        if Vehicle:
            veicle_vals = {
                'vehicle_registration': Vehicle.Data or False,
                'total_travel': Vehicle.TotalePercorso or '',
            }
            invoice_model.write(
                cr, uid, invoice_id, veicle_vals, context=context)
        # 2.4
        PaymentsData = FatturaBody.DatiPagamento
        if PaymentsData:
            for PaymentLine in PaymentsData:
                cond = PaymentLine.CondizioniPagamento or False
                if not cond:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Payment method Code not found in document')
                    )
                # term_id = False
                term_ids = PaymentTermsModel.search(
                    cr, uid, [('code', '=', cond)], context=context)
                if not term_ids:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Payment method Code %s is incorrect') % cond
                    )
                else:
                    term_id = term_ids[0]
                PayDataId = PaymentDataModel.create(
                    cr, uid,
                    {
                        'payment_terms': term_id,
                        'invoice_id': invoice_id
                    },
                    context=context
                )
                self._createPayamentsLine(
                    cr, uid, PayDataId, PaymentLine, partner_id,
                    context=context
                )
        # 2.5
        AttachmentsData = FatturaBody.Allegati
        if AttachmentsData:
            AttachModel = self.pool['fatturapa.attachments']
            for attach in AttachmentsData:
                if not attach.NomeAttachment:
                    raise orm.except_orm(
                        _('Error!'),
                        _('Attachment Name is Required')
                    )
                content = attach.Attachment
                name = attach.NomeAttachment
                _attach_dict = {
                    'name': name,
                    'datas': base64.b64encode(str(content)),
                    'datas_fname': name,
                    'description': attach.DescrizioneAttachment or '',
                    'compression': attach.AlgoritmoCompressione or '',
                    'format': attach.FormatoAttachment or '',
                    'invoice_id': invoice_id,
                }
                AttachModel.create(
                    cr, uid, _attach_dict, context=context)

    def create_e_invoice_line(self, cr, uid, line, context):
        vals = {
            'line_number': int(line.NumeroLinea or 0),
            'service_type': line.TipoCessionePrestazione,
            'name': line.Descrizione,
            'qty': float(line.Quantita or 0),
            'uom': line.UnitaMisura,
            'period_start_date': line.DataInizioPeriodo,
            'period_end_date': line.DataFinePeriodo,
            'unit_price': float(line.PrezzoUnitario or 0),
            'total_price': float(line.PrezzoTotale or 0),
            'tax_amount': float(line.AliquotaIVA or 0),
            'wt_amount': line.Ritenuta,
            'tax_kind': line.Natura,
            'admin_ref': line.RiferimentoAmministrazione,
        }
        einvoiceline_id = self.pool['einvoice.line'].create(cr, uid, vals, context)
        if line.CodiceArticolo:
            for ca_line in line.CodiceArticolo:
                self.pool['fatturapa.article.code'].create(
                    cr, uid,
                    {
                        'name': ca_line.CodiceTipo or '',
                        'code_val': ca_line.CodiceValore or '',
                        'e_invoice_line_id': einvoiceline_id
                    }, context
                )
        if line.ScontoMaggiorazione:
            for DiscRisePriceLine in line.ScontoMaggiorazione:
                DiscRisePriceVals = self._prepareDiscRisePriceLine(
                    cr, uid, einvoiceline_id, DiscRisePriceLine,
                    context={'drtype': 'e_invoice_line_id'}
                )
                self.pool['discount.rise.price'].create(cr, uid, DiscRisePriceVals)
        if line.AltriDatiGestionali:
            for dato in line.AltriDatiGestionali:
                self.pool['einvoice.line.other.data'].create(cr, uid, 
                    {
                        'name': dato.TipoDato,
                        'text_ref': dato.RiferimentoTesto,
                        'num_ref': float(dato.RiferimentoNumero or 0),
                        'date_ref': dato.RiferimentoData,
                        'e_invoice_line_id': einvoiceline_id
                    }, context
                )
        return einvoiceline_id

    def add_dati_bollo(self, cr, uid, invoice, DatiGeneraliDocumento, context=None):
        context = context or {}
        # 2.1.1.6
        Stamps = DatiGeneraliDocumento.DatiBollo
        if Stamps:
            invoice = self.pool['account.invoice'].browse(cr, uid, invoice, context)
            virtual_stamp = Stamps.BolloVirtuale
            stamp_amount = float(Stamps.ImportoBollo)
            if not stamp_amount:
                return False
            invoice.write({'virtual_stamp': virtual_stamp, 'stamp_amount': stamp_amount})

            # if invoice.partner_id.e_invoice_detail_level == '2':
            #     journal = self.get_purchase_journal(cr, uid, invoice.company_id)
            #     credit_account_id = journal.default_credit_account_id.id
            #
            #     if not credit_account_id:
            #         credit_account_id = self.pool['product.product'].default_get(cr, uid, ['property_account_expense'])[
            #                          'property_account_expense'] or \
            #                      self.pool['product.category'].default_get(cr, uid, ['property_account_expense_categ'])[
            #                          'property_account_expense_categ']
            #
            #     line_vals = {
            #         'invoice_id': invoice.id,
            #         'name': _(
            #             "Bollo assolto ai sensi del decreto MEF 17 giugno "
            #             "2014 (art. 6)"
            #         ),
            #         'account_id': credit_account_id,
            #         'price_unit': stamp_amount,
            #         'quantity': 1
            #     }
            #     if invoice.company_id.dati_bollo_product_id:
            #         dati_bollo_product = (
            #             invoice.company_id.dati_bollo_product_id)
            #         line_vals['product_id'] = dati_bollo_product.id
            #         line_vals['name'] = dati_bollo_product.name
            #         self.adjust_accounting_data(
            #             cr, uid,
            #             dati_bollo_product, line_vals, context
            #         )
            #     self.pool['account.invoice.line'].create(cr, uid, line_vals)

    def check_CessionarioCommittente(
        self, cr, uid, company, FatturaElettronicaHeader, context=None
    ):
        if (
            company.partner_id.ipa_code !=
            FatturaElettronicaHeader.DatiTrasmissione.CodiceDestinatario
        ):
            raise orm.except_orm(
                _('Error'),
                _('XML IPA code (%s) different from company IPA code (%s)')
                % (
                    FatturaElettronicaHeader.DatiTrasmissione.
                    CodiceDestinatario, company.partner_id.ipa_code))

    def compute_xml_amount_untaxed(self, cr, uid, DatiRiepilogo, context=None):
        amount_untaxed = 0.0
        for Riepilogo in DatiRiepilogo:
            amount_untaxed += float(Riepilogo.ImponibileImporto)
        return amount_untaxed

    # TODO: Migrare funzione _prepare_generic_line_data

    def check_invoice_amount(
        self, cr, uid, invoice, FatturaElettronicaBody, context=None
    ):
        if context is None:
            context = {}

        invoice.write(
            {
                'check_total': FatturaElettronicaBody.DatiGenerali.
                DatiGeneraliDocumento.ImportoTotaleDocumento
            }, context=context)
        if (
            FatturaElettronicaBody.DatiGenerali.DatiGeneraliDocumento.
            ScontoMaggiorazione and
            FatturaElettronicaBody.DatiGenerali.DatiGeneraliDocumento.
            ImportoTotaleDocumento
        ):
            # assuming that, if someone uses
            # DatiGeneraliDocumento.ScontoMaggiorazione, also fills
            # DatiGeneraliDocumento.ImportoTotaleDocumento
            ImportoTotaleDocumento = float(
                FatturaElettronicaBody.DatiGenerali.DatiGeneraliDocumento.
                ImportoTotaleDocumento)
            if invoice.amount_total != ImportoTotaleDocumento:
                if context.get('inconsistencies'):
                    context['inconsistencies'] += '\n'
                context['inconsistencies'] += (
                    _('Invoice total %s is different from '
                      'ImportoTotaleDocumento %s')
                    % (invoice.amount_total, ImportoTotaleDocumento)
                )
        else:
            # else, we can only check DatiRiepilogo if
            # DatiGeneraliDocumento.ScontoMaggiorazione is not present,
            # because otherwise DatiRiepilogo and openerp invoice total would
            # differ
            amount_untaxed = self.compute_xml_amount_untaxed(
                cr, uid,
                FatturaElettronicaBody.DatiBeniServizi.DatiRiepilogo,
                context=context)
            if invoice.amount_untaxed != amount_untaxed:
                if context.get('inconsistencies'):
                    context['inconsistencies'] += '\n'
                context['inconsistencies'] += (
                    _('Computed amount untaxed %s is different from'
                      ' DatiRiepilogo %s')
                    % (invoice.amount_untaxed, amount_untaxed)
                )

    # def strip_xml_content(self, xml):
    #     root = etree.XML(xml)
    #     for elem in root.iter('*'):
    #         if elem.text is not None:
    #             elem.text = elem.text.strip()
    #     return etree.tostring(root)

    # def remove_xades_sign(self, xml):
    #     root = etree.XML(xml)
    #     for elem in root.iter('*'):
    #         if elem.tag.find('Signature') > -1:
    #             elem.getparent().remove(elem)
    #             break
    #     return etree.tostring(root)

    # def check_file_is_pem(self, p7m_file):
    #     file_is_pem = True
    #     strcmd = (
    #         'openssl asn1parse  -inform PEM -in %s'
    #     ) % (p7m_file)
    #     cmd = shlex.split(strcmd)
    #     try:
    #         proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #         stdoutdata, stderrdata = proc.communicate()
    #         if proc.wait() != 0:
    #             file_is_pem = False
    #     except Exception as e:
    #         raise orm.except_orm(
    #             _('Errore'),
    #             _(
    #                 'Check PEM file %s'
    #             ) % e.args
    #         )
    #     return file_is_pem

    # def parse_pem_2_der(self, pem_file, tmp_der_file):
    #     strcmd = (
    #         'openssl asn1parse -in %s -out %s'
    #     ) % (pem_file, tmp_der_file)
    #     cmd = shlex.split(strcmd)
    #     try:
    #         proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #         stdoutdata, stderrdata = proc.communicate()
    #         if proc.wait() != 0:
    #             _logger.warning(stdoutdata)
    #             raise Exception(stderrdata)
    #     except Exception as e:
    #         raise orm.except_orm(
    #             _('Errore'),
    #             _(
    #                 'Parsing PEM to DER  file %s'
    #             ) % e.args
    #         )
    #     if not os.path.isfile(tmp_der_file):
    #         raise orm.except_orm(
    #             _('Errore'),
    #             _(
    #                 'ASN.1 structure is not parsable in DER'
    #             )
    #         )
    #     return tmp_der_file

    # def decrypt_to_xml(self, signed_file, xml_file):
    #     strcmd = (
    #         'openssl smime -decrypt -verify -inform'
    #         ' DER -in %s -noverify -out %s'
    #     ) % (signed_file, xml_file)
    #     cmd = shlex.split(strcmd)
    #     try:
    #         proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #         stdoutdata, stderrdata = proc.communicate()
    #         if proc.wait() != 0:
    #             _logger.warning(stdoutdata)
    #             raise Exception(stderrdata)
    #     except Exception as e:
    #         raise orm.except_orm(
    #             _('Errore'),
    #             _(
    #                 'Signed Xml file %s'
    #             ) % e.args
    #         )
    #     if not os.path.isfile(xml_file):
    #         raise orm.except_orm(
    #             _('Errore'),
    #             _(
    #                 'Signed Xml file not decryptable'
    #             )
    #         )
    #     return xml_file

    def importFatturaPA(self, cr, uid, ids, context=None):
        if not context:
            context = {}

        fatturapa_attachment_obj = self.pool['fatturapa.attachment.in']
        invoice_model = self.pool['account.invoice']
        attachment_model = self.pool['ir.attachment']

        context['inconsistencies'] = ''
        new_invoices = []

        fatturapa_attachment_ids = context.get('active_ids', False)

        for fatturapa_attachment_id in fatturapa_attachment_ids:
            ctx = context.copy()
            fatturapa_attachment = fatturapa_attachment_obj.browse(
                cr, uid, fatturapa_attachment_id, context=ctx)
            if fatturapa_attachment.in_invoice_ids:
                raise orm.except_orm(
                    _("Error"), _("File is linked to invoices already"))
            # decrypt  p7m file
            if fatturapa_attachment.datas_fname.lower().endswith('.p7m'):
                temp_file_name = (
                    '/tmp/%s' % fatturapa_attachment.datas_fname.lower())
                temp_der_file_name = (
                    '/tmp/%s_tmp' % fatturapa_attachment.datas_fname.lower())
                with open(temp_file_name, 'w') as p7m_file:
                    p7m_file.write(fatturapa_attachment.datas.decode('base64'))
                xml_file_name = os.path.splitext(temp_file_name)[0]

                # check if temp_file_name is a PEM file
                file_is_pem = attachment_model.check_file_is_pem(temp_file_name)

                # if temp_file_name is a PEM file
                # parse it in a DER file
                if file_is_pem:
                    temp_file_name = attachment_model.parse_pem_2_der(
                        temp_file_name, temp_der_file_name)

                # decrypt signed DER file in XML readable
                xml_file_name = attachment_model.decrypt_to_xml(
                    temp_file_name, xml_file_name)

                with open(xml_file_name, 'r') as fatt_file:
                    file_content = fatt_file.read()
                xml_string = file_content
            elif fatturapa_attachment.datas_fname.lower().endswith('.xml'):
                xml_string = fatturapa_attachment.datas.decode('base64')

            # xml_string = attachment_model.remove_additional_namespaces(xml_string)
            # xml_string = attachment_model.remove_empty_uom(xml_string)
            # xml_string = attachment_model.remove_xades_sign(xml_string)
            # xml_string = attachment_model.strip_xml_content(xml_string)
            xml_string = attachment_model.sanitize(xml_string)

            fatt = fatturapa.CreateFromDocument(xml_string)

            if fatt.FatturaElettronicaHeader.CessionarioCommittente.DatiAnagrafici.IdFiscaleIVA:
                vat_country_receiver = fatt.FatturaElettronicaHeader.CessionarioCommittente.DatiAnagrafici.IdFiscaleIVA.IdPaese
                vat_code_receiver = fatt.FatturaElettronicaHeader.CessionarioCommittente.DatiAnagrafici.IdFiscaleIVA.IdCodice

                company_vat = self.pool['res.users'].browse(
                    cr, uid, uid, context=context).company_id.partner_id.vat

                if not company_vat == vat_country_receiver + vat_code_receiver:
                    raise orm.except_orm(
                        'Error',
                        'Stai cercando di caricare una fattura non indirizzata a te'
                    )

            if 'invoice_id' in context and fatt.FatturaElettronicaBody:
                FatturaBody = fatt.FatturaElettronicaBody[0]
                e_invoice_line_ids = []
                for line in FatturaBody.DatiBeniServizi.DettaglioLinee:
                    einvoiceline_id = self.create_e_invoice_line(cr, uid, line, context)
                    e_invoice_line_ids.append(einvoiceline_id)
                # todo Verificare con Andrei
                invoice = self.pool['account.invoice'].browse(cr, uid, context['invoice_id'], context)
                if invoice.fatturapa_attachment_in_id:
                    raise orm.except_orm(
                        _("Error"), _("File is linked to invoices already"))
                invoice.write({
                    'fatturapa_attachment_in_id': fatturapa_attachment.id,
                    'e_invoice_line_ids': [(6, 0, e_invoice_line_ids)],
                    'date_invoice':
                        FatturaBody.DatiGenerali.DatiGeneraliDocumento.Data,
                    'supplier_invoice_number':
                        FatturaBody.DatiGenerali.DatiGeneraliDocumento.Numero,
                })

                self.write_additional_invoice_info(cr, uid, FatturaBody, context['invoice_id'], invoice.partner_id.id, context)
                new_invoices = [context['invoice_id']]
            else:
                cedentePrestatore = fatt.FatturaElettronicaHeader.CedentePrestatore
                # 1.2
                partner_id = self.getCedPrest(
                    cr, uid, cedentePrestatore, context=ctx)
                # 1.3
                TaxRappresentative = fatt.FatturaElettronicaHeader.\
                    RappresentanteFiscale
                # 1.5
                # Intermediary = fatt.FatturaElettronicaHeader.\
                #     TerzoIntermediarioOSoggettoEmittente
                # 2
                for fattura in fatt.FatturaElettronicaBody:
                    # if 'invoice_id' in context:

                    invoice_id = self.invoiceCreate(
                        cr, uid, ids, fatt, fatturapa_attachment, fattura,
                        partner_id, context=ctx)

                    self.set_StabileOrganizzazione(cr, uid, cedentePrestatore, invoice_id)
                    # if TaxRappresentative:
                    #     tax_partner_id = self.getPartnerBase(
                    #         cr, uid, TaxRappresentative.DatiAnagrafici,
                    #         TaxRappresentative.DatiAnagrafici.Anagrafica,
                    #         context=ctx)
                    #     invoice_model.write(
                    #         cr, uid, invoice_id,
                    #         {
                    #             'tax_representative_id': tax_partner_id
                    #         }, context=ctx
                    #     )
                    # if Intermediary:
                    #     Intermediary_id = self.getPartnerBase(
                    #         cr, uid, Intermediary.DatiAnagrafici, Intermediary.Sede, context=ctx)
                    #     invoice_model.write(
                    #         cr, uid, invoice_id,
                    #         {
                    #             'intermediary': Intermediary_id
                    #         }, context=ctx
                    #     )
                    new_invoices.append(invoice_id)
                    invoice = invoice_model.browse(cr, uid, invoice_id, ctx)
                    self.check_invoice_amount(
                        cr, uid, invoice,
                        fattura,
                        context=ctx)

            if ctx.get('inconsistencies'):
                invoice.write(
                    {'inconsistencies': ctx['inconsistencies']},
                    context=ctx)

        action_window = {
                'name': _('Supplier Invoice'),
                'view_type': 'form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'context': {'type': invoice.type, 'journal_type': invoice.journal_id.type}
            }

        mod_obj = self.pool['ir.model.data']
        if len(new_invoices) == 1:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
            res_id = res and res[1] or False
            action_window.update({
                'view_mode': 'form',
                'view_id': [res_id],
                'res_id': new_invoices and new_invoices[0] or False
            })
        else:
            action_window.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', new_invoices)]
            })

        return action_window

    # TODO sul partner?
    def set_StabileOrganizzazione(self, cr, uid, CedentePrestatore, invoice):
        vals = {}
        if CedentePrestatore.StabileOrganizzazione:
            vals['efatt_stabile_organizzazione_indirizzo'] = (
                CedentePrestatore.StabileOrganizzazione.Indirizzo)
            vals['efatt_stabile_organizzazione_civico'] = (
                CedentePrestatore.StabileOrganizzazione.NumeroCivico)
            vals['efatt_stabile_organizzazione_cap'] = (
                CedentePrestatore.StabileOrganizzazione.CAP)
            vals['efatt_stabile_organizzazione_comune'] = (
                CedentePrestatore.StabileOrganizzazione.Comune)
            vals['efatt_stabile_organizzazione_provincia'] = (
                CedentePrestatore.StabileOrganizzazione.Provincia)
            vals['efatt_stabile_organizzazione_nazione'] = (
                CedentePrestatore.StabileOrganizzazione.Nazione)
            self.pool.get('account.invoice').write(cr, uid, invoice, vals)

    def get_invoice_obj(self, cr, uid, fatturapa_attachment):
        xml_string = self.pool['ir.attachment'].get_xml_string(cr, uid, fatturapa_attachment.ir_attachment_id.id)
        return fatturapa.CreateFromDocument(xml_string)
