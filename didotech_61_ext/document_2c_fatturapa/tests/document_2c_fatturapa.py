# -*- coding: utf-8 -*-
# © 2018 Nicola Gramola - Didotech srl (www.didotech.com)
# © 2019 Andrei Levin - Didotech srl (www.didotech.com)

import StringIO
from requests import Session
from zeep import Client
from zeep.transports import Transport
import logging.config
import zipfile


class FatturaPA_2C(object):
    def __init__(self, config, dry_run=False):
        self.useralias = config.document_username
        self.password = bytearray(config.document_password, 'utf-8')

        session = Session()
        session.verify = False
        self.transport = Transport(session=session)
        self.client = Client(config.document_host, transport=self.transport, strict=False)

        # self.id_azienda = config.document_company_id
        # self.id_utente = config.document_user_id

        self._upload_filename = None

        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

    def upload_data(self, document_name, data, dry_run=False):
        if self._upload_filename:
            # TODO controllare se inviato prima di upload
            return None

        # STEP 1: get file name to upload fatturapa
        self._upload_filename = self.client.service.GetNomeFileZipFatturaPA(
            codiceCliente=self.useralias,
            passwordServizi=self.password
        )

        # STEP 1.1: setup zip file
        archive = StringIO.StringIO()
        zf = zipfile.ZipFile(archive, mode='w')
        zf.writestr(document_name, data)
        zf.close()

        # STEP 2:
        archive.seek(0)
        ret_upload = self.client.service.UploadFileFatturaPA(
            codiceCliente=self.useralias,
            passwordServizi=self.password,
            nomeFile=self._upload_filename,
            buffer=archive.read(),  # zeep fa la conversione in base64 automaticamente
            offset=0
        )

        return ret_upload

    def send_fatturapa(self, dry_run=False):
        if self._upload_filename:
            # STEP 3: send to SDI
            ret_invio = self.client.service.InvioSdiFatturaPA(
                codiceCliente=self.useralias,
                passwordServizi=self.password,
                nomeFile=self._upload_filename,
                rinominaFile=False,
                firmaTerzoIntermediario=True
            )
            return ret_invio
        else:
            return None

    def get_log_fatturapa(self, idsdi=None, filename_2c=None, from_date=None, to_date=None):
        params = {
            'codiceCliente': self.useralias,
            'passwordServizi': self.password,
        }

        if idsdi:
            params['identificativoSdi'] = idsdi
        if filename_2c:
            params['nomeFileZip'] = filename_2c
        if from_date:
            params['Data_Da'] = from_date
        if to_date:
            params['Data_A'] = to_date

        ret_fatturapa = self.client.service.GetLogFatturaPA(**params)

        return ret_fatturapa

    def get_fatturapa(self, idsdi, estrazioneP7M=True):
        params = {
            'codiceCliente': self.useralias,
            'passwordServizi': self.password,
            'idSdi': idsdi,
            'estrazioneP7M': estrazioneP7M
        }

        ## Vecchie API
        # ret_fatturapa = self.client.service.GetFileFatturaPAbyIdSdi(**params)
        # if ret_fatturapa and len(ret_fatturapa) == 2:
        #     datas = ret_fatturapa[1].decode('utf-8-sig').encode('utf-8')
        #     return datas.encode('base64')
        # else:
        #     return None

        ## Nuove API
        ret_fatturapa = self.client.service.GetFileElectronicInvoice(
            paramAuth=dict(
                CustomerCode=self.useralias,
                Password=self.password,
            ),
            paramFileInvoice=dict(
                IdSdi=idsdi,
                ExtractionP7M=True,
            )
        )
        if ret_fatturapa['ResultCode'] == 'Success':
            datas = ret_fatturapa['File'].decode('utf-8-sig').encode('utf-8')
            return datas.encode('base64')
        else:
            return None

    def get_esito_invio(self, idsdi):
        """Esito invio FatturaPA
        """
        ret_esito = self.client.service.GetElectronicInvoiceOutcomes(
            paramAuth=dict(
                CustomerCode=self.useralias,
                Password=self.password,
            ),
            paramFilter=dict(
                # IdInvoice='',
                IdSdi=idsdi,
                # FilenameInvoice='',
                # StatusLegalStorage='Conservato',   # Sconosciuto or DaConservare or VersatoPdV or VersatoRdV or Conservato
                DataFullOutcomes=False
            )
        )
        return ret_esito
