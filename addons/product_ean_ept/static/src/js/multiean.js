odoo.define('product_ean_ept.multi_ean', function (require) {
"use strict";

	var models = require('point_of_sale.models');
	
	models.load_models({
	    model: 'product.ean13',
	    fields: ['name','product_id','sequence','by_supplier','supplier_id','type'],
	    domain: null,
        loaded: function(self,prod_multi_ean){
            for (var i = 0; i < prod_multi_ean.length; i++) {
            	self.db.product_by_barcode[prod_multi_ean[i]['name']]=self.db.product_by_id[prod_multi_ean[i]['product_id'][0]]
            }
	    },
	    after:["product.product"],
	});

});
