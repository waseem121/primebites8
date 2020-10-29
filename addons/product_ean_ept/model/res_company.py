from openerp import api, fields, models

                
class resComapny(models.Model):
    
    _name="res.company"
    _inherit=['res.company']
    barcode_at_product_create = fields.Boolean('Allow to generate barcode at product creation time') 
     
    
