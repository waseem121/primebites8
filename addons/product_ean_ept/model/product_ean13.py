# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime
from openerp.exceptions import Warning
import math
import string 
from openerp.addons.product import product as product

class ir_sequence_type(models.Model):
    
        _name = 'ir.sequence.type'
        
        name= fields.Char('Name', required=True)
        code= fields.Char('Code', size=32, required=True)
        
        def _create_sequence(self, cr, id, number_increment, number_next):
            assert isinstance(id, (int, long))
            sql = "CREATE SEQUENCE ir_sequence_%03d INCREMENT BY %%s START WITH %%s" % id
            cr.execute(sql, (number_increment, number_next))

def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    total = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


class product_ean13(models.Model):
    _name = 'product.ean13'
    _description = "List of EAN13 for a product."
    _order = 'sequence'
    
    name = fields.Char('EAN Number', size=13, copy=False)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    sequence = fields.Integer('Sequence',index="True")
    by_supplier = fields.Boolean('Provided By Supplier', default=True, help="This is useful to know the barcode is of supplier or not")
    supplier_id = fields.Many2one('res.partner', string='Supplier Name')
    type = fields.Char('EAN Type', default='EAN13', size=10)
    created_by = fields.Many2one('res.users', string='Created By', readonly=True)
    created_date = fields.Datetime('Created Date')
    modified_date = fields.Datetime('Modified Date')
   
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'EAN number already exist. EAN Number must be Unique.!'),
    ]
        
        
    @api.one
    @api.constrains('name')
    def _check_ean_key(self):
        if self.by_supplier:
            res = check_ean(string.zfill(self.name, 13))
            if not res:
                raise Warning(('Error: Invalid ean code.'))
        
    @api.model
    def create(self, vals):
        """Create ean13 with a sequence higher than all
        other products when it is not specified"""
        if not vals.get('sequence') and vals.get('product_id'):
            ean13s = self.search([('product_id', '=', vals['product_id'])])
            vals['sequence'] = 1
            if ean13s:
                vals['sequence'] = max([ean.sequence for ean in ean13s]) + 1
                
    
        vals['created_by'] = self.env.uid
        vals['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vals['modified_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return super(product_ean13, self).create(vals)
    
    @api.multi
    def write(self, vals):
        vals['modified_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = super(product_ean13, self).write(vals)
        return res
