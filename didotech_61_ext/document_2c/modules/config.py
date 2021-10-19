from collections import OrderedDict
import datetime


class SimpleConfig:
    pass


config = SimpleConfig()
config.document_host = u'https://demosaas.solutiondocondemand.com/SolutionDOC/Service_SolutionDOC_Main.asmx?wsdl'
config.document_username = 'IT04726150289_DS'
config.document_password = u'171B2B7B45E370EFBC50BFBE3101D782'
config.document_company_id = '6089'
config.document_user_id = '43100'


document_type = '113992'

document_values = {'Documento': OrderedDict((
    ("NomeFile", {'@Value': ""}),
    ("PathCompletoFile", {'@Value': ""}),
    ("NumeroTipologia", {'@Value': document_type}),
    ("Indice1", {'@Value': datetime.datetime.now().strftime("%d/%m/%Y")}),
    ("Indice2", {'@Value': ""}),
    ("Indice3", {'@Value': "PDF"}),
    ("Indice4", {'@Value': ""}),
    ("Indice5", {'@Value': ""}),
    ("Indice6", {'@Value': ""}),
    ("Indice7", {'@Value': ""}),
    ("Indice8", {'@Value': ""}),
    ("Indice9", {'@Value': ""}),
    ("Indice10", {'@Value': ""}),
    ("FullText", {'@Value': ""}),
    ("Sostituzione", {'@Value': "0"}),
    ("MantieniLock", {'@Value': "0"}),
    ("Cancellare", {'@Value': "1"}),
    ("AnnoArchiviazioneFile", {'@Value': datetime.datetime.now().year}),
    ("AbilitaEspressioneCartellina", {'@Value': "0"}),
    ("AbilitaRinominaFile", {'@Value': "0"}),
    ("PathCartelline", {"Path": {
        "PathCartellina": {'@Value': "{year}/{client}".format(
            year=datetime.datetime.now().year, client='vari'
        )}
    }})
))}
