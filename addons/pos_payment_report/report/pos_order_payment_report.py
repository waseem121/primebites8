from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp

class report_pos_order_payment(osv.osv):
    _name = "report.pos.order.payment"
    _description = "Point of Sale Payment Analysis"
    _auto = False
    
    _columns = {
        'pos_session_id' : fields.many2one('pos.session', 'Session'),
        'pos_config_id' : fields.many2one('pos.config', 'Point of Sale'),
        'statement_name': fields.char('Reference'),
        'date': fields.date('Date'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'period_id': fields.many2one('account.period', 'Period'),
        'balance_start': fields.float('Starting Balance', digits_compute=dp.get_precision('Account')),
        'balance_end_real': fields.float('Ending Balance', digits_compute=dp.get_precision('Account')),
        'currency': fields.many2one('res.currency', 'Currency'),
        'company_id': fields.many2one('res.company','Company'),
    }
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'report_pos_order_payment')
        cr.execute("""
            create or replace view report_pos_order_payment as (
                select
                    min(bs.id) as id,
                    count(*) as nbr,
                    bs.pos_session_id as pos_session_id,
                    ps.config_id as pos_config_id,
                    bs.name as statement_name,
                    bs.date as date,
                    bs.journal_id as journal_id,
                    bs.period_id as period_id,
                    bs.balance_start as balance_start,
                    bs.balance_end_real as balance_end_real,
                    bs.company_id as company_id
                from pos_session as ps
                    left join account_bank_statement bs on (bs.pos_session_id=ps.id)
                group by
                    bs.pos_session_id, ps.config_id, bs.name, bs.date, bs.journal_id, bs.period_id, bs.balance_start,
                    bs.balance_end_real, bs.company_id)""")
