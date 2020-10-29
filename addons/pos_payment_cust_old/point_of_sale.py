import logging

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
import time

from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class pos_order(osv.osv):
    _inherit = "pos.order"
    
    def create_from_ui(self, cr, uid, orders, context=None):
        # Keep only new orders
        #### Customize- If line qty > 9999.00 then skip the order
        submitted_references = [o['data']['name'] for o in orders]
        existing_order_ids = self.search(cr, uid, [('pos_reference', 'in', submitted_references)], context=context)
        existing_orders = self.read(cr, uid, existing_order_ids, ['pos_reference'], context=context)
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]

        order_ids = []

        for tmp_order in orders_to_save:
            #print "date_order: ",tmp_order['data']['date_order']
            if tmp_order['data']['lines'][0][2]['qty'] > 9999.00:
                continue
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            order_id = self._process_order(cr, uid, order, context=context)
            order_ids.append(order_id)

            try:
                self.signal_workflow(cr, uid, [order_id], 'paid')
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice:
                self.action_invoice(cr, uid, [order_id], context)
                order_obj = self.browse(cr, uid, order_id, context)
                self.pool['account.invoice'].signal_workflow(cr, uid, [order_obj.invoice_id.id], 'invoice_open')

        return order_ids
    
    def _process_order(self, cr, uid, order, context=None):
        ### Customize- If only cash register then amount should be total amount without change
        #print "_process_order cust order: ",order
        session = self.pool.get('pos.session').browse(cr, uid, order['pos_session_id'], context=context)

        if session.state == 'closing_control' or session.state == 'closed':
            session_id = self._get_valid_session(cr, uid, order, context=context)
            session = self.pool.get('pos.session').browse(cr, uid, session_id, context=context)
            order['pos_session_id'] = session_id

        order_id = self.create(cr, uid, self._order_fields(cr, uid, order, context=context),context)
        journal_ids = set()
        
        ### Check to see if only cash journal is being used
        only_cash_journal = True
        total_paid_amount = 0.0
        journal_obj = self.pool.get('account.journal')
        for payments in order['statement_ids']:
            journal = journal_obj.browse(cr,uid,payments[2]['journal_id'])
            #print "journal: ",journal
            total_paid_amount += payments[2]['amount']
            if journal.type != 'cash':
                only_cash_journal = False
        #print "only_cash_journal: ",only_cash_journal
        if only_cash_journal:
            total_paid_amount = total_paid_amount - order['amount_return']
            #print "total_paid_amount: ",total_paid_amount
            sample_statement = order['statement_ids'][0][2]
            new_statements = [0,0,{
                'journal_id': sample_statement['journal_id'], 
                'amount': total_paid_amount, 
                'name': sample_statement['name'], 
                'account_id': sample_statement['account_id'],
                'statement_id': sample_statement['statement_id']
            }]
            order['statement_ids'] = [new_statements]
        #print "new order: ",order
        
        for payments in order['statement_ids']:
            self.add_payment(cr, uid, order_id, self._payment_fields(cr, uid, payments[2], context=context), context=context)
            journal_ids.add(payments[2]['journal_id'])

        if session.sequence_number <= order['sequence_number']:
            session.write({'sequence_number': order['sequence_number'] + 1})
            session.refresh()

        if not float_is_zero(order['amount_return'], self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')) and not only_cash_journal:
            cash_journal = session.cash_journal_id.id
            if not cash_journal:
                # Select for change one of the cash journals used in this payment
                cash_journal_ids = self.pool['account.journal'].search(cr, uid, [
                    ('type', '=', 'cash'),
                    ('id', 'in', list(journal_ids)),
                ], limit=1, context=context)
                if not cash_journal_ids:
                    # If none, select for change one of the cash journals of the POS
                    # This is used for example when a customer pays by credit card
                    # an amount higher than total amount of the order and gets cash back
                    cash_journal_ids = [statement.journal_id.id for statement in session.statement_ids
                                        if statement.journal_id.type == 'cash']
                    if not cash_journal_ids:
                        raise osv.except_osv( _('error!'),
                            _("No cash statement found for this session. Unable to record returned cash."))
                cash_journal = cash_journal_ids[0]
            self.add_payment(cr, uid, order_id, {
                'amount': -order['amount_return'],
                'payment_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_name': _('return'),
                'journal': cash_journal,
            }, context=context)
        return order_id
