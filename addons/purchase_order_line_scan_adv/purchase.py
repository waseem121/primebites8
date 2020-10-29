from openerp.osv import fields, osv
from openerp.tools.translate import _

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
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
    
    def create_from_ui(self, cr, uid, order_id, barcode, quantity, context=None):
        print "order_id barcode quantity: ",order_id, barcode, quantity
        product_obj = self.pool.get('product.product')
        
#        search_clause = []
#        search_clause.append(('ean13','=',barcode)) if len(barcode) == 13 else search_clause.append(('default_code','=',barcode))
#        print "search_clause: ",search_clause
#
#        product_ids = product_obj.search(cr,uid,search_clause)

        product_ids = product_obj.search(cr,uid,[('ean13','=',barcode)])
        if not product_ids:
            product_ids = product_obj.search(cr,uid,[('default_code','=',barcode)])
        print "product_ids: ",product_ids 

        if not product_ids:
            raise osv.except_osv(_('Error!'),_("Product with barcode %s does not exist.") % (barcode,))

        product = product_obj.browse(cr,uid,product_ids[0],context)
        order = self.pool.get('purchase.order').browse(cr,uid,order_id[0],context)

        vals = self._prepare_purchase_order_line(cr, uid, order, product, quantity, context=context)
        line_id = self.create(cr, uid, vals, context=context)
        return line_id