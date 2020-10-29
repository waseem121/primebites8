# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
import logging
from openerp.osv import osv
from openerp import netsvc, tools, models, fields, api,_
import time
from openerp.tools import float_is_zero

from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from base64 import b64encode
from reportlab.graphics import renderPM
from reportlab.lib import units

_logger = logging.getLogger(__name__)

class pos_order(models.Model):
    _inherit = "pos.order"
    
    parent_return_order = fields.Char('Return Order ID', size=64)
    return_seq = fields.Integer('Return Sequence')
    return_process = fields.Boolean('Return Process')
    back_order = fields.Char('Back Order', size=256, default=False, copy=False)
    
    def _order_fields(self, cr, uid, ui_order, context=None):
        res = super(pos_order, self)._order_fields(cr, uid, ui_order, context=None)
        res.update({
            'return_order':         ui_order.get('return_order', ''),
            'back_order':           ui_order.get('back_order',''),
            'parent_return_order':  ui_order.get('parent_return_order',''),
            'return_seq':           ui_order.get('return_seq',''),
        })
        return res

    def _process_order(self, cr, uid, order, context=None):
        order_id = self.create(cr, uid, self._order_fields(cr, uid, order, context=context),context)

        for payments in order['statement_ids']:
            if not order.get('sale_mode') and order.get('parent_return_order', ''):
                payments[2]['amount'] = payments[2]['amount'] or 0.0
            self.add_payment(cr, uid, order_id, self._payment_fields(cr, uid, payments[2], context=context), context=context)

        session = self.pool.get('pos.session').browse(cr, uid, order['pos_session_id'], context=context)
        if session.sequence_number <= order['sequence_number']:
            session.write({'sequence_number': order['sequence_number'] + 1})
            session.refresh()

        if not order.get('parent_return_order', '') and not float_is_zero(order['amount_return'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')):
            cash_journal = session.cash_journal_id
            if not cash_journal:
                cash_journal_ids = filter(lambda st: st.journal_id.type=='cash', session.statement_ids)
                if not len(cash_journal_ids):
                    raise osv.except_osv( _('error!'),
                        _("No cash statement found for this session. Unable to record returned cash."))
                cash_journal = cash_journal_ids[0].journal_id
            self.add_payment(cr, uid, order_id, {
                'amount': -order['amount_return'],
                'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_name': _('return'),
                'journal': cash_journal.id,
            }, context=context)
        
        if order.get('parent_return_order', '') and not float_is_zero(order['amount_return'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')):
            cash_journal = session.cash_journal_id
            if not cash_journal:
                cash_journal_ids = filter(lambda st: st.journal_id.type=='cash', session.statement_ids)
                if not len(cash_journal_ids):
                    raise osv.except_osv( _('error!'),
                        _("No cash statement found for this session. Unable to record returned cash."))
                cash_journal = cash_journal_ids[0].journal_id
            self.add_payment(cr, uid, order_id, {
                'amount': -order['amount_return'],
                'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_name': _('return'),
                'journal': cash_journal.id,
            }, context=context)

        return order_id

    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
        existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]

        order_ids = []

        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            order_id = self._process_order(cr, uid, order, context=context)
            if order_id:
#                if order.get('parent_return_order'):
                    pos_line_obj = self.pool.get('pos.order.line')
                    to_be_returned_items = {}
                    for line in order.get('lines'):
                        if line[2].get('return_process'):
                            if to_be_returned_items.has_key(line[2].get('product_id')):
                                to_be_returned_items[line[2].get('product_id')] = to_be_returned_items[line[2].get('product_id')] + line[2].get('qty')
                            else:
                                to_be_returned_items.update({line[2].get('product_id'):line[2].get('qty')})
                    for line in order.get('lines'):
                        for item_id in to_be_returned_items:
                            for origin_line in self.browse(cr, uid, [line[2].get('return_process')]).lines:
                                if to_be_returned_items[item_id] == 0:
                                    continue
                                if origin_line.return_qty > 0 and item_id == origin_line.product_id.id:
                                    if (to_be_returned_items[item_id] * -1) >= origin_line.return_qty:
                                        ret_from_line_qty = 0
                                        to_be_returned_items[item_id] = to_be_returned_items[item_id] + origin_line.return_qty
                                    else:
                                        ret_from_line_qty = to_be_returned_items[item_id] + origin_line.return_qty
                                        to_be_returned_items[item_id] = 0
                                    pos_line_obj.write(cr, uid, [origin_line.id], {'return_qty': ret_from_line_qty});
            order_ids.append(order_id)

            try:
                self.signal_workflow(cr, uid, [order_id], 'paid')
            except Exception, e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice:
                self.action_invoice(cr, uid, [order_id], context)
                order_obj = self.browse(cr, uid, order_id, context)
                self.pool['account.invoice'].signal_workflow(cr, uid, [order_obj.invoice_id.id], 'invoice_open')

        return order_ids
    
    #override for pos_sireal
    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        pos_order_pool = self.pool.get('pos.order')
        move_obj = self.pool.get('stock.move')
        stock_pack_pool = self.pool.get('stock.pack.operation')
        for order in self.browse(cr, uid, ids, context=context):
            addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            if picking_type:
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': addr.get('delivery', False),
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'invoice_state': 'none',

                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise osv.except_osv(_('Error!'), _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']

            move_list = []
            for line in order.lines:
                if line.product_id and line.product_id.type == 'service':
                    continue

                move_list.append(move_obj.create(cr, uid, {
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'picking_type_id': picking_type.id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.qty),
                    'product_uom_qty': abs(line.qty),
                    'state': 'draft',
                    'location_id': location_id if line.qty >= 0 else destination_id,
                    'location_dest_id': destination_id if line.qty >= 0 else location_id,
#                     'restrict_lot_id': line.prodlot_id.id or False
                }, context=context))

            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                picking_obj.force_assign(cr, uid, [picking_id], context=context)
# CUSTOM CODE
                picking = picking_obj.browse(cr, uid, picking_id, context=context)
                items = []
                packs = []

                if not picking.pack_operation_ids:
                    picking.do_prepare_partial()
                pos_ids = pos_order_pool.search(cr, uid, [('picking_id', '=', picking_id)])
                if pos_ids:
                    pack_op_ids = [x.id for x in picking.pack_operation_ids]
                    for each_line in pos_order_pool.browse(cr, uid, pos_ids[0]).lines:
                        line_product_id = each_line.product_id.id
                        line_lot_id = each_line.prodlot_id.id
                        if line_lot_id:
                            for each_op in picking.pack_operation_ids:
                                    if each_op.product_id.id == line_product_id:
                                        if not each_op.lot_id:
                                            stock_pack_pool.write(cr, uid, each_op.id, {'lot_id': line_lot_id})
                                            break
# CUSTOM CODE
                picking_obj.action_done(cr, uid, [picking_id], context=context)
            elif move_list:
                move_obj.action_confirm(cr, uid, move_list, context=context)
                move_obj.force_assign(cr, uid, move_list, context=context)
                move_obj.action_done(cr, uid, move_list, context=context)

        return True

class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    return_qty = fields.Integer('Return QTY', size=64)
    return_process = fields.Char('Return Process')
    back_order = fields.Char('Back Order', size=256, default=False, copy=False)
    prodlot_id = fields.Many2one('stock.production.lot', "Serial No.")

class account_journal(models.Model):
    _inherit = 'account.journal'

    shortcut_key = fields.Char('Shortcut Key')
    
class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_pos_serial = fields.Boolean('POS Serial')

class product_product(models.Model):
    _inherit = 'product.product'
    
    def _check_ean_key(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_check_ean_key, 'You provided an invalid "EAN13 Barcode" reference. You may use the "Internal Reference" field instead.', ['ean13'])]
