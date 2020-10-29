from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class purchase_order_line_scan(osv.osv_memory):
    _name = "purchase.order.line.scan"
    _description = "Purchase Order Scan"
    
    def _prepare_purchase_order_line(self, cr, uid, order, product, qty, context=None):
        if context is None:
            context = {}
        
        po_line_obj = self.pool.get('purchase.order.line')
        
        supplier = order.partner_id
        default_uom_po_id = product.uom_po_id.id
        date_order = order.date_order
        supplier_pricelist = supplier.property_product_pricelist_purchase and supplier.property_product_pricelist_purchase.id or False

        vals = po_line_obj.onchange_product_id(
            cr, uid, [], supplier_pricelist, product.id, qty, default_uom_po_id,
            supplier.id, date_order=date_order,
            fiscal_position_id=supplier.property_account_position,
            name=False, price_unit=False, state='draft', context=context)['value']
        vals.update({
            'order_id': order.id,
            'product_id': product.id,
            'taxes_id': [(6, 0, vals.get('taxes_id', []))],
        })

        return vals
    
    def make_purchase_line(self, cr, uid, ids, context=None):
        print "inside make_purchase_line: ",context
        if not context.get('active_id',False):
            return False
        
        order = self.pool.get('purchase.order').browse(cr,uid,context['active_id'])
        product_obj = self.pool.get('product.product')
        purchase_order_line = self.pool.get('purchase.order.line')
        
        for wiz in self.browse(cr,uid,ids,context):
            for line in wiz.purchase_order_line_scan_line_ids:
                barcode = line.barcode 
                product_qty = line.product_qty

                search_clause = []
                search_clause.append(('ean13','=',barcode)) if len(barcode) == 13 else search_clause.append(('default_code','=',barcode))
                print "search_clause: ",search_clause
                
                product_ids = product_obj.search(cr,uid,search_clause)
                print "product_ids: ",product_ids 
                
                if not product_ids:
                    raise osv.except_osv(_('Error!'),_("Product with barcode %s does not exist.") % (barcode,))
                
                product = product_obj.browse(cr,uid,product_ids[0],context)
                
                vals = self._prepare_purchase_order_line(cr, uid, order, product, product_qty, context=context)
                purchase_order_line.create(cr, uid, vals, context=context)
            
        return True
    
    _columns = {
        'purchase_order_line_scan_line_ids': fields.one2many('purchase.order.line.scan.line', 'purchase_order_line_scan_id', 'Scan Lines'),
    }
    
purchase_order_line_scan()
    
    
class purchase_order_line_scan_line(osv.osv_memory):
    _name = "purchase.order.line.scan.line"
    _description = "Purchase Order Scan Lines"
    _columns = {
        'barcode': fields.char('Barcode', size=13, required=True),
        'product_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'purchase_order_line_scan_id': fields.many2one('purchase.order.line.scan', 'Purchase Order Line')
    }
    
purchase_order_line_scan_line()    