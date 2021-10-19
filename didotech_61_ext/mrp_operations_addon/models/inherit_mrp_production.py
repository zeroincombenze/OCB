# -*- coding: utf-8 -*-
# © 2017 Andrei Levin - Didotech srl (www.didotech.com)

import netsvc
from openerp.osv import orm, fields


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    _order = 'priority desc, name'

    def _get_production_material_cost(self, cr, uid, ids, name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        uom_obj = self.pool['product.uom']
        for production in self.browse(cr, uid, ids, context):
            cost = 0
            for stock in production.move_lines2:
                if stock.state == 'done':
                    # qty = stock.product_qty
                    cost_price = stock.product_id.standard_price

                    if stock.product_uom.category_id.id != stock.product_id.uom_id.category_id.id:
                        uos_coeff = stock.product_id.uos_coeff or 1
                        qty = stock.product_qty / uos_coeff
                    else:
                        qty = uom_obj._compute_qty(cr, uid, from_uom_id=stock.product_uom.id, qty=stock.product_qty,
                                                   to_uom_id=stock.product_id.uom_id.id)

                    cost += qty * cost_price

            result[production.id] = cost
        return result

    def _get_dummy_function(self, cr, uid, ids, name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for production_id in ids:
            result[production_id] = False
        return result

    def _search_product_bom_ids(self, cr, uid, obj, name, args, context):
        if not args:
            return
        res = []
        domain = []
        for arg in args:
            if arg[0] == name:
                domain.append(('product_id', arg[1], arg[2]))

        move_line_ids = self.pool['stock.move'].search(cr, uid, domain, context=context)
        production_ids = self.search(cr, uid, [('move_lines', 'in', move_line_ids)])
        production_ids += self.search(cr, uid, [('move_lines2', 'in', move_line_ids)])

        return [('id', 'in', list(set(production_ids)))]

    def _get_total_delay_from_operation(self, cr, uid, ids, name, arg, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        result = {}
        for production in self.browse(cr, uid, ids, context):
            delay = 0
            for work_order in production.workcenter_lines:
                if work_order.state in ['done']:
                    for operation in work_order.operation_fractions_ids:
                        delay += operation.working_time
            result[production.id] = delay

        return result

    _columns = {
        'notes': fields.text('Note'),
        'sale_id': fields.many2one('sale.order', 'Sale order', select=True),
        'partner_id': fields.related('sale_id', 'partner_id', type="many2one", relation='res.partner', string='Customer'),
        'production_material_cost': fields.function(_get_production_material_cost, string='Material Production Cost', type="float", readonly=True),
        'product_bom_ids': fields.function(_get_dummy_function, string='Product BOM', relation='product.product', type='many2one', fnct_search=_search_product_bom_ids),
        'total_delay': fields.function(_get_total_delay_from_operation, string='Working Hours', type="float",
                                 help="The elapsed time between operation start and stop in this Work Center",
                                 readonly=True),
    }

    # def create(self, cr, uid, values, context=None):
    #     context = context or self.pool['res.users'].context_get(cr, uid)
    #     if 'sale_id' in values and values['sale_id']:
    #         sale_order = self.pool['sale.order'].read(cr, uid, values['sale_id'], ['name', 'client_order_ref'], context)
    #         values['sale_name'] = sale_order['name']
    #         values['sale_ref'] = sale_order['client_order_ref']
    #     return super(MrpProduction, self).create(cr, uid, values, context)

    def _make_production_internal_shipment(self, cr, uid, production, context=None):
        picking_id = super(MrpProduction, self)._make_production_internal_shipment(cr, uid, production, context)
        picking_vals = {}
        if production.sale_id:
            picking_vals.update({'sale_id': production.sale_id.id})
        if production.notes:
            picking_vals.update({'note': production.notes})
        if picking_vals:
            self.pool['stock.picking'].write(cr, uid, picking_id, picking_vals, context)
        return picking_id

    def action_production_end(self, cr, uid, ids, context=None):
        """ Finishes work order if production order is done.
        @return: Super method
        """
        obj = self.browse(cr, uid, ids, context=context)[0]
        wf_service = netsvc.LocalService("workflow")
        for workcenter_line in obj.workcenter_lines:
            if workcenter_line.state == 'draft':
                wf_service.trg_validate(uid, 'mrp.production.workcenter.line', workcenter_line.id, 'button_force_done', cr)

        return super(MrpProduction, self).action_production_end(cr, uid, ids, context=context)


