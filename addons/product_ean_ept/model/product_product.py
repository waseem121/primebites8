from openerp import api, models, fields

def __sumDigits(chk, start=0, end=1, step=2, mult=1): 
    return reduce(lambda x, y: int(x) + int(y), list(chk[start:end:step])) * mult

def get_check_digit(chk):
    m0 = 1
    m1 = 3
    t = 10 - int(int(__sumDigits(chk, start=0, end=12, mult=m0) + (__sumDigits(chk, start=1, end=12, mult=m1))) % 10) % 10 
    if t == 10: 
        return 0 
    else: 
        return t
      
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    ean13_ids = fields.One2many('product.ean13', 'product_id', 'EAN13', copy=False)
    
    main_ean13 = fields.Char(compute='_get_main_ean13', size=13, string='Main EAN13', readonly=True)
    
  
    
    @api.model
    def create(self, vals):
        
        if vals.get('company_id', False):
            company_obj = self.env['res.company'].browse(vals['company_id'])
        elif vals.get('product_tmpl_id', False):
            company_obj = self.env['product.template'].browse(int(vals['product_tmpl_id'])).company_id
  
            print company_obj            
            if company_obj and company_obj.barcode_at_product_create :                
                ean_seq = self.env['ir.sequence'].next_by_code('product.product.ean')
                if ean_seq:
                    new_ean13 = "%s%s" % (ean_seq, get_check_digit(ean_seq))
                    if new_ean13 :
                        vals.update({'ean13_ids':[[0, False, {'by_supplier': False, 'name':new_ean13 , 'sequence': 10}]]})
        return super(ProductProduct, self).create(vals)


    @api.multi
    def auto_generate_ean13(self):
        product_ean13 = self.env['product.ean13']
        ean_seq = self.env['ir.sequence'].next_by_code('product.product.ean')
        def check_ean13(ean_seq):
            return product_ean13.search([('name', '=', new_ean13)])    
        if ean_seq:
            new_ean13 = "%s%s" % (ean_seq, get_check_digit(ean_seq))       
            
            while check_ean13(new_ean13):
                ean_seq = self.env['ir.sequence'].next_by_code('product.product.ean')
                new_ean13 = "%s%s" % (ean_seq, get_check_digit(ean_seq))
                
            ean13_ids = product_ean13.search([('product_id', '=', self.ids[0])])

            for ean_obj in ean13_ids:
                ean_obj.write({ 
                                     'sequence': ean_obj.sequence + 1 if ean_obj.sequence > 0 else 2,
                                    })
               
            vals = {
                        'sequence':1,
                        'name':new_ean13,
                        'product_id':self.ids[0],
                        'by_supplier':False,
                    }
            product_ean13.create(vals)
        self.main_ean13 = new_ean13
       
    
    @api.multi
    @api.depends('ean13_ids')
    def _get_main_ean13(self):
        for product in self: 
            if product.ean13_ids:
                product.main_ean13 = product.ean13_ids[0].name
            else :
                product.main_ean13 = ""
 

    @api.multi
    @api.depends('sequence')
    def _get_ean(self):
        res = set()
        obj = self.pool.get('product.ean13')
        for ean in obj.browse():
            res.add(ean.product_id.id)
        self.sequence = list(res)
    
    
    @api.model    
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """overwrite the search method in order to search
        on all ean13 codes of a product when we search an ean13"""
        ean_ids = []
        if filter(lambda x: x[0] == 'ean13', args):
            # get the operator of the search
            ean_operator = filter(lambda x: x[0] == 'ean13', args)[0][1]
            # get the value of the search
            ean_value = filter(lambda x: x[0] == 'ean13', args)[0][2]
            # search the ean13
            ean_ids += self.env['product.ean13'].search([('name', ean_operator, ean_value)]).ids

            # get the other arguments of the search
            args = filter(lambda x: x[0] != 'ean13', args)
            # add the new criterion
            args += [('ean13_ids', 'in', ean_ids)]
            
        if filter(lambda x: x[0] == 'barcode', args):
            # get the operator of the search
            ean_operator = filter(lambda x: x[0] == 'barcode', args)[0][1]
            # get the value of the search
            ean_value = filter(lambda x: x[0] == 'barcode', args)[0][2]
            # search the ean13

            ean_ids += self.env['product.ean13'].search([('name', ean_operator, ean_value)]).ids

            # get the other arguments of the search
            args = filter(lambda x: x[0] != 'barcode', args)
            # add the new criterion
            args += [('ean13_ids', 'in', ean_ids)]
            
        return super(ProductProduct, self).search(args, offset, limit, order, count=count)
