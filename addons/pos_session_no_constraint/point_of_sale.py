from openerp.osv import osv

class pos_session(osv.osv):
    _inherit = 'pos.session'
    
    def _check_pos_config(self, cr, uid, ids, context=None):
        return True
    
    def _check_unicity(self, cr, uid, ids, context=None):
        return True
    
    _constraints = [
        (_check_unicity, "You cannot create two active sessions with the same responsible!", ['user_id', 'state']),
        (_check_pos_config, "You cannot create two active sessions related to the same point of sale!", ['config_id']),
    ]