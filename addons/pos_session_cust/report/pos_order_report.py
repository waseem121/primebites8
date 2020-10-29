# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp

class pos_order_report(osv.osv):
    _inherit = "report.pos.order"
    _description = "Point of Sale Orders Statistics"
    _auto = False

    _columns = {
        'date': fields.datetime('Date Order', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Partner', readonly=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True),
        'state': fields.selection([('draft', 'New'), ('paid', 'Closed'), ('done', 'Synchronized'), ('invoiced', 'Invoiced'), ('cancel', 'Cancelled')],
                                  'Status'),
        'user_id':fields.many2one('res.users', 'Salesperson', readonly=True),
        'price_total':fields.float('Total Price', readonly=True, digits_compute=dp.get_precision('Account')),
        'total_discount':fields.float('Total Discount', readonly=True, digits_compute=dp.get_precision('Account')),
        'average_price': fields.float('Average Price', readonly=True,group_operator="avg",digits_compute=dp.get_precision('Account')),
        'location_id':fields.many2one('stock.location', 'Location', readonly=True),
        'company_id':fields.many2one('res.company', 'Company', readonly=True),
        'nbr':fields.integer('# of Lines', readonly=True),  # TDE FIXME master: rename into nbr_lines
        'product_qty':fields.integer('Product Quantity', readonly=True, digits_compute=dp.get_precision('Account')),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'delay_validation': fields.integer('Delay Validation'),
        'product_categ_id': fields.many2one('product.category', 'Product Category', readonly=True),
    }
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_pos_order')
        cr.execute("""
            create or replace view report_pos_order as (
                select
                    min(l.id) as id,
                    count(*) as nbr,
                    s.date_order as date,
                    sum(l.qty * u.factor) as product_qty,
                    sum(l.qty * l.price_unit) as price_total,
                    sum((l.qty * l.price_unit) * (l.discount / 100)) as total_discount,
                    (sum(l.qty*l.price_unit)/sum(l.qty * u.factor))::decimal as average_price,
                    sum(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') as int)) as delay_validation,
                    s.partner_id as partner_id,
                    s.state as state,
                    s.user_id as user_id,
                    s.location_id as location_id,
                    s.company_id as company_id,
                    s.sale_journal as journal_id,
                    l.product_id as product_id,
                    pt.categ_id as product_categ_id
                from pos_order_line as l
                    left join pos_order s on (s.id=l.order_id)
                    left join product_product p on (p.id=l.product_id)
                    left join product_template pt on (pt.id=p.product_tmpl_id)
                    left join product_uom u on (u.id=pt.uom_id)
                group by
                    s.date_order, s.partner_id,s.state, pt.categ_id,
                    s.user_id,s.location_id,s.company_id,s.sale_journal,l.product_id,s.create_date
                having
                    sum(l.qty * u.factor) != 0)""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
