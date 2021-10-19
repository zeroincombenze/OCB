# -*- coding: utf-8 -*-


import tools

from openerp.osv import fields, orm


class product_document_grouped(orm.Model):

    _name = 'product.document.grouped'

    _auto = False
    _rec_name = 'partner_id'

    DOCUMENT_TYPE = [
        ('10_sale_order', 'Preventivi Vendita'),
        ('15_sale_order', 'Ordini Vendita'),
        ('20_purchase_order', 'Ordini Acquisto'),
        ('30_out_invoice', 'Fatture Cliente'),
        ('40_in_invoice', 'Fatture Fornitori'),
        ('50_out_refund', 'Note Accredito Cliente'),
        ('60_in_refund', 'Note Accredito Fornitore'),
    ]

    _columns = {
        'name': fields.char('Numero Documento', size=64),
        'year': fields.char('Anno', size=64),
        'document_type': fields.selection(DOCUMENT_TYPE, 'Tipo Documento', readonly=True),
        'state': fields.char('Stato', size=64),
        'document_date': fields.date('Data Documento', size=64),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'product_id': fields.many2one('product.product', 'Prodotto'),
        'qty': fields.float(u'Qtà'),
        'uom': fields.many2one('product.uom', 'Uom'),
        'price_unit': fields.float('Prezzo Unitario'),
        'discount': fields.float('Sconto'),
        'price_unit_discount': fields.float('Prezzo Scontato'),
        'date_from': fields.function(lambda *a, **k: {}, method=True, type='date', string="Dal"),
        'date_to': fields.function(lambda *a, **k: {}, method=True, type='date', string="Al"),

    }

    _order = "year desc, document_date desc"

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'product_document_grouped')

        try:
            cr.execute("""
                            CREATE or REPLACE view product_document_grouped AS (
                            SELECT 
                            row_number() OVER ()::INTEGER AS id,
                            to_char(document_date, 'YYYY'::text) AS year, 
                            *
                            FROM
                            (
                                SELECT 
                                    *
                                FROM
                                    (SELECT 
                                    '20_purchase_order'::text as document_type,
                                    purchase_order.state::text as state,
                                    purchase_order.name::text as name, 
                                    (case 
                                        when purchase_order.date_approve is not null then purchase_order.date_approve
                                        else purchase_order.date_order
                                    end) as document_date, 
                                    purchase_order.partner_id as partner_id,
                                    purchase_order_line.product_id as product_id,
                                    purchase_order_line.product_qty as qty,
                                    purchase_order_line.product_uom as uom,
                                    purchase_order_line.price_unit as price_unit,
                                    purchase_order_line.discount as discount,
                                    (case
                                        when purchase_order_line.price_unit <> 0 then purchase_order_line.price_unit * (100 - discount) / 100
                                        else 0.0
                                    end) as price_unit_discount
    
                                    FROM purchase_order_line purchase_order_line
                                                          join purchase_order purchase_order on (purchase_order_line.order_id=purchase_order.id) 
                                    where purchase_order_line.order_id = purchase_order.id and purchase_order.state not in ('draft', 'cancel')
                                    group by purchase_order.date_order, purchase_order.date_approve, purchase_order.name, purchase_order.partner_id, purchase_order.state, purchase_order_line.product_id, purchase_order_line.product_qty, purchase_order_line.product_uom, purchase_order_line.price_unit, purchase_order_line.discount) as orders
    
                                UNION ALL
    
                                SELECT 
                                    *
                                FROM
                                    (SELECT 
                                    (case
                                        when sale_order.state in ('done', 'manual', 'progress') then '15_sale_order'::text
                                        else  '10_sale_order'::text
                                    end) as document_type,
                                    sale_order.state::text as state,
                                    sale_order.name::text as name, 
                                    (case 
                                        when sale_order.date_confirm is not null then sale_order.date_confirm
                                        else sale_order.date_order
                                    end) as document_date, 
                                    sale_order.partner_id as partner_id,
                                    sale_order_line.product_id as product_id,
                                    sale_order_line.product_uom_qty as qty,
                                    sale_order_line.product_uom as uom,
                                    sale_order_line.price_unit as price_unit,
                                    sale_order_line.discount as discount,
                                    (case
                                        when sale_order_line.product_uom_qty <> 0 then sale_order_line.price_subtotal / sale_order_line.product_uom_qty
                                        else 0.0
                                    end) as price_unit_discount
    
                                FROM sale_order_line sale_order_line
                                                      join sale_order sale_order on (sale_order_line.order_id=sale_order.id) 
                                where sale_order_line.order_id = sale_order.id and sale_order.state not in ('draft', 'cancel')
                                group by sale_order.date_order, sale_order.date_confirm, sale_order.name, sale_order.partner_id, sale_order.state, sale_order_line.product_id, sale_order_line.product_uom_qty, sale_order_line.product_uom, sale_order_line.price_unit, sale_order_line.price_subtotal, sale_order_line.discount) as orders
    
                                UNION ALL
    
                                SELECT
                                    *
                                FROM
                                    (SELECT 
                                    '30_out_invoice'::text as document_type,
                                    account_invoice.state::text as state,
                                    account_invoice.number::text as name, 
                                    account_invoice.date_invoice as document_date, 
                                    account_invoice.partner_id as partner_id,
                                    account_invoice_line.product_id as product_id,
                                    account_invoice_line.quantity as qty,
                                    account_invoice_line.uos_id as uom,
                                    account_invoice_line.price_unit as price_unit,
                                    account_invoice_line.discount as discount,
                                    (case
                                        when account_invoice_line.quantity <> 0 then account_invoice_line.price_subtotal / account_invoice_line.quantity
                                        else 0.0
                                    end) as price_unit_discount
    
                                FROM account_invoice_line account_invoice_line
                                                      join account_invoice account_invoice on (account_invoice_line.invoice_id=account_invoice.id) 
                                where account_invoice_line.product_id is not null and account_invoice.state in ('open', 'paid') and account_invoice_line.invoice_id=account_invoice.id and account_invoice.type = 'out_invoice'
                                group by account_invoice.date_invoice, account_invoice.number, account_invoice.partner_id, account_invoice.state, account_invoice_line.product_id, account_invoice_line.uos_id, account_invoice_line.quantity, account_invoice_line.price_unit, account_invoice_line.price_subtotal, account_invoice_line.discount) as invoices
    
                                UNION ALL
    
                                SELECT
                                    *
                                FROM
                                    (SELECT 
                                    '50_out_refund'::text as document_type,
                                    account_invoice.state::text as state,
                                    account_invoice.number::text as name, 
                                    account_invoice.date_invoice as document_date, 
                                    account_invoice.partner_id as partner_id,
                                    account_invoice_line.product_id as product_id,
                                    account_invoice_line.quantity as qty,
                                    account_invoice_line.uos_id as uom,
                                    account_invoice_line.price_unit as price_unit,
                                    account_invoice_line.discount as discount,
                                    (case
                                        when account_invoice_line.quantity <> 0 then account_invoice_line.price_subtotal / account_invoice_line.quantity
                                        else 0.0
                                    end) as price_unit_discount
    
                                FROM account_invoice_line account_invoice_line
                                                      join account_invoice account_invoice on (account_invoice_line.invoice_id=account_invoice.id) 
                                where account_invoice_line.product_id is not null and account_invoice.state in ('open', 'paid') and account_invoice_line.invoice_id=account_invoice.id and account_invoice.type = 'out_refund'
                                group by account_invoice.date_invoice, account_invoice.number, account_invoice.partner_id, account_invoice.state, account_invoice_line.product_id, account_invoice_line.uos_id, account_invoice_line.quantity, account_invoice_line.price_unit, account_invoice_line.price_subtotal, account_invoice_line.discount) as invoices
    
                                UNION ALL
    
                                SELECT
                                    *
                                FROM
                                    (SELECT 
                                    '40_in_invoice'::text as document_type,
                                    account_invoice.state::text as state,
                                    account_invoice.number::text as name, 
                                    account_invoice.date_invoice as document_date, 
                                    account_invoice.partner_id as partner_id,
                                    account_invoice_line.product_id as product_id,
                                    account_invoice_line.quantity as qty,
                                    account_invoice_line.uos_id as uom,
                                    account_invoice_line.price_unit as price_unit,
                                    account_invoice_line.discount as discount,
                                    (case
                                        when account_invoice_line.quantity <> 0 then account_invoice_line.price_subtotal / account_invoice_line.quantity
                                        else 0.0
                                    end) as price_unit_discount
    
                                FROM account_invoice_line account_invoice_line
                                                      join account_invoice account_invoice on (account_invoice_line.invoice_id=account_invoice.id) 
                                where account_invoice_line.product_id is not null and account_invoice.state in ('open', 'paid') and account_invoice_line.invoice_id=account_invoice.id and account_invoice.type = 'in_invoice'
                                group by account_invoice.date_invoice, account_invoice.number, account_invoice.partner_id, account_invoice.state, account_invoice_line.product_id, account_invoice_line.uos_id, account_invoice_line.quantity, account_invoice_line.price_unit, account_invoice_line.price_subtotal, account_invoice_line.discount) as invoices
    
                                UNION ALL
    
                                SELECT
                                    *
                                FROM
                                    (SELECT 
                                    '60_in_refund'::text as document_type,
                                    account_invoice.state::text as state,
                                    account_invoice.number::text as name, 
                                    account_invoice.date_invoice as document_date, 
                                    account_invoice.partner_id as partner_id,
                                    account_invoice_line.product_id as product_id,
                                    account_invoice_line.quantity as qty,
                                    account_invoice_line.uos_id as uom,
                                    account_invoice_line.price_unit as price_unit,
                                    account_invoice_line.discount as discount,
                                    (case
                                        when account_invoice_line.quantity <> 0 then account_invoice_line.price_subtotal / account_invoice_line.quantity
                                        else 0.0
                                    end) as price_unit_discount
    
                                FROM account_invoice_line account_invoice_line
                                                      join account_invoice account_invoice on (account_invoice_line.invoice_id=account_invoice.id) 
                                where account_invoice_line.product_id is not null and account_invoice.state in ('open', 'paid') and account_invoice_line.invoice_id=account_invoice.id and account_invoice.type = 'in_refund'
                                group by account_invoice.date_invoice, account_invoice.number, account_invoice.partner_id, account_invoice.state, account_invoice_line.product_id, account_invoice_line.uos_id, account_invoice_line.quantity, account_invoice_line.price_unit, account_invoice_line.price_subtotal, account_invoice_line.discount) as invoices
                            )
                            AS SUPER_QUERY
                            )
                            """)
        except Exception as e:
            print(e)


