from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    def _get_orig_price_unit(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        purchase_lines = self.browse(cr, uid, ids, context=context)
        for line in purchase_lines:
            if not line.discount:
                res[line.id] = line.price_unit
        return res
    
    _columns = {
        'orig_price_unit': fields.function(_get_orig_price_unit, string='Orig. Unit Price', type='float',digits_compute= dp.get_precision('Product Price'), store=True),
        'discount': fields.char('Discount', readonly=True),
    }
