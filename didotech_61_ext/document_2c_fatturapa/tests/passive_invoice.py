import imp
from pprint import pprint
import datetime

invoice_2c = imp.load_source('document_2c_fatturapa', '../models/document_2c_fatturapa.py')


if __name__ == "__main__":
    class SimpleConfig:
        pass

    config = SimpleConfig()

    # config.document_host = u'https://testfppa.solutiondocondemand.com/CustomerTest/FatturaPassivaPA.svc?wsdl'
    # config.document_username = '0000001Test0001462'
    # Passiva
    # config.document_password = b'F900E8934E6AEA5B3397A5EE96DBB7EA'
    # Attiva:
    # config.document_password = b'F900E8934E6AEA5B3397A5EE96DBB7'

    # config.document_host = u'https://fppa.solutiondocondemand.com/FatturaPassivaPA.svc?wsdl'
    # config.document_username = '0000449'
    # config.document_password = b'5924CE0F1A32C424045C8D7A042F6EDF'

    invoice = invoice_2c.PassiveInvoice_2C(config)

    # TODO: get_last_passive_invoice()

    # invoices = invoice.get_invoices({'DataInizio': datetime.datetime(year=2019, month=1, day=21)})
    invoices = invoice.get_invoices({'DataInizio': datetime.datetime(year=2019, month=1, day=4)})
    # invoices = invoice.get_invoices()

    for invoice in invoices:
        print invoice.DatiFattura.NomeFile, invoice.DatiFattura.IdSdi
        print invoice.FileFattura
