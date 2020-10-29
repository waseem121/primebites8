from openerp import models, api

class generate_ean_wizard(models.TransientModel):
    _name = 'generate.ean.wizard'
    _description = 'Generate EAN for multiple products.'
    
    @api.multi
    def generate_eans(self):
        product_obj = self.env['product.product']
        ctx = self._context or {}
        model = ctx.get('active_model')
        if model == 'product.product':
            product_ids = ctx.get('active_ids',[])
            products = product_obj.search([('id','in',product_ids)])
            for product in products:
                product.auto_generate_ean13()
        elif model == 'product.category':
            category_ids = ctx.get('active_ids',[])
            products = product_obj.search([('categ_id','in',category_ids)])
            for product in products:
                product.auto_generate_ean13()
            if ctx.get('open_products'):
                product_action = self.env.ref('product.product_normal_action_sell',False)
                if product_action:
                    result = product_action.read()
                    result = result[0]
                    product_ids = products.ids
                    result['domain'] = "[('id','in',["+','.join(map(str, product_ids))+"])]"
                    return result
        return True
    