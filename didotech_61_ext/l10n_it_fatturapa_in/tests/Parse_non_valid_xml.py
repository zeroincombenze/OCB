from lxml import etree
# from lxml import
import xml.etree.ElementTree as ET


def do_nothing(xml):
    root = etree.XML(xml)

    return etree.tostring(root)


def sanitize(xml):
    # parser = etree.XMLParser(attribute_defaults=True)
    parser = etree.XMLParser(recover=True)
    root = etree.fromstring(xml, parser)
    # for prefix, uri in root.nsmap.items():
    #     print root.nsmap[prefix]
    #     # root.nsmap[key] = value.replace(' ', '/')
    #     ET.register_namespace(prefix, uri.replace(' ', '/'))
    #     print root.nsmap[key]

    return etree.tostring(root)


def sanitize2(xml):
    root = ET.fromstring(xml)
    return ET.tostring(root)


if __name__ == '__main__':
    # path = '/Users/andrei/ownCloud/DIDOTECH/Sviluppo/Fattura Elettronica/Legnolandia/8491/it00488410010_07lqp.xml'
    path = '/opt2/IT09633951000_7U7P6.xml'
    # OK:
    # path = '/Users/andrei/Desktop/Test FatturaPA/IT06700500637_00004.xml'

    with open(path, 'r') as xml_file:
        xml = xml_file.read()
        xml = sanitize(xml)
        print xml
        print do_nothing(xml)
