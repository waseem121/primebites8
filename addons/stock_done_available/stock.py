from openerp.osv import osv

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def action_assign(self, cr, uid, ids, context=None):
        res = super(stock_picking, self).action_assign(cr, uid, ids, context)
        move_ids = []
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.state == 'assigned':
                move_ids = [x.id for x in pick.move_lines]
        print "move_ids: ",move_ids
        self.pool.get('stock.move').update_cost_price(cr,uid,move_ids,context)
        return res
    
    def _check_product_availability(self, cr, uid, ids, context=None):
        for picking in self.browse(cr,uid,ids,context):
            for move in picking.move_lines:
                if move.product_id.type == 'product' and move.availability <= 0.0:
                    return False
        return True
    
class stock_move(osv.osv):
    _inherit = "stock.move"
    
    def update_cost_price(self, cr, uid, ids, context=None):
        for move in self.browse(cr, uid, ids, context=context):
            if move.state != 'assigned':
                continue
            move.write({'price_unit': move.product_id.product_tmpl_id.standard_price})
        return True