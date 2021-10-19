# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2012 Andrei Levin (andrei at lanart.it)
#
#                          All Rights Reserved.
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
##############################################################################

import base64

from openerp.osv import orm, fields

from welld_import_pricelist.utils import import_pricelist


# ASCII_CODE = 'ascii'
# UTF8_CODE = 'utf-8'
# ISO_8859_15_CODE = 'iso-8859-15'

class pricelist_import(orm.TransientModel):
    _name = "pricelist.import"
    _description = "Import pricelist"
    _inherit = "ir.wizard.screen"

    _description = "Import pricelist from file"

    # Campi dati della tabella nel DB
    _columns = {
        # Stato in cui si trova il wizard
        'state': fields.selection(
            [
                ('import', 'import'),
                ('preview', 'preview'),
                ('end', 'end'),
            ],
            'state',
            required=True,
            translate=False,
            readonly=True,
        ),

        # Dati contenuti nel file passato dall'utente arrivano codificati in BASE64
        'pricelist_base64': fields.binary(
            'Pricelist file path',
            required=False,
            translate=False,
        ),

        'file_name': fields.char('File Name', size=256),

        # Dati contenuti nel file passato dall'utente in formato testo
        'pricelist_text': fields.binary(
            'Pricelist file path',
            required=False,
            translate=False,
        ),

        ## Codifiche disponibili
        # 'text_encoding': fields.selection(
        #    [
        #        (ASCII_CODE, 'ascii'),
        #        (UTF8_CODE, 'utf-8'),
        #        (ISO_8859_15_CODE, 'iso-8859-15'),
        #    ],
        #    'Text encoding',
        #    required=True,
        #    translate=False,
        # ),

        'pricelist_format': fields.selection(
            [
                ('csv', 'CSV'),
                ('excel', 'Excel - xls'),
            ],
            'Format',
            required=True,
            translate=False,
            # readonly=False,
        ),

        ## Righe del listino che danno problemi, memorizzate con la
        # codifica originale
        'preview_text_original': fields.binary(
            'Preview text in original encoding',
            required=False,
            translate=False,
            readonly=True,
        ),

        # Righe del listino che danno problemi, memorizzate in
        # utf-8 e convertite con la codifica definita dall'utente
        'preview_text_decoded': fields.text(
            'Preview text decoded',
            required=False,
            translate=False,
            readonly=True,
        ),

        # Fornitore a cui si riferisce il listino
        # 'supplier': fields.many2one(
        #     'res.partner',
        #     'Seller',
        #     required=True,
        #     translate=False,
        # ),

        # # Unit of Measurement
        # 'uom': fields.many2one(
        #     'product.uom',
        #     'Unit of Measure',
        #     required=True,
        #     translate=True,
        # ),

        # Percentuale raggiunta nella converione
        'progress_indicator': fields.integer(
            'Import completato',
            size=3,
            translate=False,
            readonly=True,
        ),

    }

    # Valori de default per i campi dati dell'oggetto
    _defaults = {
        # 'text_encoding': 1,
        'pricelist_format': 'excel',
        'state': 'import',
        'progress_indicator': 0,
    }

    # # # # # # # # # # # # # # # # # # # # # #
    # Azioni associate ai click dei pulsanti  #
    # # # # # # # # # # # # # # # # # # # # # #

    def actionCheckEncoding(self, cr, uid, ids, context):
        # ATTENZIONE: è NECESSARIO passare il contesto alla funzione read
        #             perchè funzioni correttamente!!!!
        record = self.browse(cr, uid, ids[0], context=context)

        # Verifichiamo che ci sia stato passato un file da cui prendere i dati

        # Estrazione del contenuto del file in codifica base64
        pricelistBase64 = record.pricelist_base64

        # Check if user supplied the data, if data was not supplied show a message
        if not pricelistBase64:
            # Send a message to the user telling that there is a missing field
            raise orm.except_orm('Attenzione!', 'Non è stato impostato il file contenente il listino')

        # end if

        # TODO: verifica impostazione del supplier

        # Decodifica del contenuto del file e memorizzazione del testo ottenuto nell'oggetto
        pricelistText = base64.decodestring(pricelistBase64)

        vals = {
            'pricelist_text': pricelistText,
            'file_name': record.file_name,
        }

        self.write(cr, uid, ids, vals, context=context)

        # Passaggio allo stato finale
        self.write(cr, uid, ids, {'state': 'end'}, context=context)
        cr.commit()
        # Avvio processo di import
        self.startImport(cr, uid, ids, context)

        # Fine funzione
        return False

    def actionStartImport(self, cr, uid, ids, context):
        # Imposta lo stato finale come prossimo stato
        self.write(cr, uid, ids, {'state': 'end'}, context=context)

        # Avvia la procedura di import
        self.startImport(cr, uid, ids, context)

        ### Avvia l'importatore
        ##importer = import_pricelist.ImportPricelist( cr, uid, ids, context )
        ##importer.start()

        # Fine funzione
        return False

    # end startImport()


    # # # # # # # # # # # #
    # Metodi dell'oggetto #
    # # # # # # # # # # # #

    def startImport(self, cr, uid, ids, context):
        # Avvia l'importatore
        importer = import_pricelist.ImportPricelist(cr, uid, ids, context)
        importer.start()

    # end startImport()

    # def actionShowCsv(self, cr, uid, ids, context ):
    #    self.write(cr, uid, ids, {'state': 'preview'}, context=context)

    def onChangeEncoding(self, cr, uid, ids, context, text_encoding, state):
        pass
