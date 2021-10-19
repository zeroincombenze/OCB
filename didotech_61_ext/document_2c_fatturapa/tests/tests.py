# from document_2c_fatturapa import FatturaPA_2C
import imp

invoice_2c = imp.load_source('document_2c_fatturapa', '../models/document_2c_fatturapa.py')


if __name__ == "__main__":

    class SimpleConfig:
        pass
    config = SimpleConfig()
    # config.document_host = u'https://testfe.solutiondocondemand.com/SolutionDOC_Hub.asmx?wsdl'
    config.document_username = '0000001Test0001462'
    # # config.document_username = 'IT04726150289_DS'
    config.document_password = b'F900E8934E6AEA5B3397A5EE96DBB7EA'
    # config.document_password = b'171B2B7B45E370EFBC50BFBE3101D782'
    # config.document_company_id = '6089'
    # config.document_user_id = '43100'

    # Il Sole:
    # config.document_host = u'https://hubfe.solutiondocondemand.com/SolutionDOC_Hub.asmx?wsdl'
    # config.document_username = '0000449A0143905'
    # config.document_password = b'A016F6931CBB05FD2BE4726CEFB6400A'

    nomefile = 'IT04726150289_00085.xml'
    fpa = invoice_2c.FatturaPA_2C(config)

    # print fpa.upload_data(nomefile, open('./local_addons/document_2c_fatturapa/tests/' + nomefile, 'r').read())
    # print fpa.upload_data(nomefile, open(nomefile, 'r').read())
    # # Z:\TempServizi\Cliente_22430\FatturaElettronica\20180612_144553_87339236-0068-45c1-bd9e-4f2a40f685bc.zip
    #
    # #print fpa.send_fatturapa()
    # print fpa.send_fatturapa(email=['andrei.levin@didotech.com'])

    # ['1247863', '12/06/2018 14.45.55', ['None']]

    # print fpa.get_fatturapa('1294191')

    # print fpa.get_esito_invio('1274351')  # AT
    # print fpa.get_esito_invio('1274349')  # AT
    # print fpa.get_esito_invio('1294175')
    # print fpa.get_esito_invio('10062008')
    # print fpa.send_email('10062008', 'andrei.levin@didotech.com')


    # Il Sole -> Didotech:
    # id_sdi = '237126098'
    # email = 'mario@rossi.it'
    # print fpa.send_email(id_sdi)
