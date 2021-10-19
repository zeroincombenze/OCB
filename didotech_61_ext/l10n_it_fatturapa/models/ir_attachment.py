# -*- coding: utf-8 -*-
#    Copyright (C) 2018-2019 Didotech Srl <http://www.didotech.com>

import logging
import os
import shlex
import subprocess
import xml.etree.ElementTree as etree
from io import BytesIO

import lxml.etree as ET
from openerp.modules.module import get_module_resource
from openerp.osv import fields, orm
from openerp.osv.osv import except_osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class Attachment(orm.Model):
    _inherit = 'ir.attachment'

    # def _get_fattura_elettronica_preview(self, cr, uid, ids, name, unknow_none, context=None):
    #     user = self.pool['res.users'].browse(cr, uid, uid, context)
    #     style_sheet_mode = user.company_id.style_sheet_mode
    #     if style_sheet_mode == 'asso_software':
    #         xsl_path = get_module_resource('l10n_it_fatturapa', 'data', 'FoglioStileAssoSoftware.xsl')
    #     else:
    #         xsl_path = get_module_resource('l10n_it_fatturapa', 'data', 'fatturaordinaria_v1.2.1.xsl')
    #     xslt = ET.parse(xsl_path)
    #     context = context or {}
    #     if isinstance(ids, (int, long)):
    #         ids = [ids]
    #     res = {}
    #     for fatturapa_attachment in self.browse(cr, uid, ids, context):
    #         try:
    #             xml_string = self.get_xml_string(cr, uid, [fatturapa_attachment.id], context=context)
    #             xml_file = BytesIO(xml_string)
    #             recovering_parser = ET.XMLParser(recover=True)
    #             dom = ET.parse(xml_file, parser=recovering_parser)
    #             transform = ET.XSLT(xslt)
    #             newdom = transform(dom)
    #             res[fatturapa_attachment.id] = ET.tostring(newdom, pretty_print=True)
    #         except Exception as e:
    #             res[fatturapa_attachment.id] = ''
    #     return res
    #
    # _columns = {
    #     'xml_preview': fields.function(_get_fattura_elettronica_preview, type="text", string="Preview", method=True),
    # }

    @staticmethod
    def check_file_is_pem(p7m_file):
        file_is_pem = True
        strcmd = (
            'openssl asn1parse  -inform PEM -in %s'
        ) % (p7m_file)
        cmd = shlex.split(strcmd)
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            proc.communicate()
            if proc.wait() != 0:
                file_is_pem = False
        except Exception as e:
            raise except_osv(_('Error'),
                             _('An error with command "openssl asn1parse" occurred: %s') % e.args)
        return file_is_pem

    @staticmethod
    def parse_pem_2_der(pem_file, tmp_der_file):
        strcmd = (
            'openssl asn1parse -in %s -out %s'
        ) % (pem_file, tmp_der_file)
        cmd = shlex.split(strcmd)
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            stdoutdata, stderrdata = proc.communicate()
            if proc.wait() != 0:
                _logger.warning(stdoutdata)
                raise Exception(stderrdata)
        except Exception as e:
            raise except_osv(_('Error'),
                             _('Parsing PEM to DER  file %s') % e.args)
        if not os.path.isfile(tmp_der_file):
            raise except_osv(_('Error'),
                             _('ASN.1 structure is not parsable in DER'))
        return tmp_der_file

    @staticmethod
    def decrypt_to_xml(signed_file, xml_file):
        strcmd = (
            'openssl smime -decrypt -verify -inform'
            ' DER -in %s -noverify -out %s'
        ) % (signed_file, xml_file)
        cmd = shlex.split(strcmd)
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            stdoutdata, stderrdata = proc.communicate()
            if proc.wait() != 0:
                _logger.warning(stdoutdata)
                raise Exception(stderrdata)
        except Exception as e:
            if stderrdata:
                raise except_osv(_('Error'),
                                 _('Signed Xml file %s') % e.args)
            else:
                raise except_osv(_('Error'),
                                 _("""Signed Xml file is not decryptable.
                                 Please decrypt file before uploading it to ERP"""))
        if not os.path.isfile(xml_file):
            raise except_osv(_('Error'),
                             _('Signed Xml file is not decryptable'))
        return xml_file

    @staticmethod
    def remove_additional_namespaces(xml):
        root = etree.fromstring(xml)
        return etree.tostring(root)

    @staticmethod
    def remove_xades_sign(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('Signature') > -1:
                elem.getparent().remove(elem)
                break
        return ET.tostring(root)

    @staticmethod
    def remove_empty_uom(xml):
        root = ET.XML(xml)

        for line in root.find('FatturaElettronicaBody').find('DatiBeniServizi').findall('DettaglioLinee'):
            elem = line.find('UnitaMisura')
            if elem is not None and not elem.text:
                line.remove(elem)

            for altri_dati in line.findall('AltriDatiGestionali'):
                if altri_dati:
                    elem = altri_dati.find('RiferimentoTesto')
                    if elem is not None and not elem.text:
                        altri_dati.remove(elem)
                        # if altri_dati is not None and not altri_dati.text:
                        #     line.remove(altri_dati)

        return ET.tostring(root)

    @staticmethod
    def remove_empty_riferimento_amministrativo(xml):
        root = ET.XML(xml)
        for line in root.find('FatturaElettronicaBody').find('DatiBeniServizi').findall('DettaglioLinee'):
            elem = line.find('RiferimentoAmministrazione')
            if elem is not None and not elem.text:
                line.remove(elem)
        return ET.tostring(root)

    @staticmethod
    def strip_xml_content(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.text is not None:
                elem.text = elem.text.strip()
        return ET.tostring(root)

    @staticmethod
    def remove_empty_attachment(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('Allegati') > -1:
                attachment_elem = elem.find('Attachment')
                if attachment_elem is not None and not attachment_elem.text:
                    elem.getparent().remove(elem)

        return ET.tostring(root)

    @staticmethod
    def remove_empty_id_document(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('DatiOrdineAcquisto') > -1:
                document_elem = elem.find('IdDocumento')
                if document_elem is not None and not document_elem.text:
                    # IdDocument can't be empty
                    document_elem.text = 'IdDocumento'

        return ET.tostring(root)

    @staticmethod
    def set_fake_address(xml):
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('CedentePrestatore') > -1:
                sede_elem = elem.find('Sede')
                address_elem = sede_elem.find('Indirizzo')
                if address_elem is not None and not address_elem.text:
                    address_elem.text = '-'

                municipality_elem = sede_elem.find('Comune')
                if municipality_elem is not None and not municipality_elem.text:
                    municipality_elem.text = '-'

        return ET.tostring(root)

    @staticmethod
    def set_invoice_date_naive(xml):
        # Remove useless timezone info
        root = ET.XML(xml)
        for elem in root.iter('*'):
            if elem.tag.find('DatiGeneraliDocumento') > -1:
                date_elem = elem.find('Data')
                if len(date_elem.text) > 10:
                    date_elem.text = date_elem.text[0:10]

                causal = elem.find('Causale')
                if causal is not None and not causal.text:
                    elem.remove(causal)

        return ET.tostring(root)

    def sanitize(self, xml_string):
        xml_string = self.remove_additional_namespaces(xml_string)
        xml_string = self.remove_xades_sign(xml_string)
        xml_string = self.strip_xml_content(xml_string)
        xml_string = self.remove_empty_uom(xml_string)
        xml_string = self.set_fake_address(xml_string)
        xml_string = self.remove_empty_attachment(xml_string)
        xml_string = self.remove_empty_id_document(xml_string)
        xml_string = self.set_invoice_date_naive(xml_string)
        xml_string = self.remove_empty_riferimento_amministrativo(xml_string)

        return xml_string

    def get_xml_string(self, cr, uid, ids, context=None):
        context = context or {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        xml_string = ''
        for fatturapa_attachment in self.browse(cr, uid, ids, context):
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
                file_is_pem = self.check_file_is_pem(temp_file_name)
    
                # if temp_file_name is a PEM file
                # parse it in a DER file
                if file_is_pem:
                    temp_file_name = self.parse_pem_2_der(
                        temp_file_name, temp_der_file_name)
    
                # decrypt signed DER file in XML readable
                xml_file_name = self.decrypt_to_xml(
                    temp_file_name, xml_file_name)
    
                with open(xml_file_name, 'r') as fatt_file:
                    file_content = fatt_file.read()
                xml_string = file_content
            elif fatturapa_attachment.datas_fname.lower().endswith('.xml'):
                xml_string = fatturapa_attachment.datas.decode('base64')
            break

        xml_string = self.sanitize(xml_string)
        return xml_string
