from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
import time

class pos_config(osv.osv):
    _inherit = "pos.config"
    
    _columns = {
        'discount': fields.float('Discount (%)', help="Select the discount percentage above which password is required"),
        'password_discount': fields.char('Discount Password'),
    }
pos_config()

class pos_order(osv.osv):
    _inherit = "pos.order"
    
    def _process_order(self, cr, uid, order, context=None):
        product_obj = self.pool.get('product.product')
        line_obj = self.pool.get('pos.order.line')
        order_id = self.create(cr, uid, self._order_fields(cr, uid, order, context=context),context)

        for payments in order['statement_ids']:
            self.add_payment(cr, uid, order_id, self._payment_fields(cr, uid, payments[2], context=context), context=context)
        if order.get('disc_checked',False): 
            prod_ids = product_obj.search(cr, uid, [('default_code','=','disc_fix')])
            if prod_ids:
                pid = prod_ids[0]
            else:
                pid = product_obj.create(cr, uid, {'name': 'Discount Fixed Price', 'default_code' : 'disc_fix', 'type': 'service'})
            line_vals = {
                'product_id' : pid,
                'qty' : 1,
                'price_unit' : -(order.get('disc_amount',False)),
                'order_id' : order_id
            }
            line_obj.create(cr, uid, line_vals)
            
        session = self.pool.get('pos.session').browse(cr, uid, order['pos_session_id'], context=context)
        if session.sequence_number <= order['sequence_number']:
            session.write({'sequence_number': order['sequence_number'] + 1})
            session.refresh()

        if not float_is_zero(order['amount_return'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')):
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