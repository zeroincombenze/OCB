# -*- encoding: utf-8 -*-
#
##############################################################################
#
#    Copyright (c) 2012 - 2017 Andrei Levin (andrei at lanart.it)
#
#                              All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
# based on product_metel_import by Marco Tosato
#

import logging
import math
import threading
from datetime import datetime

import pooler
from openerp.osv import orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from tools.translate import _
from openerp.addons.core_extended.file_manipulation import import_sheet

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# DEBUG = True
DEBUG = False

if DEBUG:
    import pdb


class ImportPricelist(threading.Thread):
    def __init__(self, cr, uid, ids, context):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)

        # Inizializzazione classe ImportPricelist
        self.uid = uid

        self.dbname = cr.dbname
        self.pool = pooler.get_pool(cr.dbname)
        self.start_time = datetime.now()
        self.newSequence = {}
        self.product_obj = self.pool['product.product']

        # Necessario creare un nuovo cursor per il thread,
        # quello fornito dal metodo chiamante viene chiuso
        # alla fine del metodo e diventa inutilizzabile
        # all'interno del thread.
        self.cr = pooler.get_db(self.dbname).cursor()

        self.productImportID = ids[0]

        self.context = context
        self.error = []
        self.warning = []
        self.header = True

        # Contatori dei nuovi prodotti inseriti e dei prodotti aggiornati,
        # vengono utilizzati per compilare il rapporto alla terminazione
        # del processo di import
        self.uo_new = 0
        self.uo_update = 0
        self.problems = 0
        # self.updated = 0

    def run(self):
        # Recupera il record dal database
        self.productImportTable = self.pool['pricelist.import']
        self.productImportRecord = self.productImportTable.browse(self.cr, self.uid, self.productImportID, context=self.context)
        # self.uom_id = self.productImportRecord.uom.id
        self.file_name = self.productImportRecord.file_name  # .split('\\')[-1]

        # if self.productImportRecord.pricelist_format == 'csv':
        #     try:
        #         import csv
        #         import StringIO
        #     except (ImportError, IOError) as err:
        #         _logger.debug(err)
        #
        #     ## Create virtual File:
        #     pricelistFile = StringIO.StringIO(self.productImportRecord.pricelist_text)
        #
        #     ## Process CSV file:
        #     sample = pricelistFile.read(512)
        #     pricelistFile.seek(0)
        #
        #     dialect = csv.Sniffer().sniff(sample)
        #     self.pricelist = csv.reader(pricelistFile, dialect)
        #
        #     self.numberOfLines = sum(1 for row in self.pricelist)
        #     pricelistFile.seek(0)
        #
        #     ''' Sometimes we can get an error about a new line inside a string :-(
        #     this happense, because our Unicode string is transformed in ASCII inside csv module.
        #     '''
        #     if csv.Sniffer().has_header(sample):
        #         self.pricelist.next()
        #         self.numberOfLines -= 1
        #
        # elif self.productImportRecord.pricelist_format == 'excel':
        #     try:
        #         import xlrd
        #     except (ImportError, IOError) as err:
        #         _logger.debug(err)
        #
        #     for encoding in ('utf-8', 'latin-1', 'cp1252'):
        #         try:
        #             pricelist = xlrd.open_workbook(file_contents=self.productImportRecord.pricelist_text, encoding_override=encoding)
        #             break
        #         except:
        #             pass
        #     else:
        #         raise orm.except_orm('Error', _('Unknown encoding'))
        #
        #     sheet = []
        #     sh = pricelist.sheet_by_index(0)
        #
        #     for rx in range(sh.nrows):
        #         row = []
        #         for cx in range(sh.ncols):
        #             row.append(sh.cell_value(rowx=rx, colx=cx))
        #         sheet.append(row)
        #
        #     self.numberOfLines = sh.nrows
        #     self.pricelist = sheet
        #

        try:
            self.pricelist, self.numberOfLines = import_sheet(self.file_name, self.productImportRecord.pricelist_text)
        except Exception as e:
            # Annulla le modifiche fatte
            self.cr.rollback()
            self.cr.commit()

            title = u"Import failed"
            message = u"Errore nell'importazione del file %s" % self.file_name + u"\nDettaglio:\n\n" + str(e)

            if DEBUG:
                ### Debug
                _logger.debug(message)
                pdb.set_trace()

            self.notifySuccessfulImport(self.cr, self.uid, title, message, error=True, record=self.productImportRecord)


        # Elaborazione del listino prezzi
        try:
            # Importa il listino
            self.processPricelist()

            # Genera il report sull'importazione
            self.notifySuccessfulImport(self.cr, self.uid, 'Importazione prodotti', record=self.productImportRecord)

            # Salva le modifiche sul database e chiude la connessione
            self.cr.commit()
            self.cr.close()

        except Exception as e:
            # Annulla le modifiche fatte
            self.cr.rollback()
            self.cr.commit()

            if DEBUG:
                ### Debug
                pdb.set_trace()

            message = u"Error occured at line %s" % self.importedLines + u"\nError details:\n\n" + str(e)
            self.notifySuccessfulImport(self.cr, self.uid, 'Importazione prodotti', body=message, error=True, record=self.productImportRecord)

    def processPricelist(self):
        self.importedLines = 0
        self.progressIndicator = 0

        notifyProgressStep = (self.numberOfLines / 100) + 1  # NB: divisione tra interi da sempre un numero intero!
        # NB: il + 1 alla fine serve ad evitare divisioni per zero

        for row_list in self.pricelist:
            # Update counter of imported lines
            self.importedLines = self.importedLines + 1

            # Import row
            self.importRow(row_list)

            # If 
            if (self.importedLines % notifyProgressStep) == 0:
                completedQuota = float(self.importedLines) / float(self.numberOfLines)
                completedPercentage = math.trunc(completedQuota * 100)
                self.progressIndicator = completedPercentage
                self.updateProgressIndicator()

        self.progressIndicator = 100
        self.updateProgressIndicator()

    def getBrand(self, brand_name, owner_name):
        ## Sales -> Configuration -> Address Book -> Partner Brand -> New Owner

        brand_name_lower = brand_name.lower()
        owner_name_lower = owner_name.lower()

        # Search for a brand name:
        # brand_ids = self.pool['res.partner.brand'].search(self.cr, self.uid, [('name', 'ilike', brand_name)])
        brand_ids = self.pool['res.partner.brand'].search(self.cr, self.uid, [('name', '=ilike', brand_name + '%')], context=self.context)
        if len(brand_ids) > 1:
            self.error.append(u'More than one brand {brand_name} found'.format(brand_name=brand_name))

        brandFound = False
        for brand_id in brand_ids:
            brand = self.pool['res.partner.brand'].browse(self.cr, self.uid, brand_id, self.context)

            if brand.name.lower() == brand_name_lower:
                brandFound = True
                break

                # If there is no matching brand - create one
        if not brandFound:
            owner_ids = self.pool['res.partner'].search(self.cr, self.uid, [('brand_alias', 'ilike', owner_name)], context=self.context)

            if len(owner_ids) > 1:
                self.error.append(u'More than one owner {owner_name} found'.format(owner_name=owner_name))

            ownerFound = False
            for owner_id in owner_ids:
                owner = self.pool['res.partner'].browse(self.cr, self.uid, owner_id,context=self.context)
                if owner.brand_alias.lower() == owner_name_lower:
                    ownerFound = True
                    break

            if not ownerFound:
                raise OwnerNotFoundException(u"Owner alias {owner_name} does not exist".format(owner_name=owner_name))

            brand_id = self.pool['res.partner.brand'].create(self.cr, self.uid, {
                'name': brand_name.strip().upper(),
                'owner_id': owner_id,
            }, context=self.context)

        return brand_id

    def importRow(self, row_list):
        ean13 = ''

        price = row_list[-1]
        # Sometime value is only numeric and we don't want string to be treated as Float
        row_list = [self.toStr(value) for value in row_list]

        # brand_alias, area, category, family, serie, product_code, internal_code, ean13, description, price = row_list
        # r_sociale, brand_alias, area, category, family, serie, product_code, internal_code, description, ean13, price = row_list

        owner, brand, area, category, family, serie, internal_code, product_name, ean13, year, price_as_string = row_list

        # ean13 = str(ean13)
        if len(ean13) < 12:
            ean13 = ''
        elif len(ean13) < 13:
            ean13 = ean13.rjust(13, '0')

        try:
            if price == '':
                price = 0
            price = float(price)
            self.header = False
        except:
            if not self.header:
                # It's not a header row
                self.error.append(u'{price} in line {importedLines} is not a valid price value'.format(price=price, importedLines=self.importedLines))
            return

        if len(product_name) == 0 and len(ean13) == 0:
            return

        if len(internal_code) == 0 and len(product_name) > 0:
            internal_code = product_name

        product_category, error = self.getCategory([brand, area, category, family, serie])

        if not error == '':
            print error
            self.error.append(error)
            return
        try:
            brand_id = self.getBrand(brand, owner)
        except:
            self.error.append(u'Il brand {brand} di {owner} non è stato trovato nella riga{importedLines}'.format(brand=brand, owner=owner, importedLines=self.importedLines))
            return

        if ean13 == '':
            # Check if product is already registered in the DB, in this case the product need to be updated, else we must
            # create it
            product_ids = self.product_obj.search(self.cr, self.uid, [('brand_id', '=', brand_id), ("name", '=', product_name)], context=self.context)
            if not product_ids:
                product_ids = self.product_obj.search(self.cr, self.uid, [('brand_id', '=', brand_id), ("name", '=', product_name), ('active', '=', False)], context=self.context)
        else:
            product_ids = self.product_obj.search(self.cr, self.uid, [('brand_id', '=', brand_id), ("ean13", '=', ean13)], context=self.context)
            if not product_ids:
                product_ids = self.product_obj.search(self.cr, self.uid, [('brand_id', '=', brand_id), ("ean13", '=', ean13), ('active', '=', False)], context=self.context)
        if not product_ids:
            product_ids = self.product_obj.search(self.cr, self.uid,
                                                  [('brand_id', '=', brand_id), ("name", '=', internal_code)],
                                                  context=self.context)
        if not product_ids:
            product_ids = self.product_obj.search(self.cr, self.uid,
                                                  [('brand_id', '=', brand_id), ("name", '=', internal_code), ('active', '=', False)],
                                                  context=self.context)

        # If a matching product is already in the DB proceed with the update....
        if product_ids:
            for product_id in product_ids:
                self.uo_update += 1

                product = self.product_obj.write(self.cr, self.uid, product_id, {
                    'default_code': internal_code,
                    'name': product_name,
                    'ean13': ean13,
                    'brand_id': brand_id,
                    'categ_id': product_category,
                    'cost_price': price,
                    'min_cost_price': price * 0.5,
                    'max_cost_price': price * 1.5,
                    'year': year,
                    'active': True
                }, self.context)

        # ....else create the new product and the new suppliers entries.
        # We use the code and the description of the manufacturer
        else:
            self.uo_new += 1

            if len(product_name) > 256:
                self.error.append(u'{product_name} exceeds 256 char limit al line {importedLines} on name'.format(product_name=product_name, importedLines=self.importedLines))

            uom_ids = self.pool['product.uom'].search(self.cr, self.uid, [('name', '=', 'PCE'), ], context=self.context)
            if len(uom_ids) > 0:
                uom_id = uom_ids[0]
            else:
                uom_id = 1

            '''
            We should never register internal_code, because this can create e
            serious problem of disalignment.
            If we register a product with internal_code which is not generated,
            counters will not be updated and the next time we generate an internal_code
            we can produce the same code which is assigned to some product.
            '''
            # default_code is generated automaticaly by module product_code_category

            product_vals = {
                'default_code': internal_code,
                'name': product_name,
                'ean13': ean13,
                'brand_id': brand_id,
                'categ_id': product_category,
                'uom_id': uom_id,
                'uom_po_id': uom_id,
                'cost_price': price,
                'min_cost_price': price * 0.5,
                'max_cost_price': price * 1.5,
                'year': year
            }
            product_id = self.product_obj.create(self.cr, self.uid, product_vals, self.context)
            product_ids = [product_id]
        return product_ids

    def notifySuccessfulImport(self, cr, uid, title, body='', error=False, record=False):
        EOL = '\n<br/>'
        end_time = datetime.now()
        duration_seconds = (end_time - self.start_time).seconds
        duration = u'{min}m {sec}sec'.format(min=duration_seconds / 60, sec=duration_seconds - duration_seconds / 60 * 60)
        user = self.pool['res.users'].browse(cr, uid, uid, context=self.context)

        if not error:
            body += EOL + EOL
            body += u"File '{0}' {1}{1}".format(self.file_name, EOL)
            body += _(u"Importate righe: {self.uo_new}{eol}Righe non importate: {self.problems}{eol}").format(self=self, eol=EOL)
            body += _(u"Righe aggiornate: {0}{1}").format(self.uo_update, EOL)
            body += _(u'Inizio: {0}{1}').format(self.start_time.strftime('%Y-%m-%d %H:%M:%S'), EOL)
            body += _(u'Fine: {0}{1}').format(end_time.strftime('%Y-%m-%d %H:%M:%S'), EOL)
            body += _(u'Importazione eseguita in: {0}{1}{1}').format(duration, EOL)
            if self.error:
                body += u'{0}{0}<strong>Errori:</strong>{0}'.format(EOL) + EOL.join(self.error)

            if self.warning:
                body += u'{0}{0}<strong>Avvisi:</strong>{0}'.format(EOL) + EOL.join(self.warning)

        # OpenERP v.6.1:
        mail_id = self.pool['mail.message'].create(cr, uid, {
            'subject': title,
            'date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'email_from': user.company_id.email or 'Data@Import',
            'email_to': user.user_email or '',
            'user_id': uid,
            'body_text': body,
            'body_html': body,
            'model': 'filedata.import',
            'state': 'outgoing',
            'subtype': 'html',
        }, self.context)

        if record:
            # add file to attachment of email for future use
            self.pool['mail.message'].write(cr, uid, mail_id, {
                'attachment_ids': [(0, 0, {
                    'res_model': 'mail.message',
                    'name': record.file_name,  # .split('\\')[-1],
                    'datas_fname': record.file_name,
                    'datas': record.pricelist_base64,
                    'res_id': mail_id
                })]
            }, self.context)
        cr.commit()
        # cr.close()

    def notifyError(self, errorDescription):

        body = str(errorDescription)
        request = self.pool['res.request']
        request.create(
            self.cr,
            self.uid,
            vals={
                'name': _("Pricelist Import Error"),
                'act_from': self.uid,
                'act_to': self.uid,
                # 'ref_partner_id': self.manufacturerID,
                'state': 'waiting',
                'body': body,
                'active': True,
            },
            context=self.context
        )

        # Salva il messaggio di errore nel database e chiudi la connessione
        self.cr.commit()
        self.cr.close()

    # ===========================================================================
    # Utility methods
    # ===========================================================================
    def getProductTemplateID(self, product_id):
        # Get the product_tempalte ID

        # Retrive the record associated with the product id
        productObject = self.product_obj.browse(self.cr, self.uid, product_id, self.context)

        # Retrive the template id
        product_template_id = productObject.product_tmpl_id.id

        # Return the template id
        return product_template_id

    def getCategory(self, category_list):
        '''Get the category that match the specified discount family, in not found create it
        
        Category identified by:
            area, category, family, serie
          
        Returns:
          The category ID of the product
        '''

        category_list.append('')

        ## parent_id is NULL
        parent_id = False
        # 1 - All products
        category_id = 1

        parent_prefix = '00' * (len(category_list) - 1)
        prefix_length = len(parent_prefix)

        k = 0

        for category_name in category_list:
            k += 1
            if not category_name == '':
                # category_name = self.toStr(category_name)
                if len(category_name) > 63:
                    return (u'', u'%s exceeds 63 char limit' % category_name)

                # category_ids = self.pool['product.category'].search(
                #       self.cr, self.uid, [('name', '=', category_name), ("parent_id", '=', parent_id)])
                category_ids = self.pool['product.category'].search(self.cr, self.uid, [
                    ('name', '=ilike', category_name),
                    ('parent_id', '=', parent_id)
                ], context=self.context)

                category_ids = sorted(category_ids)

                categoryFound = False

                for category in self.pool['product.category'].browse(self.cr, self.uid, category_ids, self.context):

                    if category_name.lower() == category.name.lower():
                        categoryFound = True
                        category_id = category.id
                        break

                # if not category_ids:
                if not categoryFound:
                    '''
                        We should create a category
                    '''
                    if parent_id:
                        category_id = self.pool['product.category'].create(self.cr, self.uid,
                                                                           {'name': category_name.upper(),
                                                                            'parent_id': parent_id}, self.context)
                    else:
                        category_id = self.pool['product.category'].create(self.cr, self.uid,
                                                                           {'name': category_name.upper()},
                                                                           self.context)
                    _logger.info(u'Created category {0}'.format(category_name.upper()))
                # category_id = category_ids[0]
                #    category = self.pool['product.category'].browse(self.cr, self.uid, category_id)

                parent_id = category_id
            else:
                return category_id, ''

        return category_id, ''

    def updateProgressIndicator(self):
        self.productImportRecord.progress_indicator = self.progressIndicator
        self.productImportTable.write(self.cr, self.uid, [self.productImportID],
                                      vals={'progress_indicator': self.progressIndicator}, context=self.context)
        _logger.info('Import status: {0} ({1} lines processed)'.format(self.progressIndicator, self.importedLines))

    def toStr(self, value):
        if type(value) == type(u'a') or type(value) == type('a'):
            return value.strip()
        else:
            try:
                value = int(value)
            except:
                pass
            return unicode(value)


# ===============================================================================
# Exceptions
# ===============================================================================
class OwnerNotFoundException(Exception):
    pass
