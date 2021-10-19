# -*- encoding: utf-8 -*-
##############################################################################
#
#    Manufacturing Orders Barcode
#    Copyright (C) 2016 TechSpell srl (<http://techspell.eu>). All Rights Reserved
#    $Id$
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
#
#    To customize report layout :
#
#    1 - Configure final layout using bom_structure.sxw in OpenOffice
#    2 - Compile to bom_structure.rml using ..\base_report_designer\openerp_sxw2rml\openerp_sxw2rml.py
#           python openerp_sxw2rml.py bom_structure.sxw > bom_structure.rml
#
##############################################################################
import os
import time
from report import report_sxw
from operator import itemgetter
from tools.translate import _


def _moduleName():
    path = os.path.dirname(__file__)
    return os.path.basename(os.path.dirname(path))
openerpModule=_moduleName()

def _thisModule():
    return os.path.splitext(os.path.basename(__file__))[0]
thisModule=_thisModule()

def _translate(value):
    return _(value)

###############################################################################################################à

MODEL='mrp.production'
REPORTNAME='mrp.manufacturing.order'

def _createtemplate():
    """
        Automatic XML menu creation
    """
    filepath = os.path.dirname(__file__)
    fileName = thisModule + '.xml'
    fileOut = open(os.path.join(filepath, fileName), 'w')

    listout = [[MODEL, 'mrp.report_mrp_production_report', 'Manufacturing Order', REPORTNAME]]

    fileOut.write(u'<?xml version="1.0"?>\n<openerp>\n    <data>\n\n')
    fileOut.write(u'<!--\n       IMPORTANT : DO NOT CHANGE THIS FILE, IT WILL BE REGENERERATED AUTOMATICALLY\n-->\n\n')
  
    for model, label, description, name in listout:
        fileOut.write(u'        <report auto="True"\n                header="True"\n                model="%s"\n' % (model))
        fileOut.write(u'                id="%s"\n                string="%s"\n                name="%s"\n' % (label, description,name))
        fileOut.write(u'                rml="%s/report/%s.rml"\n' % (openerpModule, thisModule))
        fileOut.write(u'                report_type="pdf"\n                file=""\n                 />\n')
    
    fileOut.write(u'<!--\n       IMPORTANT : DO NOT CHANGE THIS FILE, IT WILL BE REGENERERATED AUTOMATICALLY\n-->\n\n')
    fileOut.write(u'    </data>\n</openerp>\n')
    fileOut.close()
_createtemplate()

###############################################################################################################à


def BomSort(myObject):
    bomobject = []
    res = {}
    index = 0
    for l in myObject:
        res[str(index)] = l.itemnum
        index += 1
    items = res.items()
    items.sort(key=itemgetter(1))
    for res in items:
        bomobject.append(myObject[int(res[0])])
    return bomobject

class mrp_manufacturing_order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(mrp_manufacturing_order_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_order': self.get_order,
            'get_operations': self.get_operations,
            'get_children': self.get_children,
        })

    def get_order(self, myObject):

        result = []

        def _get_rec(myObject):
 
            for line in myObject:
                res = {
                    'name': line.name,
                    'sequence': line.sequence,
                    'workcenter_id': line.workcenter_id,
                    'cycle': line.cycle,
                    'hour': line.hour,
                }
                result.append(res)
            return result

        order = _get_rec(myObject)

        return order

    def get_operations(self, myObject):

        result = []

        def _get_rec(myObject):
 
            for line in myObject:
                res = {
                    'name': line.name,
                    'sequence': line.sequence,
                    'workcenter_id': line.workcenter_id,
                    'cycle': line.cycle,
                    'hour': line.hour,
                }
                result.append(res)
            return result

        operations = _get_rec(myObject)

        return operations

    def get_children(self, myObject):

        result = []

        def _get_rec(bomobject,level):
            myObject=BomSort(bomobject)
            for line in myObject:
                res = {
                    'name': line.name,
                    'item': line.itemnum,
                    'name': line.product_id.name,
                    'description': _(line.product_id.description),
                    'pqty': line.product_qty,
                    'pweight': line.product_id.weight_net,
                }
                result.append(res)
            return result
        
        bomObject = myObject.bom_id.bom_lines
        children = _get_rec(bomObject)
        return children


report_sxw.report_sxw('report.' + REPORTNAME, MODEL, '/' + openerpModule + '/report/' + thisModule + '.rml',
                      parser=mrp_manufacturing_order_report, header='internal')
