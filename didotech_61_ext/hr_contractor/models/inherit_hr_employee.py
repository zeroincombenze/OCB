# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Didotech SRL
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.osv import orm, fields
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class hr_contractor(orm.Model):
    _name = 'hr.contractor'
    _description = "Contractors"
    _inherit = 'hr.employee'

    def write(self, cr, uid, ids, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if vals.get('fiscalcode_surname'):
            vals.update({'fiscalcode_surname': vals['fiscalcode_surname'].title()})
        if vals.get('name', False):
            vals.update({'name': vals['name'].title()})
        if vals.get('street', False):
            vals.update({'street': vals['street'].title()})
        if vals.get('r_street', False):
            vals.update({'r_street': vals['r_street'].title()})
        if vals.get('bank_iban', False):
            if len(vals.get('bank_iban', '')) > 27:
                raise orm.except_orm('Errore', 'IBAN {iban} più lungo di 27'.format(iban=vals['bank_iban']))

        return super(hr_contractor, self).write(cr, uid, ids, vals, context)

    def create(self, cr, uid, vals, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if vals.get('fiscalcode_surname'):
            vals.update({'fiscalcode_surname': vals['fiscalcode_surname'].title()})
        if vals.get('name', False):
            vals.update({'name': vals['name'].title()})
        if vals.get('street', False):
            vals.update({'street': vals['street'].title()})
        if vals.get('r_street', False):
            vals.update({'r_street': vals['r_street'].title()})
        if vals.get('bank_iban', False):
            if len(vals.get('bank_iban', '') > 27):
                raise orm.except_orm('Errore', 'IBAN {iban} più lungo di 27'.format(iban=vals['bank_iban']))

        return super(hr_contractor, self).create(cr, uid, vals, context)

    def name_get(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        if not len(ids):
            return []
        res = []
        for hr_employee in self.browse(cr, uid, ids, context=context):
            name = hr_employee.fiscalcode_surname.title() + ' ' + (hr_employee.name or '').title()
            code = False
            if hr_employee.r_province and hr_employee.r_province.code:
                code = hr_employee.r_province.code
            elif hr_employee.province and hr_employee.province.code:
                code = hr_employee.province.code
            if code:
                name += ' [{code}]'.format(code=code)
            res.append((hr_employee.id, name))
        return res
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        context = context or self.pool['res.users'].context_get(cr, user)
        if not args:
            args = []
        ids = []
        name_array = name.split()
        search_domain = []
        for n in name_array:
            search_domain.append('|')
            search_domain.append(('name', operator, n))
            search_domain.append(('fiscalcode_surname', operator, n))
        ids = self.search(cr, user, search_domain + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)
    
    def check_fiscalcode(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        for partner in self.browse(cr, uid, ids, context):
            if not partner.fiscalcode:
                return True
            if len(partner.fiscalcode) != 16:
                return False
        return True

    def _check_name_unique(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        contractors = self.browse(cr, uid, ids, context)
        for contractor in contractors:
            contractor_ids = self.search(cr, uid, [('fiscalcode_surname', 'ilike', contractor.fiscalcode_surname),
                                                   ('name', 'ilike', contractor.name),
                                                   ('birthday', '=', contractor.birthday)], context=context)
            if len(contractor_ids) > 1:
                message = '####### Duplicate Contractor ########'
                _logger.error(message)
                return False
            elif len(contractor_ids) < 1:
                message = '####### Ubnormal situation: contractor with id "{0}" not found ########'.format(contractor.id)
                _logger.error(message)
                return False
        return True

    def _get_age(self, cr, uid, ids, name, arg, context=None):
        start_date = datetime.now()
        res = {}
        context = context or self.pool['res.users'].context_get(cr, uid)
        for employee in self.read(cr, uid, ids, ['birthday'], context):
            birthday = employee['birthday']
            difference_in_years = 0
            if birthday:
                end_date = datetime.strptime(birthday, DEFAULT_SERVER_DATE_FORMAT)
                difference_in_years = relativedelta(start_date, end_date).years
            res[employee['id']] = difference_in_years
        return res

    _description = "HR Contractor"
    _columns = {
        'age': fields.function(_get_age, string=u"Età", readonly=True, type="integer"),
        'birthday': fields.date("Date of Birth", required=True),
        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender', required=True),
        'is_contractor': fields.boolean('On Contract Bases ?'),
        'height': fields.char('Height', size=8),
        'weight': fields.char('Weight', size=8),
        'size': fields.char('Size', size=8),
        'has_auto': fields.boolean('Has Car ?'),
        'fiscalcode': fields.char('Fiscal Code', size=16),
        'vat': fields.char('Partita Iva', size=16),
        'fiscalcode_surname': fields.char('Surname', size=64, required=True),
        'birth_city': fields.many2one('res.city', 'City of birth', required=True),
        'category_ids': fields.many2many(
            'hr.employee.category',
            'contractor_category_rel',
            'category_id',
            'contractor_id',
            'Category',
            domain=[('has_contractor', '=', True)]
        ),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'province': fields.many2one('res.province', string='Province'),
        'region': fields.many2one('res.region', string='Region'),
        'country_id': fields.many2one('res.country', 'Country'),
        'r_street': fields.char('Street', size=128),
        'r_street2': fields.char('Street2', size=128),
        'r_zip': fields.char('Zip', change_default=True, size=24),
        'r_city': fields.char('City', size=128),
        'r_province': fields.many2one('res.province', string='Province'),
        'r_region': fields.many2one('res.region', string='Region'),
        'r_country_id': fields.many2one('res.country', 'Country'),
        'cellular_type': fields.selection([
            ('standar', 'Standar'),
            ('android', 'Android'),
            ('blackbarry', 'Blackbarry'),
            ('iphone', 'Iphone')
        ], "Cellular type"),
        'mobile_phone_operator': fields.selection([
            ('tim', 'Tim'),
            ('h3g', 'Tre'),
            ('vodafone', 'Vodafone'),
            ('wind', 'Wind'),
            ('other', 'Altri')
        ], "Operatore"),

        'car_plate': fields.char('Plate', size=64),
        'car_model': fields.char('Model', size=64),
        'car_manufacturer': fields.char('Manufacturer', size=256),
        'car_refound_km': fields.integer('Refound KM.'),
        'identification_id': fields.char('Identification No', size=32, readonly=True),
        'payment_type': fields.selection([('bank', 'By Bank'), ('cash', 'By Cash')], string="Payment Method"),
        'bank_iban': fields.char('IBAN', size=64),
        'bank': fields.many2one('res.bank', 'Bank'),
        'payment_due': fields.selection([('30', '30'), ('60', '60'), ('90', '90')], string='Scadenza Pagamento'),
        # 'banner_ids' : fields.many2many('res.partner.banner',"contractor_banner_rel","contractor_id","banner_id","Banner"),
        # 'brand_ids' : fields.many2many('res.partner.brand',"contractor_brand_rel","contractor_id","brand_id","Owner"),
        'transfert': fields.boolean("Transfert ?"),
        'transfert_distance': fields.selection([
            ('0', ' '),
            ('10', '< 10 Km'),
            ('30', '< 30 Km'),
            ('50', '< 50 Km'),
            ('100', '> 50 Km')
        ], string="Distance"),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('verified', 'Verified'),
            ('assigned', 'Assigned'),
            ('released', 'Released')
        ], string='State', required=True, readonly=True),
        # 'web_gallery_image_ids': fields.one2many('web.gallery.images',
        #                                          'contractor_id',
        #                                          'Images'),
        'privacy': fields.boolean("Privacy?"),
        'date': fields.date('Date', required=True, readonly=True, select=True),
        'phone_ids': fields.one2many('hr.contractor.phone', "contractor_id", "Phone"),
        'engagement_line_ids': fields.one2many('hr.engagement', 'contractor_id', 'Order Lines', oldname='engagement_line'),
        'indirizzo_spedizione': fields.text('Indirizzo Spedizione'),
        'project_id': fields.related('engagement_line_ids', 'project_id', type='many2one', relation='project.project',
                                      string='Progetto'),
        'waiting': fields.related('engagement_line_ids', 'waiting', type='boolean', string='Attesa di Risposta'),
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'is_contractor': 1,
        'has_auto': 0,
        'state': 'draft',
        'identification_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),
    }

    _sql_constraints = [
        ('fiscalcode', 'unique(fiscalcode)', 'Fiscal Code must be unique!'),
        ('bank_iban', 'unique(bank_iban)', 'IBAN Number must be unique!'),
    ]
    
    # _constraints = [
    #     (_check_name_unique, _('Collaboratore gi presente'), ['fiscalcode_surname', 'name', 'birthday']),
    # ]

    _order = 'fiscalcode_surname'
    
    def _codicefiscale(self, cognome, nome, giornonascita, mesenascita, annonascita,
                       sesso, cittanascita):

        MESI = 'ABCDEHLMPRST'
        CONSONANTI = 'BCDFGHJKLMNPQRSTVWXYZ'
        VOCALI = 'AEIOU'
        LETTERE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        REGOLECONTROLLO = {
            'A': (0, 1), 'B': (1, 0), 'C': (2, 5), 'D': (3, 7), 'E': (4, 9),
            'F': (5, 13), 'G': (6, 15), 'H': (7, 17), 'I': (8, 19), 'J': (9, 21),
            'K': (10, 2), 'L': (11, 4), 'M': (12, 18), 'N': (13, 20), 'O': (14, 11),
            'P': (15, 3), 'Q': (16, 6), 'R': (17, 8), 'S': (18, 12), 'T': (19, 14),
            'U': (20, 16), 'V': (21, 10), 'W': (22, 22), 'X': (23, 25), 'Y': (24, 24),
            'Z': (25, 23),
            '0': (0, 1), '1': (1, 0), '2': (2, 5), '3': (3, 7), '4': (4, 9),
            '5': (5, 13), '6': (6, 15), '7': (7, 17), '8': (8, 19), '9': (9, 21)
        }
        
        ###
        # Funzioni
        ##
        def _surname(stringa):
            """Ricava, da stringa, 3 lettere in base alla convenzione dei CF."""
            cons = [c for c in stringa if c in CONSONANTI]
            voc = [c for c in stringa if c in VOCALI]
            chars = cons + voc
            if len(chars) < 3:
                chars += ['X', 'X']
            return chars[:3]
         
        def _name(stringa):
            """Ricava, da stringa, 3 lettere in base alla convenzione dei CF."""
            cons = [c for c in stringa if c in CONSONANTI]
            voc = [c for c in stringa if c in VOCALI]
            if len(cons) > 3:
                cons = [cons[0]] + [cons[2]] + [cons[3]]
            chars = cons + voc
            if len(chars) < 3:
                chars += ['X', 'X']
            return chars[:3]
         
        def _datan(giorno, mese, anno, sesso):
            """Restituisce il campo data del CF."""
            chars = (list(anno[-2:]) + [MESI[int(mese) - 1]])
            gn = int(giorno)
            if sesso == 'FEMALE':
                gn += 40
            chars += list("%02d" % gn)
            return chars
         
        def _codicecontrollo(c):
            """Restituisce il codice di controllo, l'ultimo carattere del CF."""
            sommone = 0
            for i, car in enumerate(c):
                j = 1 - i % 2
                sommone += REGOLECONTROLLO[car][j]
            resto = sommone % 26
            return [LETTERE[resto]]

        """Restituisce il CF costruito sulla base degli argomenti."""
        nome = nome.upper()
        cognome = cognome.upper()
        sesso = sesso.upper()
        cittanascita = cittanascita.upper()
        chars = (_surname(cognome) +
                 _name(nome) +
                 _datan(giornonascita, mesenascita, annonascita, sesso) +
                 list(cittanascita))
        chars += _codicecontrollo(chars)
        return ''.join(chars)
     
    def compute_fiscal_code(self, cr, uid, ids, context):

        partners = self.browse(cr, uid, ids, context)
        for partner in partners:
            if not partner.fiscalcode_surname or not partner.name or not partner.birthday or not partner.birth_city.cadaster_code or not partner.gender:
                raise orm.except_orm('Error', 'Mancano alcuni campi obligatori per il calcolo del codice fiscale')
            birthday = datetime.strptime(partner.birthday, "%Y-%m-%d")
            CF = self._codicefiscale(partner.fiscalcode_surname, partner.name, str(birthday.day),
                                     str(birthday.month), str(birthday.year), partner.gender,
                                     partner.birth_city.cadaster_code)
            self.write(cr, uid, partner.id, {'fiscalcode': CF}, context)
            
        return True

    def action_released(self, cr, uid, ids, context=None):
        # print "Call action released"
        context = context or self.pool['res.users'].context_get(cr, uid)
        self.write(cr, uid, ids, {'state': 'released'}, context)
        return True
    
    def action_assigned(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # print "Call action assigned"
        self.write(cr, uid, ids, {'state': 'assigned'}, context)
        return True

    def action_verified(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # print "Call action verified"
        self.write(cr, uid, ids, {'state': 'verified'}, context)
        return True

    def action_draft(self, cr, uid, ids, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        # print "Call action draft"
        self.write(cr, uid, ids, {'state': 'draft'}, context)
        return True

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if not args:
            args = []
        args = args[:]
        for i in range(len(args)):
            if args[i][0] == 'category_ids' and int(args[i][2]) > 0:
                args[i] = ('category_ids', '=', self.pool['hr.employee.category'].browse(cr, uid, int(args[i][2]), context).name or '')
        
        return super(hr_contractor, self).search(cr, uid, args, offset=offset, limit=limit, order=order,
                                                 context=context, count=count)

    def address_get(self, cr, uid, ids, adr_pref=['default']):
        context = self.pool['res.users'].context_get(cr, uid)
        address_obj = self.pool['res.partner.address']
        address_ids = address_obj.search(cr, uid, [('employee_id', '=', ids)], context=context)
        address_rec = address_obj.browse(cr, uid, address_ids, context=context)
        res = list(tuple(addr.values()) for addr in address_rec)
        adr = dict(res)
        # get the id of the (first) default address if there is one,
        # otherwise get the id of the first address in the list
        if res:
            default_address = adr.get('default', res[0][1])
        else:
            default_address = False
        result = {}
        for a in adr_pref:
            result[a] = adr.get(a, default_address)
        return result
    
    def on_change_city(self, cr, uid, ids, city):
        context = self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if city:
            city_id = self.pool['res.city'].search(cr, uid, [('name', '=', city.title())], context=context)
            if city_id:
                city_obj = self.pool['res.city'].browse(cr, uid, city_id[0], context)
                res = {'value': {
                    'province': city_obj.province_id.id,
                    'region': city_obj.region.id,
                    'zip': city_obj.zip,
                    'country_id': city_obj.region.country_id.id,
                    'city': city.title(),
                }}
        return res
    
    def on_change_r_city(self, cr, uid, ids, r_city):
        context = self.pool['res.users'].context_get(cr, uid)
        res = {'value': {}}
        if r_city:
            city_id = self.pool['res.city'].search(cr, uid, [('name', '=', r_city.title())], context=context)
            if city_id:
                city_obj = self.pool['res.city'].browse(cr, uid, city_id[0], context)
                res = {'value': {
                    'r_province': city_obj.province_id.id,
                    'r_region': city_obj.region.id,
                    'r_zip': city_obj.zip,
                    'r_country_id': city_obj.region.country_id.id,
                    'r_city': r_city.title(),
                }}
        return res
