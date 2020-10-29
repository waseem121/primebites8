from openerp.osv import osv, fields

class stock_picking_done(osv.osv_memory):
    _name = 'stock.picking.done'
    
    def process_done(self, cr, uid, ids, context=None):
        print "inside process_done context: ",context
        
        if not context.get('active_ids',False):
            return False
        
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        context.update({'type': 'pos'})
        for picking in picking_obj.browse(cr,uid,context['active_ids']):
            move_list = [x.id for x in picking.move_lines]
            move_obj.action_confirm(cr, uid, move_list, context=context)
#            move_obj.force_assign(cr, uid, move_list, context=context)
            product_availability = picking_obj._check_product_availability(cr,uid,[picking.id],context)
            if not product_availability:
                continue
            move_obj.action_done(cr, uid, move_list, context=context)
#            picking_id = picking.id
#            picking_obj.action_confirm(cr, uid, [picking_id], context=context)
#            picking_obj.force_assign(cr, uid, [picking_id], context=context)
#            picking_obj.action_done(cr, uid, [picking_id], context=context)
            
        return True
        