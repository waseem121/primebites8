# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api, fields
from lxml import etree
from openerp.tools.translate import _
from openerp.osv import osv

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.multi
    def action_open_landed_cost(self):
        self.ensure_one()
        
        mod_obj = self.env['ir.model.data']
        model, action_id = tuple(
            mod_obj.get_object_reference(
                'purchase_landed_cost',
                'action_purchase_cost_distribution'))
        action = self.env[model].browse(action_id).read()[0]
        
        line_obj = self.env['purchase.cost.distribution.line']
        lines = line_obj.search([('picking_id', '=', self.id)])
        
        if not lines:
#            if self.state == 'done':
#                raise osv.except_osv(_('Error!'),_("You cannot create landed cost after the product is received."))
            ### Create new cost distribution
            cost_dist_obj = self.env['purchase.cost.distribution']
            cost_dist = cost_dist_obj.create({})
            print "cost_dist: ",cost_dist
            for move in self.move_lines:
                self.env['purchase.cost.distribution.line'].create({
                    'distribution': cost_dist.id,
                    'move_id': move.id,
                })
            ids = [cost_dist.id]
        else:
            ids = set([x.distribution.id for x in lines])
            
        if len(ids) == 1:
            res = mod_obj.get_object_reference(
                'purchase_landed_cost', 'purchase_cost_distribution_form')
            action['views'] = [(res and res[1] or False, 'form')]
            action['res_id'] = list(ids)[0]
        else:
            action['domain'] = "[('id', 'in', %s)]" % list(ids)
            
        return action
    
    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context
        
        res = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            print "context: ",context
            print "view_id: ",view_id
            is_incoming = False
            picking_type_id = context.get('default_picking_type_id',False)
            if not picking_type_id:
                if context.get('active_id',False) and context.get('active_model',False) == 'purchase.order':
#                    picking_type = self.env['stock.picking'].browse(context['active_id']).picking_type_id
                    is_incoming = True
                elif context.get('active_id',False) and context.get('active_model',False) == 'stock.picking':
                    picking_type = self.env['stock.picking'].browse(context['active_id']).picking_type_id.code
                    is_incoming = True if picking_type == 'incoming' else False
            else:
                picking_type = self.env['stock.picking.type'].browse(picking_type_id)
                is_incoming = True if picking_type.code == 'incoming' else False
            print "is_incoming: ",is_incoming
            doc = etree.XML(res['arch'])
            node_btn = doc.xpath("//button[@name='action_open_landed_cost']")

            if not is_incoming:
                parent = node_btn[0].find("..")
                parent.remove(node_btn[0])
        
            node_btn = doc.xpath("//button[@name='do_enter_transfer_details']")
            for node in node_btn:
#                if picking_type.code == 'incoming':
                if is_incoming:
                    node.set('confirm', _("Are you sure landed cost has been assigned?"))
            res['arch'] = etree.tostring(doc)  
#        print "res['arch']: ",res['arch']
        return res