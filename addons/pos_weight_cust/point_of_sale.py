from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class pos_order_line(osv.osv):
    _inherit = "pos.order.line"
    
    def _amount_line_all_new(self, cr, uid, ids, field_names, arg, context=None):
        ### Add adjustment to pos order line
        print "inside _amount_line_all_new"
        res = dict([(i, {}) for i in ids])
        account_tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            taxes_ids = [ tax for tax in line.product_id.taxes_id if tax.company_id.id == line.order_id.company_id.id ]
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = account_tax_obj.compute_all(cr, uid, taxes_ids, price, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)

            cur = line.order_id.pricelist_id.currency_id
            res[line.id]['price_subtotal'] = taxes['total'] + line.adjustment
            res[line.id]['price_subtotal_incl'] = taxes['total_included'] + line.adjustment
        return res
    
    _columns = {
        'adjustment': fields.float(string='Adjustment', digits_compute=dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line_all_new, multi='pos_order_line_amount', digits_compute=dp.get_precision('Product Price'), string='Subtotal w/o Tax', store=True),
        'price_subtotal_incl': fields.function(_amount_line_all_new, multi='pos_order_line_amount', digits_compute=dp.get_precision('Account'), string='Subtotal', store=True),
        'barcode': fields.char('Barcode', help="Barcode which is scanned for punching products. If not scanning then pull barcode from product master."),
    }