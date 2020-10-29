# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime
import pytz
import time
from openerp import tools
from openerp.osv import osv
from openerp.report import report_sxw

class pos_order_details(report_sxw.rml_parse):
    
    def _pos_sales_details(self,session):
        order_ids = session.order_ids
        print'order_ids----',order_ids
        cur_obj = self.pool.get('res.currency')
        total_discount = 0.0
        total_sale = 0.0
        total_netsale = 0.0
        for order in order_ids:
            for line in order.lines:
                cur = line.order_id.pricelist_id.currency_id
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                discount = (line.price_unit - price)*line.qty
                discount = cur_obj.round(self.cr, self.uid, cur, discount)
                total_discount += discount
                total_netsale += line.price_subtotal
        sale_total = total_netsale+total_discount 
        data = [{'sale_total':sale_total,'dicount_total':total_discount,'net_sale':total_netsale}]
        if data:
            return data
        else:
            return {}


    def __init__(self, cr, uid, name, context):
        super(pos_order_details, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'pos_sales_details':self._pos_sales_details,
        })


class report_pos_order_details(osv.AbstractModel):
    _name = 'report.pos_session_cust.report_sessionordersummary'
    _inherit = 'report.abstract_report'
    _template = 'pos_session_cust.report_sessionordersummary'
    _wrapped_report_class = pos_order_details

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
