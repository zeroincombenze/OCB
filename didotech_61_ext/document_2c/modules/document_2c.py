# -*- coding: utf-8 -*-
# © 2018 Andrei Levin - Didotech srl (www.didotech.com)

from requests import Session
from zeep import Client
from zeep import helpers
from zeep.transports import Transport
import logging.config
import hashlib
import zipfile
from collections import OrderedDict
import datetime
import ntpath
import StringIO
import base64


logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

INDEX_XML = """<?xml version="1.0"?>
<FileIndice>
    <Id_Azienda Value="{index[Id_Azienda][@Value]}" />
    <Id_Utente Value="{index[Id_Utente][@Value]}" />
    <AnnoArchiviazione Value="{index[AnnoArchiviazione][@Value]}" />
    {document}
</FileIndice>
"""

DOCUMENT_TEMPLATE = """<Documento>
        <NomeFile Value="{index[NomeFile][@Value]}" />
        <PathCompletoFile Value="{index[PathCompletoFile][@Value]}" />
        <NumeroTipologia Value="{index[NumeroTipologia][@Value]}" />
        <Indice1 Value="{index[Indice1][@Value]}" />
        <Indice2 Value="{index[Indice2][@Value]}" />
        <Indice3 Value="{index[Indice3][@Value]}" />
        <Indice4 Value="{index[Indice4][@Value]}" />
        <Indice5 Value="{index[Indice5][@Value]}" />
        <Indice6 Value="{index[Indice6][@Value]}" />
        <Indice7 Value="{index[Indice7][@Value]}" />
        <Indice8 Value="{index[Indice8][@Value]}" />
        <Indice9 Value="{index[Indice9][@Value]}" />
        <Indice10 Value="{index[Indice10][@Value]}" />
        <FullText Value="{index[FullText][@Value]}" />
        <Sostituzione Value="{index[Sostituzione][@Value]}" />
        <MantieniLock Value="{index[MantieniLock][@Value]}" />
        <Cancellare Value="{index[Cancellare][@Value]}" />
        <AnnoArchiviazioneFile Value="{index[AnnoArchiviazioneFile][@Value]}" />
        <PathCartelline>   
           <Path>
             <PathCartellina Value="{index[PathCartelline][Path][PathCartellina][@Value]}" />
             <PathCartellinaSeparator Value="\\" />
             <PathCartellinaVisibilita Value="2" />
           </Path>
        </PathCartelline>
        <AbilitaEspressioneCartellina Value="{index[AbilitaEspressioneCartellina][@Value]}" />
        <AbilitaRinominaFile Value="{index[AbilitaRinominaFile][@Value]}" />
    </Documento>
"""


INDEX_DICT = {
    'FileIndice': {
        'Id_Azienda': '',
        'Id_Utente': '',
        'AnnoArchiviazione': ''
    }
}

DOCUMENT_DICT = {
    'NomeFile': '',
    'PathCompletoFile': '',
    'NumeroTipologia': '',
    'Indice1': '',
    'Indice2': '',
    'Indice3': '',
    'Indice4': '',
    'Indice5': '',
    'Indice6': '',
    'Indice7': '',
    'Indice8': '',
    'Indice9': '',
    'Indice10': '',
    'FullText': '',
    'Sostituzione': '',
    'MantieniLock': '',
    'Cancellare': '',
    'AnnoArchiviazioneFile': '',
    'AbilitaEspressioneCartellina': '',
    'AbilitaRinominaFile': ''
}


class Document(object):
    def __init__(self, name, data=False):
        """
        :param name:
        :param data: base64 encoded file
        """
        self.name = name

        self.year = ''
        self.data = data
        self.dirname = ''
        self.path = ''
        self.index = ""

    def set_index(self, values):
        complete_name = ntpath.join(self.dirname, self.name)
        values['Documento']['NomeFile']['@Value'] = self.name
        values['Documento']['PathCompletoFile']['@Value'] = complete_name
        self.index = values


class SolutionDoc(object):
    def __init__(self, config, dry_run=False):
        self.useralias = config.document_username
        self.password = bytearray(config.document_password, 'utf-8')

        session = Session()
        session.verify = False
        self.transport = Transport(session=session)
        self.client = Client(config.document_host, transport=self.transport, strict=False)

        self.id_azienda = config.document_company_id
        self.id_utente = config.document_user_id

        self.year = datetime.datetime.now().year

        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def get_data(self, document_id):
        zip_doc = self.client.service.SolutionDocRemoteClient_DownloadDocumentoRecuperato(
            self.useralias,
            self.password,
            document_id
        )

        io_doc = StringIO.StringIO()
        io_doc.write(zip_doc)
        zf = zipfile.ZipFile(io_doc)

        for info in zf.infolist():
            self.logger.info('Unzipping file: {}'.format(info.filename))
            data = zf.read(info.filename)
        zf.close()

        return base64.b64encode(data)

    def set_index(self):
        self.archive = StringIO.StringIO()
        self.zf = zipfile.ZipFile(self.archive, mode='w')

        if self.dry_run:
            self.identifier = 'Dry Run'
        else:
            self.identifier = self.client.service.CreatePathFileZip()

        self.dirname = ntpath.dirname(self.identifier)

        self.index = {
            'FileIndice': OrderedDict((
                ('Id_Azienda', {'@Value': self.id_azienda}),
                ('Id_Utente', {'@Value': self.id_utente}),
                ('AnnoArchiviazione', {'@Value': self.year}),
                ('Documento', [])
            ))
        }

        return self.identifier

    @staticmethod
    def base_name(name):
        """
        :param name: file name
        :return: file name without extension
        """
        name = name.rsplit('.', 1)
        return len(name) == 2 and name[0] or name

    def add(self, document):
        document.dirname = self.dirname
        try:
            print 'adding {}'.format(document.name)
            if document.data:
                document_data = base64.b64decode(document.data)
                self.zf.writestr(document.name, document_data)
            else:
                self.zf.write(document.name)
            self.index['FileIndice']['Documento'].append(document.index['Documento'])
        except:
            print 'Error zipping a file {}'.format(document.name)

    def upload_data(self, dry_run=False):
        """
        :param dry_run:
        :return: id of an archived file
        """
        def read_buffer():
            return self.archive.read(chunk_size)

        self.zf.writestr('archiviazione.xml', self.xml)

        self.zf.close()

        chunk_size = 16 * 1024  # 16Kb default
        max_retries = 50

        hash_md5 = hashlib.md5()

        self.archive.seek(0)

        offset = 0
        for buffer in iter(read_buffer, ''):
            retries = 0
            result = False

            print offset
            hash_md5.update(buffer)

            while not result == '0' or retries >= max_retries:
                retries += 1

                if dry_run:
                    result = '0'
                else:
                    result = self.client.service.AppendChunk(self.identifier, buffer, offset)

            if retries >= max_retries:
                raise Exception("Error occurred during upload, too many retries.")

            offset += chunk_size

        hash_zip = [hash_md5.hexdigest().upper()[i:i + 2] for i in range(0, len(hash_md5.hexdigest()), 2)]

        if dry_run:
            hash_result = True
        else:
            hash_result = self.client.service.SolutionDOC_Archiviazione_Internet_TOM_InfoDocumenti(self.identifier, '-'.join(hash_zip))
            if not hash_result[0] == '0':
                self.logger.error(hash_result[0])
                raise Exception(hash_result[0])
            else:
                return hash_result[1]['anyType'][0]['anyType'][1]

        return hash_result

    @property
    def xml(self):
        # Works only in python 3.x
        # return xmltodict.unparse(self.index, pretty=True, short_empty_elements=True)
        # return xmltodict.unparse(self.index, pretty=True)
        index = INDEX_DICT.copy()
        index.update(self.index)

        document = DOCUMENT_DICT.copy()
        document.update(index['FileIndice']['Documento'][0])

        document_xml = DOCUMENT_TEMPLATE.format(index=document)

        return INDEX_XML.format(index=index['FileIndice'], document=document_xml)

    def get_document_types(self):
        result = self.client.service.SolutionScan_GetTipologie(
            self.useralias,
            self.password,
            self.id_azienda
        )
        return result

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, 'zf'):
            self.zf.close()


if __name__ == "__main__":
    from pprint import pprint
    from config import config
    from config import document_values


    # action = 'upload'
    # action = 'get_type'
    # action = 'get_clients'
    action = 'search'
    # action = 'download'

    with SolutionDoc(config, dry_run=False) as archive:
        if action == 'upload':
            data = open('/Users/andrei/tmp/Archive/Catalogo_ADMIRA_2013.pdf', 'r').read()
            # document = Document('Catalogo_ADMIRA_2013.pdf', data=data)
            # data = open('/Users/andrei/Desktop/The_Two_Brothers.pdf', 'r').read()
            document = Document('The_Two_Brothers.pdf', data=data)

            identifier = archive.set_index(document_values)
            print identifier
            archive.add(document)
            print archive.xml
            # result = archive.upload_data(dry_run=True)
            result = archive.upload_data()
            print result
        elif action == 'download_root_folder':
            root_folders = archive.client.service.SolutionScan_GetCartellineRootImpaginate(
                config.document_useralias, config.document_password, 0)

            print root_folders
        elif action == 'get_type':
            document_types = archive.get_document_types()
            types = []
            for type in document_types:
                types.append({
                    'description': type['anyType'][0],
                    'type_id': type['anyType'][1]
                })
                print('{}, {}'.format(type['anyType'][1], type['anyType'][0]))

            for type in types:
                pprint(type)
        elif action == 'get_clients':
            clients = archive.client.service.SolutionScan_GetAziendeUtente(config.document_useralias, config.document_password)
            print clients
        elif action == 'search':
            docs_dataset = archive.client.service.SolutionDocRemoteClient_GetElencoDocumentiRecupero(
                config.document_username,
                config.document_password,
                config.document_company_id,
                '114003',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                'Python.pdf'
            )
            print(docs_dataset)
            # Reply in XML:
            print(archive.transport.response.text)

        elif action == 'download':
            # document_id = '117638'
            document_id = '117682'

            data = archive.get_data(document_id)
            file('/tmp/Remote_file_new.pdf', 'w').write(data)

        elif action == 'info':
            "Usare getAllDocument() (in RESTful) (Vedi SDK Conservazione) che ritorna info del documento"
