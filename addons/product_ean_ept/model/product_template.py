from openerp.osv import osv, fields
from openerp import fields

class product_template( osv.osv ):
    _inherit = 'product.template'
    ean13=fields.Char(string='EAN13 Barcode',related='product_variant_ids.main_ean13')