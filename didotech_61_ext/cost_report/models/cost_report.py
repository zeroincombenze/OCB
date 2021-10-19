# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product Detailed Structure Cost Report, Open Source    
#    Copyright (C) 2017 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#
#    Created on: 2017-12-01
#    Author : Fabio Colognesi
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

from openerp.osv import fields, osv


class mrp_price(osv.osv_memory):
    _name = 'mrp.product_price'
    _inherit = 'mrp.product_price'
    _description = "Detailed Product Cost Structure"

    _columns = {
        'name': fields.char('wizard name'),
        'bomtype': fields.selection(
            [('normal', 'Normal BoM'), ('ebom', 'Engineering BoM'), ('spbom', 'Spare BoM')],
            'BoM Type', required=True,
            help="Specify the BoM type will be used to produce or buy. Report of Cost structure will be displayed based on this BoM type."),
        'listflat': fields.boolean(
            'Add "Flat List" of products',
            help="Specify if a flat list of all products of the BoM will be printed as 'second page'."),
        'pricedigits': fields.integer(
            'Price Digits',
            help="Increase this value if some prices would be so small to be printed as zero."),
        'liststandard': fields.boolean(
            'Print "Standard Cost" of product',
            help="Specify if the standard cost of a product has to be printed when suppliers list prices exist."),
        'usestandard': fields.boolean(
            'Print only "Standard Cost" and "Customer Lead Time"',
            help="Specify if has to be used only 'Standard Cost' and 'Customer Lead Time' of a product on report."),
    }
    _defaults = {
        'name': _description,
        'bomtype': 'normal',
        'listflat': True,
        'pricedigits': 2,
        'liststandard': True,
        'usestandard': False,
    }

    def on_change_sortbyprice(self, cr, uid, oid, sortbyprice=False):
        if sortbyprice:
                return {'value': {'sortbyleadtime': False}}            
        return {'value': {'sortbyleadtime': True}}            

    def on_change_sortbyltime(self, cr, uid, oid, sortbyleadtime=False):
        if sortbyleadtime:
                return {'value': {'sortbyprice': False}}            
        return {'value': {'sortbyprice': True}}            

    def print_detailed_report(self, cr, uid, ids, context=None):
        """ To print the report of Product cost structure
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return : Report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['number', 'bomtype', 'listflat', 'pricedigits', 'liststandard', 'usestandard'])
        res = res and res[0] or {}
        datas['form'] = res

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cost.product.structure',
            'datas': datas,
        }
