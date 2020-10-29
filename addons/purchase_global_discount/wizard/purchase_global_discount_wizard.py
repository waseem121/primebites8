from openerp import models, fields, api
import logging
from datetime import datetime
#from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)


class purchase_global_discount_wizard(models.TransientModel):
    _name = "purchase.order.global_discount.wizard"

    # todo implement fixed amount
    type = fields.Selection([
         ('percentage', 'Percentage'),
         ('fixed_amount', 'Fixed Amount'),
         ],
         'Type',
         required=True,
         default='fixed_amount',
         )
    amount = fields.Float(
        # 'Amount',
        'Discount',
        required=True,
        )

    @api.multi
    def confirm(self):
        self.ensure_one()
        order = self.env['purchase.order'].browse(
            self._context.get('active_id', False))

        if self.type == 'percentage':
            for line in order.order_line:
                line.discount = str(self.amount) + "%"
                line.price_unit = line.orig_price_unit * (1 - (self.amount or 0.0) / 100.0)
        else:
            total_amount = order.amount_untaxed
            for line in order.order_line:
                line.discount = ((line.price_subtotal / total_amount) * self.amount) / line.product_qty
                line.price_unit = float(line.orig_price_unit) - float(line.discount)
        return True
