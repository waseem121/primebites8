openerp.pos_mohas = function (instance) {
    var module = instance.point_of_sale;
	var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;
    
    /*For pos_serial*/
    var models = module.PosModel.prototype.models;
    for(var i=0; i<models.length; i++){
        var model=models[i];
        if(model.model === 'product.product'){
             model.fields.push('track_incoming','track_all');
        } 
    }
    
    
    /*Products load background Features*/
    var _super_posmodel = instance.point_of_sale.PosModel.prototype;
    instance.point_of_sale.PosModel = instance.point_of_sale.PosModel.extend({
        initialize: function(session, attributes) {
            _super_posmodel.initialize.call(this, session, attributes);
            this.product_list = [];
            this.product_fields = [];
            this.product_domain = [];
            this.product_context = {};
        },
     // loads all the needed data on the sever. returns a deferred indicating when all the data has loaded. 
        load_server_data: function(){
            var self = this;
            var loaded = new $.Deferred();
            var progress = 0;
            var progress_step = 1.0 / self.models.length;
            var tmp = {}; // this is used to share a temporary state between models loaders

            function load_model(index){
            	var model = self.models[index];
                if(index >= self.models.length){
                    loaded.resolve();
                }else{
                    var model = self.models[index];
                    var fields =  typeof model.fields === 'function'  ? model.fields(self,tmp)  : model.fields;
                    var domain =  typeof model.domain === 'function'  ? model.domain(self,tmp)  : model.domain;
                    var context = typeof model.context === 'function' ? model.context(self,tmp) : model.context; 
                    var ids     = typeof model.ids === 'function'     ? model.ids(self,tmp) : model.ids;
                    if ( model.model && model.model !== 'product.product') {
                        self.pos_widget.loading_message(_t('Loading')+' '+(model.label || model.model || ''), progress);
                    } else if(model.model && model.model == 'product.product') {
                        self.product_domain = self.product_domain.concat(model.domain);
                        self.product_fields = self.product_fields.concat(model.fields);
                        self.product_context = $.extend(self.product_context, context)
                    }
                    progress += progress_step;

                    if( model.model && model.model !== 'product.product'){
                        if (model.ids) {
                            var records = new instance.web.Model(model.model).call('read',[ids,fields],context);
                        } else {
                            var records = new instance.web.Model(model.model).query(fields).filter(domain).context(context).all()
                        }
                        records.then(function(result){
                                try{    // catching exceptions in model.loaded(...)
                                    $.when(model.loaded(self,result,tmp))
                                        .then(function(){ load_model(index + 1); },
                                              function(err){ loaded.reject(err); });
                                }catch(err){
                                    loaded.reject(err);
                                }
                            },function(err){
                                loaded.reject(err);
                            });
                    }else if( model.loaded ){
                        try{    // catching exceptions in model.loaded(...)
                            $.when(model.loaded(self,tmp))
                                .then(  function(){ load_model(index +1); },
                                        function(err){ loaded.reject(err); });
                        }catch(err){
                            loaded.reject(err);
                        }
                    }else{
                        load_model(index + 1);
                    }
                }
            }

            try{
                load_model(0);
            }catch(err){
                loaded.reject(err);
            }

            return loaded;
        },
    });
    
    instance.point_of_sale.PosModel.prototype.models.push({
    	model:  'res.users',
        fields: ['name','ean13'],
        domain: null,
        loaded: function(self,users){ 
        	self.users = users; 
        	self.db.add_users(users);
        },
    });
    
    var _super_posdb = instance.point_of_sale.PosDB.prototype;
    instance.point_of_sale.PosDB = instance.point_of_sale.PosDB.extend({
    	init: function(options){
    		this.user_by_ean13 = {};
    		_super_posdb.init.call(this,options);
        },
        add_users: function(users){
        	for(var i = 0, len = users.length; i < len; i++){
                var user = users[i];
                if(user.ean13){
                    this.user_by_ean13[user.ean13] = user;
                }
        	}
        },
        get_user_by_ean13: function(ean13){
            return this.user_by_ean13[ean13];
        },
    });
    
    var _super_ProductCategoriesWidget = instance.point_of_sale.ProductCategoriesWidget.prototype;
    instance.point_of_sale.ProductCategoriesWidget = instance.point_of_sale.ProductCategoriesWidget.extend({
        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            $.ajax({
                type: "POST",
                url: '/web/dataset/load_products',
                data: {
                        model: 'product.product',
                        fields: JSON.stringify(this.pos.product_fields),
                        domain: JSON.stringify(this.pos.product_domain),
                        context: JSON.stringify(this.pos.product_context)
                    },
                success: function(res) {
                    self.pos.product_list.push(JSON.parse(res))
                    self.pos.db.add_products(JSON.parse(res));
                    self.renderElement();
                },
                error: function() {
                    console.log('Product loading failed.');
                },
            });
        },
        /* For keyborad Shortcut*/
        clear_search: function(){
            _super_ProductCategoriesWidget.clear_search.call(this);
            var input = this.el.querySelector('.searchbox input');
                input.value = '';
                input.blur();
        },
    });
    
    var _super_barcodeReader = instance.point_of_sale.BarcodeReader.prototype;
    instance.point_of_sale.BarcodeReader = instance.point_of_sale.BarcodeReader.extend({
        scan: function(code){
            self = this;
            if(code.length > 3){
                if (this.pos.product_list.length == 0) {
                    var fields = ['display_name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 
                                  'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description',
                                  'product_tmpl_id'];
                    var domain = ['|','|', ['ean13', '=', code],['ean13', '=', '0'+code],['default_code', '=', code]];
                    var context = { 
                        pricelist: self.pos.pricelist.id, 
                        display_default_code: false, 
                    }
                    new instance.web.Model("product.product").get_func("search_read")(domain=domain, fields=fields, offset=0, false, false, context=context)
                        .pipe(function(result) {
                            if (result[0]) {
                                self.pos.get('selectedOrder').addProduct(result[0]);
                            } else {
                            	var partner = self.pos.db.get_partner_by_ean13(code);
                            	var cashier = self.pos.db.get_user_by_ean13(code);
                            	if(code.length == 12){
                            		partner = self.pos.db.get_partner_by_ean13('0'+code);
                                	cashier = self.pos.db.get_user_by_ean13('0'+code);
                            	}
                            	if(partner) {
                            		self.pos.get('selectedOrder').set_client(partner);
                            	}else if(cashier) {
                            		var usernameWidget_obj = new instance.point_of_sale.UsernameWidget(self, {});
                            		self.pos.cashier = {};
                        			self.pos.cashier['id'] = cashier.id;
                        			self.pos.cashier['name'] = cashier.name;
                        			$('.username').html(self.pos.cashier['name']);
                            	} else {
                            		var partner = self.pos.db.get_partner_by_ean13(code);
                                	var cashier = self.pos.db.get_user_by_ean13(code);
                                	if(partner) {
                                		self.pos.get('selectedOrder').set_client(partner);
                                	}else if(cashier) {
                                		var usernameWidget_obj = new instance.point_of_sale.UsernameWidget(self, {});
                                		self.pos.cashier = {};
                            			self.pos.cashier['id'] = cashier.id;
                            			self.pos.cashier['name'] = cashier.name;
                            			$('.username').html(self.pos.cashier['name']);
                                	} else {
                                		var parse_result = {
                                            encoding: 'error',
                                            type: 'error',
                                            code: code,
                                        }
                                        if(parse_result.type in {'product':'', 'weight':'', 'price':''}){    //ean is associated to a product
                                            if(self.action_callback['product']){
                                                self.action_callback['product'](parse_result);
                                            }
                                        }else{
                                            if(self.action_callback[parse_result.type]){
                                                self.action_callback[parse_result.type](parse_result);
                                            }
                                        }
                                	}
                            	}
                            }
                        });
                } else {
//                    _super_barcodeReader.scan.call(this,code);
                	if(code.length < 3){
                        return;
                    }else if(this.pos.db.get_product_by_ean13(code)){
                    	self.pos.get('selectedOrder').addProduct(this.pos.db.get_product_by_ean13(code));
                    	return
                    }else if(code.length === 13 && this.check_ean(code)){
                        var parse_result = this.parse_ean(code);
                    }else if(code.length === 12 && this.check_ean('0'+code)){
                        // many barcode scanners strip the leading zero of ean13 barcodes.
                        // This is because ean-13 are UCP-A with an additional zero at the beginning,
                        // so by stripping zeros you get retrocompatibility with UCP-A systems.
                        var parse_result = this.parse_ean('0'+code);
                    }else if(this.pos.db.get_product_by_reference(code)){
                        var parse_result = {
                            encoding: 'reference',
                            type: 'product',
                            code: code,
                        };
                    }else{
                        var parse_result = {
                            encoding: 'error',
                            type: 'error',
                            code: code,
                        };
                    }

                    if(parse_result.type in {'product':'', 'weight':'', 'price':''}){    //ean is associated to a product
                        if(this.action_callback['product']){
                            this.action_callback['product'](parse_result);
                        }
                    }else{
                        if(this.action_callback[parse_result.type]){
                            this.action_callback[parse_result.type](parse_result);
                        }
                    }
                }
            }
        },
    });
    
    /*POS Returns Features*/
    instance.point_of_sale.ProductScreenWidget = instance.point_of_sale.ProductScreenWidget.extend({
        init: function() {
            this._super.apply(this, arguments);
        },
        start:function(){
            var self = this;
            this._super();
            
            pos = self.pos;
            selectedOrder = self.pos.get('selectedOrder');
            $('#return_order_ref').html('');
            pos = pos;
            
            $("span#return_order").click(function() {
//                var self = this;
                $("span#return_order").css('background', 'blue');
                $("span#sale_mode").css('background', '');
                $("span#missing_return_order").css('background', '');
                selectedOrder = pos.get('selectedOrder');
                selectedOrder.set_sale_mode(false);
                selectedOrder.set_missing_mode(false);
                dialog = new instance.web.Dialog(this, {
                    title: _t("Return Order"),
                    size: 'small',
                    buttons: [
                        {text: _t("Validate"), click: function() {
                        	if(self.pos.product_list.length <= 0) {
                        		return alert("Please Wait, products are loading..")
                        	}
                            var ret_o_ref = dialog.$el.find("input#return_order_number").val();
                            if (ret_o_ref.indexOf('Order') == -1) {
                                ret_o_ref_order = _t('Order ') + ret_o_ref.toString();
                            }
                            if (ret_o_ref.length > 0) {
                                new instance.web.Model("pos.order").get_func("search_read")
                                            ([['pos_reference', '=', ret_o_ref_order]], 
                                            ['id', 'pos_reference', 'partner_id']).pipe(
                                    function(result) {
                                        if (result && result.length == 1) {
                                            new instance.web.Model("pos.order.line").get_func("search_read")
                                                    ([['order_id', '=', result[0].id],['return_qty', '>', 0]]).pipe(
                                            function(res) {
                                                if (res) {
                                                    products = [];
                                                    _.each(res,function(r) {
                                                        product = pos.db.get_product_by_id(r.product_id[0]);
                                                        products.push(product)
                                                    });
                                                    self.product_list_widget.set_product_list(products);
                                                }
                                            });
                                            selectedOrder.set_ret_o_id(result[0].id);
                                            selectedOrder.set_ret_o_ref(result[0].pos_reference);
                                            $('#return_order_ref').html(result[0].pos_reference);
                                            if (result[0].partner_id) {
                                                var partner = pos.db.get_partner_by_id(result[0].partner_id[0]);
                                                selectedOrder.set_client(partner);
                                            }
                                        } else {
                                            var error_str = _t('Please enter correct reference number !');
                                            var error_dialog = new instance.web.Dialog(this, { 
                                                size: 'small',
                                                buttons: [{text: _t("Close"), click: function() { this.parents('.modal').modal('hide'); }}],
                                            }).open();
                                            error_dialog.$el.append(
                                                '<span id="error_str" style="font-size:16px;">' + error_str + '</span>');
                                        }
                                    }
                                );
                                this.parents('.modal').modal('hide');
                            } else {
                                var error_str =_t('Order number can not be empty !');
                                var error_dialog = new instance.web.Dialog(this, { 
                                    size: 'small',
                                    buttons: [{text: _t("Close"), click: function() { this.parents('.modal').modal('hide'); }}],
                                }).open();
                                error_dialog.$el.append(
                                    '<span id="error_str" style="font-size:18px;">' + error_str + '</span>');
                            }
                        }},
                        {text: _t("Cancel"), click: function() { 
                            $("span#return_order").css('background', '');
                            $("span#sale_mode").css('background', 'blue');
                            $("span#missing_return_order").css('background', '');
                            this.parents('.modal').modal('hide'); 
                            $("span.remaining-qty-tag").css('display', 'none');
                        }}
                    ]
                }).open();
                dialog.$el.html(QWeb.render("pos-return-order", self));
                dialog.$el.find("input#return_order_number").focus();
                dialog.$el.find("input#return_order_number").keypress(function(event) {
                    if (event.which == 13) {
                        event.preventDefault();
                        $('.oe_form_button').trigger('click');
                    }
                });
            });
            
            $("span#sale_mode").click(function(event) {
                var selectedOrder = pos.get('selectedOrder');
                var id = $(event.target).data("category-id");
                selectedOrder.set_ret_o_id('');
                selectedOrder.set_sale_mode(true);
                selectedOrder.set_missing_mode(false);
                var category = pos.db.get_category_by_id(id);
                self.product_categories_widget.set_category(category);
                self.product_categories_widget.renderElement();
                
                $("span#sale_mode").css('background', 'blue');
                $("span#return_order").css('background', '');
                $("span#missing_return_order").css('background', '');
                selectedOrder.set_ret_o_ref('');
                $('#return_order_ref').html('');
                $("span.remaining-qty-tag").css('display', 'none');
            });
            
            $("span#missing_return_order").click(function(event) {
                var selectedOrder = pos.get('selectedOrder');
                var id = $(event.target).data("category-id");
//                selectedOrder.set_ret_o_id('Missing Receipt');
                selectedOrder.set_sale_mode(false);
                selectedOrder.set_missing_mode(true);
                var category = pos.db.get_category_by_id(id);
                self.product_categories_widget.set_category(category);
                self.product_categories_widget.renderElement();
                
                $("span#sale_mode").css('background', '');
                $("span#return_order").css('background', '');
                $("span#missing_return_order").css('background', 'blue');
//                selectedOrder.set_ret_o_ref('Missing Receipt');
                $('#return_order_ref').html('Missing Receipt');
                $("span.remaining-qty-tag").css('display', 'none');
            });
        },
    });

    instance.point_of_sale.ReceiptScreenWidget = instance.point_of_sale.ReceiptScreenWidget.extend({
        show: function(){
            this._super();
            var self = this;

            var barcode_val = this.pos.get('selectedOrder').getName();
            if (barcode_val.indexOf('Order') != -1) {
                var vals = barcode_val.split('Order ');
                if (vals) {
                    barcode = vals[1];
                    $("tr#barcode1").html($("<td style='padding:2px 2px 2px 0px; text-align:center;'><div class='" + barcode + "' width='150' height='50'/></td>"));
                    $("." + barcode.toString()).barcode(barcode.toString(), "code128");
                }
            }
            
            //For keyboard Shortcut
            this.handler_new_order = function(e){
                if(e.which === 110){ // for ASCII of 'n' character
                    self.finishOrder();
                }
            };
            $('body').on('keypress', this.handler_new_order);
        },
        finishOrder: function() {
        	this._super();
            this.pos.get('selectedOrder').set_ret_o_id('')
            this.pos.get('selectedOrder').destroy();
            this.pos.get('selectedOrder').set_sale_mode(false);
            this.pos.get('selectedOrder').set_missing_mode(false);
            $("span#sale_mode").css('background', 'blue');
            $("span#return_order").css('background', '');
            $("span#missing_return_order").css('background', '');
            $('#return_order_ref').html('');
            $('#return_order_number').val('');
            $("span.remaining-qty-tag").css('display', 'none');
        },
        wait: function( callback, seconds){
            return window.setTimeout( callback, seconds * 1000 );
        },
        print: function() {
            this.pos.get('selectedOrder')._printed = true;
            this.wait( function(){ window.print(); }, 2);
        },
    });
    
    var orderline_id = 1;
    
    var _super_orderline = instance.point_of_sale.Orderline.prototype;
    instance.point_of_sale.Orderline = instance.point_of_sale.Orderline.extend({
        initialize: function(attr,options){
            this.oid = null;
            this.backorder = null;
            this.prodlot_id = null;
            this.prodlot_id_id = null;
            _super_orderline.initialize.call(this, attr, options);
        },
        set_serial_id: function(sr_no_id) {
            this.prodlot_id_id = sr_no_id;
        },
        get_serial_id: function() {
            return this.prodlot_id_id;
        },
        set_serial: function(sr_no) {
            this.prodlot_id = sr_no;
        },
        get_serial: function() {
            return this.prodlot_id;
        },
        set_quantity: function(quantity){
            if(quantity === 'remove'){
                this.set_oid('');
                this.pos.get('selectedOrder').removeOrderline(this);
                return;
            }else{
                _super_orderline.set_quantity.call(this, quantity);
            }
            this.trigger('change',this);
        },
        export_as_JSON: function() {
            var lines = _super_orderline.export_as_JSON.call(this);
            var oid = this.get_oid();
            var return_process = oid;
//            if (oid) {
//                return_process = true;
//            }
            var return_qty = this.get_quantity();
            
            var order_ref = this.pos.get('selectedOrder').get_ret_o_id();
            new_val = {
                return_process: return_process,
                return_qty: parseInt(return_qty),
                prodlot_id: this.get_serial_id(),
                back_order: this.get_back_order()
            }
            $.extend(lines, new_val);
            return lines;
        },
        
        set_oid: function(oid) {
            this.set('oid', oid)
        },
        get_oid: function() {
            return this.get('oid');
        },
        set_back_order: function(backorder) {
            this.set('backorder', backorder);
        },
        get_back_order: function() {
            return this.get('backorder');
        },
        can_be_merged_with: function(orderline){
            var merged_lines = _super_orderline.can_be_merged_with.call(this, orderline);
            if(this.get_serial()) {
                return false;
            }
            if(this.get_oid() && this.pos.get('selectedOrder').get_sale_mode()) {
                return false;
            } else if ((this.get_oid() != orderline.get_oid()) && 
                            (this.get_product().id == orderline.get_product().id)) {
                return false;
            }
            return merged_lines;
        },
        merge: function(orderline){
            if (this.get_oid() || this.pos.get('selectedOrder').get_missing_mode()) {
                this.set_quantity(this.get_quantity() + orderline.get_quantity() * -1);
            } else {
                _super_orderline.merge.call(this, orderline);
            }
        },
    });

    var _super_order = instance.point_of_sale.Order.prototype;
    instance.point_of_sale.Order = instance.point_of_sale.Order.extend({
        initialize: function(attributes){
            Backbone.Model.prototype.initialize.apply(this, arguments);
            this.pos = attributes.pos; 
            this.sequence_number = this.pos.pos_session.sequence_number++;
            this.uid =     this.generateUniqueId_barcode();     //this.generateUniqueId();
            this.set({
                creationDate:   new Date(),
                orderLines:     new instance.point_of_sale.OrderlineCollection(),
                paymentLines:   new instance.point_of_sale.PaymentlineCollection(),
                name:           _t("Order ") + this.uid, 
                client:         null,
                ret_o_id:       null,
                ret_o_ref:      null,
                sale_mode:      false,
                missing_mode:   false,
            });
            this.selected_orderline   = undefined;
            this.selected_paymentline = undefined;
            this.screen_data = {};  // see ScreenSelector
            this.receipt_type = 'receipt';  // 'receipt' || 'invoice'
            this.temporary = attributes.temporary || false;
            return this;
        },
//        initialize: function(attr) {
//            ret_o_id = null,
//            ret_o_ref = null,
//            sale_mode = false,
//            missing_mode = false,
//            this.uid = this.generateUniqueId_barcode();     //this.generateUniqueId();
//            _super_order.initialize.name = _t("Order ") + this.uid;
//            _super_order.initialize.apply(this,arguments);
//        },
        generateUniqueId_barcode: function() {
            return new Date().getTime();
        },
        
        // return order

        set_sale_mode: function(sale_mode) {
            this.set('sale_mode', sale_mode);
        },
        get_sale_mode: function() {
            return this.get('sale_mode');
        },
        set_missing_mode: function(missing_mode) {
            this.set('missing_mode', missing_mode);
        },
        get_missing_mode: function() {
            return this.get('missing_mode');
        },
        set_ret_o_id: function(ret_o_id) {
            this.set('ret_o_id', ret_o_id)
        },
        get_ret_o_id: function(){
            return this.get('ret_o_id');
        },
        set_ret_o_ref: function(ret_o_ref) {
            this.set('ret_o_ref', ret_o_ref)
        },
        get_ret_o_ref: function(){
            return this.get('ret_o_ref');
        },
        addProduct: function(product, options){
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;

            var is_sale_mode = this.get_sale_mode();
            var is_missing_mode = this.get_missing_mode();

            var retoid = this.pos.get('selectedOrder').get_ret_o_id();
            var order_ref = this.pos.get('selectedOrder').get_ret_o_ref() // to add backorder in line.
            if (retoid && !is_missing_mode) {
                var pids = [];
                new instance.web.Model("pos.order.line").get_func("search_read")
                                    ([['order_id', '=', retoid],['product_id', '=', attr.id],['return_qty', '>', 0]], 
                                    ['return_qty', 'id', 'price_unit', 'discount']).pipe(
                    function(result) {
                        if (result && result.length > 0  && !is_sale_mode) {
                            var return_qty = 0;
                            _.each(result, function(res) {
                                return_qty = return_qty + res.return_qty;
                            });
                            product['remaining_qty'] = return_qty
                            if (product.remaining_qty > 0 && selectedOrder.get_ret_o_id()) {
                                $("[data-product-id='"+product.id+"'] span.remaining-qty-tag").css('display', '');
                                $("[data-product-id='"+product.id+"'] span.remaining-qty-tag").html(product.remaining_qty);
                            } else {
                                $("[data-product-id='"+product.id+"'] span.remaining-qty-tag").css('display', 'none');
                            }
                            if (return_qty > 0) {
                                add_prod = true;
                                var added_item_count = 0;
                                (attr.order.get('orderLines')).each(_.bind( function(item) {
                                    if (attr.id == item.get_product().id && item.get_oid()) {
                                        added_item_count = added_item_count + (item.quantity * -1)
                                    }
                                    if (attr.id == item.get_product().id && return_qty <= added_item_count) {
                                        var error_str = _t('Can not return more products !');
                                        var error_dialog = new instance.web.Dialog(this, { 
                                            size: 'small',
                                            buttons: [{text: _t("Close"), click: function() { this.parents('.modal').modal('hide'); }}],
                                        }).open();
                                        error_dialog.$el.append(
                                            '<span id="error_str" style="font-size:18px;">' + error_str + '</span>');
                                        add_prod = false;
                                    }
                                }, self));
                                if (add_prod) {
                                    var line = new instance.point_of_sale.Orderline({}, {pos: attr.pos, order: this, product: product});
                                    line.set_oid(retoid);
                                    line.set_back_order(order_ref);
                                    if (result[0].discount) {
                                        line.set_discount(result[0].discount);
                                    }
                                    if(options.quantity !== undefined){
                                        line.set_quantity(options.quantity);
                                    }
                                    if(options.price !== undefined){
                                        line.set_unit_price(result[0].price_unit);
                                    }
                                    line.set_unit_price(result[0].price_unit);
                                    var last_orderline = attr.order.getLastOrderline();
                                    if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                                        last_orderline.merge(line);
                                    }else{
                                        line.set_quantity(line.get_quantity() * -1)
                                        attr.order.get('orderLines').add(line);
                                    }
                                    attr.order.selectLine(attr.order.getLastOrderline());
                                }
                            } else {
                                var error_str = _t('Please check quantity of selected product & sold product !');
                                var error_dialog = new instance.web.Dialog(this, { 
                                    size: 'small',
                                    buttons: [{text: _t("Close"), click: function() { this.parents('.modal').modal('hide'); }}],
                                }).open();
                                error_dialog.$el.append(
                                    '<span id="error_str" style="font-size:18px;">' + error_str + '</span>');
                                return;
                            }
                    } else {
                        if (!is_sale_mode) {
                            var error_str = _t('Product is not in order list or try Sale Mode to add new products !');
                            var error_dialog = new instance.web.Dialog(this, { 
                                size: 'small',
                                buttons: [{text: _t("Close"), click: function() { this.parents('.modal').modal('hide'); }}],
                            }).open();
                            error_dialog.$el.append(
                                '<span id="error_str" style="font-size:18px;">' + error_str + '</span>');
                        } else {
                            var line = new instance.point_of_sale.Orderline({}, {pos: attr.pos, order: self, product: product});
                            if (retoid && retoid.toString() != 'Missing Receipt') {
                                line.set_oid(retoid);
                                line.set_back_order(order_ref);
                            }
                            if(options.quantity !== undefined){
                                line.set_quantity(options.quantity);
                            }
                            if(options.price !== undefined){
                                line.set_unit_price(options.price);
                            }
                            if(options.discount !== undefined){
                                line.set_discount(options.discount);
                            }
                            var last_orderline = attr.order.getLastOrderline();
                            if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                                last_orderline.merge(line);
                            }else{
                                attr.order.get('orderLines').add(line);
                            }
                            attr.order.selectLine(attr.order.getLastOrderline());
                        }
                    }
                });
            } else if(is_missing_mode) {
                var line = new instance.point_of_sale.Orderline({}, {pos: attr.pos, order: self, product: product});
                if (retoid) {
                    line.set_oid(retoid);
                    line.set_back_order(order_ref);
                }
                if(options.quantity !== undefined){
                    line.set_quantity(options.quantity);
                }
                if(options.price !== undefined){
                    line.set_unit_price(options.price);
                }
                if(options.discount !== undefined){
                    line.set_discount(options.discount);
                }
                var last_orderline = this.getLastOrderline();
                if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                    last_orderline.merge(line);
                }else{
                    line.set_quantity(line.get_quantity() * -1)
                    this.get('orderLines').add(line);
                }
                this.selectLine(this.getLastOrderline());
            } else {
            	var line = new instance.point_of_sale.Orderline({}, {pos: attr.pos, order: self, product: product});
            	if (this.pos.config.enable_pos_serial && (product.track_incoming || product.track_all)) {
	                var self = this;
	                new instance.web.Model("stock.production.lot").get_func("search_read")
	                            ([['product_id', '=', attr.id]]).pipe(
	                    function(result) {
	                        if (result) {
	                            initial_ids = _.map(result, function(x) {return x['id']});
	                            this.pop = new instance.web.form.SelectCreatePopup(this);
	                                this.pop.select_element(
	                                    'stock.production.lot', 
	                                    {
	                                        title: 'Select serial number for: ' + attr.display_name, 
	                                        initial_ids: initial_ids, 
	                                        initial_view: 'search',
	                                        disable_multiple_selection: true,
	                                        no_create: true
	                                    }, [], new instance.web.CompoundContext({}));
	                        }
	                        this.pop.on("elements_selected", self, function(element_ids) {
	                            var dataset = new instance.web.DataSetStatic(self, 'stock.production.lot', {});
	                            dataset.name_get(element_ids).done(function(data) {
	                                if (data) {
	                                	new instance.web.Model("stock.production.lot").get_func("check_stock_lot")(data[0][0]).pipe(
	                                        function(lot_res){
	                                            if (lot_res > 0) {
	                                             line.set_serial_id(data[0][0]);
	                                                line.set_serial(data[0][1]);
	                                                sr_no = data[0][1];
	                                                (self.get('orderLines')).each(_.bind( function(item) {
	                                                    if (item.get_product().id == attr.id && item.get_serial() == data[0][1]) {
	                                                        alert('Same product is already assigned with same serial number !');
	                                                        sr_no = null;
	                                                        return false;
	                                                    }
	                                                }, this));
	                                                if (sr_no != null) {
	                                                    if(options.quantity !== undefined){
	                                                        line.set_quantity(options.quantity);
	                                                    }
	                                                    if(options.price !== undefined){
	                                                        line.set_unit_price(options.price);
	                                                    }
	                                                    if(options.discount !== undefined){
	                                                        line.set_discount(options.discount);
	                                                    }
	                                                    var last_orderline = self.getLastOrderline();
	                                                    if (last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
	                                                        last_orderline.merge(line);
	                                                    } else {
	                                                        self.get('orderLines').add(line);
	                                                    }
	                                                    self.selectLine(self.getLastOrderline());
	                                                }
	                                            } else {
	                                                alert (_t('Not enough quantity in this serial number !'))
	                                            }
		                                    });
	                                }
	                            });
	                        });
	                    });
	            } else {
	            	_super_order.addProduct.call(this, product, options);
	            }
            }
            // Keyboad Shortcuts
            this.numpad_state = this.pos.pos_widget.numpad.state;
            this.numpad_state.set('mode', 'quantity');
            this.pos.pos_widget.numpad.changedMode();
        },
        // exports a JSON for receipt printing
        export_for_printing: function(){
            var submitted_order_printing = _super_order.export_for_printing.call(this);
            $.extend(submitted_order, {'ret_o_id': this.get_ret_o_id});
        },
        export_as_JSON: function() {
            var submitted_order = _super_order.export_as_JSON.call(this);
            parent_return_order = '';
            var ret_o_id = this.get_ret_o_id();
            var ret_o_ref = this.get_ret_o_ref();
            var return_seq = 0;
            if (ret_o_id) {
                parent_return_order = this.get_ret_o_id();
            }
            backOrders = '';
            (this.get('orderLines')).each(_.bind( function(item) {
            	if (item.get_back_order()) {
                    return backOrders += item.get_back_order() + ', ';
            	}
            }, this));
            var new_val = {
            	parent_return_order: parent_return_order, // Required to create paid return order
                return_seq: return_seq || 0,
                back_order: backOrders,
                sale_mode: this.get_sale_mode(),
            }
            $.extend(submitted_order, new_val);
            return submitted_order;
        },
    });
    
    
    //Keyboard Shortcut
    instance.point_of_sale.ProductListWidget = instance.point_of_sale.ProductListWidget.extend({
        defaults: {
            buffer: "0",
            mode: "quantity"
        },
        init: function(parent, options) {
            var self = this;
            this._super(parent,options);
            var order_widget = self.pos;
            this.state = new instance.point_of_sale.NumpadState();
            var timeStamp = 0;
            var ok = true;
            
            this.handler_find_operation = function(e){
                var token = e.which;
                var cashregisters = self.pos.cashregisters;
                var paymentLines_keys = [];

                if (!(token == 100 || token == 112 || (token >= 48 && token <= 57) 
                    || token == 190 || token == 113 || token == 46 || token == 115 || token == 8)) {
                    var flag = true;
                    _.each(cashregisters, function(paymentline){
                        if (paymentline.journal.shortcut_key && paymentline.journal.shortcut_key == String.fromCharCode(e.which)) {
                            flag = false;
                        }
                    });
                    if (flag) {
                        return
                    }
                }
                var order = self.pos.get('selectedOrder');
                oldBuffer = self.get('buffer');
                if (oldBuffer === '0' || oldBuffer == undefined) {
                    self.set({
                        buffer: String.fromCharCode(e.which)
                    });
                } else if (oldBuffer === '-0') {
                    self.set({
                        buffer: "-" + String.fromCharCode(e.which)
                    });
                } else {
                    self.set({
                        buffer: (self.get('buffer')) + String.fromCharCode(e.which)
                    });
                }
                
                var cashregisters = self.pos.cashregisters;
                var paymentLines = order.get('paymentLines');
                var paymentLines_keys = [];
                _.each(cashregisters, function(paymentline){
                    if (paymentline.journal.shortcut_key) {
                        paymentLines_keys.push(paymentline.journal.shortcut_key);
                    }
                    if (paymentline.journal.shortcut_key && paymentline.journal.shortcut_key == String.fromCharCode(e.which)) {
                        var newPaymentline = new instance.point_of_sale.Paymentline({},{cashregister:paymentline, pos:self.pos});
                        if(paymentline.journal.type !== 'cash'){
                            newPaymentline.set_amount( Math.max(order.getDueLeft(),0) );
                        }
                        
                        paymentLines.add(newPaymentline);
                        order.selectPaymentline(newPaymentline);
                        self.pos_widget.screen_selector.set_current_screen('payment');
                    }
                });
                
                if (e.which == 8 && order.getSelectedLine()) {
                    if(self.get('buffer') === ""){
                        if(self.get('mode') === 'quantity'){
                            order.getSelectedLine().set_quantity('remove');
                        }else if( self.get('mode') === 'discount'){
                            order.getSelectedLine().set_discount(self.get('buffer'));
                        }else if( self.get('mode') === 'price'){
                            order.getSelectedLine().set_unit_price(self.get('buffer'));
                        }
                    }else{
                        var newBuffer = "";
                        self.set({ buffer: newBuffer });
                        if(self.get('mode') === 'quantity'){
                            if(self.get('buffer') === "") {
                                order.getSelectedLine().set_quantity('remove');
                            } else {
                                order.getSelectedLine().set_quantity(self.get('buffer'));
                            }
                        }else if( self.get('mode') === 'discount'){
                            order.getSelectedLine().set_discount(self.get('buffer'));
                        }else if( self.get('mode') === 'price'){
                            order.getSelectedLine().set_unit_price(self.get('buffer'));
                        }
                    }
                }
                
                if (e.which == 115) {
                    $( "div.searchbox" ).find( "input" ).focus();
                    return
                } else if (e.which == 100) {
                    order_widget.pos_widget.numpad.state.set('mode', 'discount');
                    self.set({
                        buffer: "0",
                        mode: 'discount'
                    });
                    order_widget.pos_widget.numpad.changedMode();
                } else if (e.which == 113) {
                    order_widget.pos_widget.numpad.state.set('mode', 'quantity');
                    self.set({
                        buffer: "0",
                        mode: 'quantity'
                    });
                    order_widget.pos_widget.numpad.changedMode();
                } else if (e.which == 112) {
                    order_widget.pos_widget.numpad.state.set('mode', 'price');
                    self.set({
                        buffer: "0",
                        mode: 'price'
                    });
                    order_widget.pos_widget.numpad.changedMode();
                } else if (order.getSelectedLine() && e.which != 113 && e.which != 100 && e.which != 112 &&
                                   $.inArray(String.fromCharCode(e.which), paymentLines_keys) == -1) {
                    var mode = order_widget.pos_widget.numpad.state.get('mode');
                    if( mode === 'quantity'){
                        if (order.getSelectedLine().get_quantity() == 1 || order.getSelectedLine().get_quantity() == 0 ) {
                            if (self.get('buffer').length >= 1) {
                                if ((self.get('buffer').length == 2 || self.get('buffer').length == 3) && self.get('buffer').slice(0,1) == '1') {
                                    order.getSelectedLine().set_quantity(self.get('buffer'));
                                } else {
                                    var qty = self.get('buffer').split('');
                                    if(qty[qty.length-2] == '.'){
                                        self.set({
                                            buffer: qty[qty.length-1]/((qty[qty.length-1]).length*10),
                                            mode: 'quantity'
                                        });
                                        order.getSelectedLine().set_quantity(qty[qty.length-1]/((qty[qty.length-1]).length*10));
                                    }
                                    else{
                                    self.set({
                                        buffer: qty[qty.length-1],
                                        mode: 'quantity'
                                    });
                                    order.getSelectedLine().set_quantity(qty[qty.length-1]);
                                    }
                                }
                            }
                        } else {
                            order.getSelectedLine().set_quantity(self.get('buffer'));
                        }
                    }else if( mode === 'discount'){
                        order.getSelectedLine().set_discount(self.get('buffer'));
                    }else if( mode === 'price'){
                        order.getSelectedLine().set_unit_price(self.get('buffer'));
                    }
                } else {
                    return;
                }
            };

            $('body').on('keypress', function(e){
                if (timeStamp + 50 > new Date().getTime()) {
                    ok = false;
                } else {
                    ok = true;
                }
                timeStamp = new Date().getTime();
                setTimeout(function(){
                    if (ok) {self.handler_find_operation(e);}
                }, 50);
            });
            
            var rx = /INPUT|SELECT|TEXTAREA/i;
            $('body').on("keydown keypress", function(e){
                var order = self.pos.get('selectedOrder');
                if( e.which == 8 && order.getSelectedLine() ){ // 8 == backspace
                    if(!rx.test(e.target.tagName) || e.target.disabled || e.target.readOnly ){
                        e.preventDefault();
                        if (self.get('mode') == 'quantity') {
                            self.set({
                                buffer: self.get('buffer').slice(0,-1),
                                mode: 'quantity'
                            });
                            qty = self.get('buffer')
                            if (qty == '' && order.getSelectedLine().get_quantity() == 0) {
                                qty = 'remove';
                            }
                            order.getSelectedLine().set_quantity(qty);
                        }
                        if (self.get('mode') == 'discount') {
                            self.set({
                                buffer: self.get('buffer').slice(0,-1),
                                mode: 'discount'
                            });
                            order.getSelectedLine().set_discount(self.get('buffer'));
                        }
                        if (self.get('mode') == 'price') {
                            self.set({
                                buffer: self.get('buffer').slice(0,-1),
                                mode: 'price'
                            });
                            order.getSelectedLine().set_unit_price(self.get('buffer'));
                        }
                    }
                } else if (e.which == 8) {
                    if(!rx.test(e.target.tagName) || e.target.disabled || e.target.readOnly ){
                        e.preventDefault();
                    }
                }
            });
        },
    });
    
    var ReturnPaymentScreenWidget = instance.point_of_sale.PaymentScreenWidget.prototype;
    instance.point_of_sale.PaymentScreenWidget = instance.point_of_sale.PaymentScreenWidget.extend({
        validate_order: function(options) {
            var self = this;
            options = options || {};
            var currentOrder = this.pos.get('selectedOrder');
            
            ReturnPaymentScreenWidget.validate_order.call(this, options)
            currentOrder.set_ret_o_id('');
            currentOrder.set_sale_mode(true);
            currentOrder.set_missing_mode(false);
            $("span#sale_mode").css('background', 'blue');
            $("span#return_order").css('background', '');
            $("span#missing_return_order").css('background', '');
            $('#return_order_ref').html('');
            $('#return_order_number').val('');
            $("span.remaining-qty-tag").css('display', 'none');
        },
        wait: function( callback, seconds){
           return window.setTimeout( callback, seconds * 1000 );
        },
    });
    
    instance.point_of_sale.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get('selectedOrder');
            this.numpad_state = this.pos_widget.numpad.state;
            var mode = this.numpad_state.get('mode');
            if (this.editable && order.getSelectedLine()) {
                var ret_o_id = order.get_ret_o_id();
                if (ret_o_id) {
                    var prod_id = order.getSelectedLine().get_product().id;
	                if (order.get('orderLines').length !== 0) {
	                    if( mode === 'quantity'){
	                        var ret_o_id = order.get_ret_o_id();
	                        if (ret_o_id && ret_o_id.toString() != 'Missing Receipt' && val != 'remove') {
	                            var self = this;
	                            var pids = [];
	                            new instance.web.Model("pos.order.line").get_func("search_read")
	                                                ([['order_id', '=', ret_o_id],['product_id', '=', prod_id],['return_qty', '>', 0]], 
	                                                ['return_qty', 'id']).pipe(
	                                function(result) {
	                                    if (result && result.length > 0) {
	                                        if (result[0].return_qty > 0) {
	                                            add_prod = true;
	                                            (order.get('orderLines')).each(_.bind( function(item) {
	                                                if (prod_id == item.get_product().id && 
	                                                    result[0].return_qty < parseInt(val)) {
	                                                    var error_str = _t('Can not return more products !');
	                                                    var error_dialog = new instance.web.Dialog(this, { 
	                                                        size: 'small',
	                                                        buttons: [{text: _t("Close"), click: function() { this.parents('.modal').modal('hide'); }}],
	                                                    }).open();
	                                                    error_dialog.$el.append(
	                                                        '<span id="error_str" style="font-size:18px;">' + error_str + '</span>');
	                                                    add_prod = false;
	                                                }
	                                            }));
	                                        }
	                                        if (add_prod) {
	                                            if (val != 'remove') {
	                                                order.getSelectedLine().set_quantity(parseInt(val) * -1);
	                                            } else {
	                                                order.getSelectedLine().set_quantity(val)
	                                            }
	                                        }
	                                    }
	                                }
	                            );
	                        } else {
	                            order.getSelectedLine().set_quantity(val);
	                        }
	                    }else if( mode === 'discount'){
	                        order.getSelectedLine().set_discount(val);
	                    }else if( mode === 'price'){
	                        order.getSelectedLine().set_unit_price(val);
	                    }
	                } else {
	                    this.pos.get('selectedOrder').destroy();
	                }
                } else {
                	if (val != 'remove' && val != '' && order.getSelectedLine().get_serial()) {
                        alert('Can not change quantity if serial number assigned !');
                    } else {
                    	this._super(val);
                    }
                }
            }
        },
    });
    instance.web.SearchView.include({
        start: function() {
            var self = this;

            this.$view_manager_header = this.$el.parents(".oe_view_manager_header").first();

            this.setup_global_completion();
            this.query = new instance.web.search.SearchQuery()
                    .on('add change reset remove', this.proxy('do_search'))
                    .on('change', this.proxy('renderChangedFacets'))
                    .on('add reset remove', this.proxy('renderFacets'));

            if (this.options.hidden) {
                this.$el.hide();
            }
            if (this.headless) {
                this.ready.resolve();
            } else {
                var load_view = instance.web.fields_view_get({
                    model: this.dataset._model,
                    view_id: this.view_id,
                    view_type: 'search',
                    context: this.dataset.get_context(),
                });

                this.alive($.when(load_view)).then(function (r) {
                    self.fields_view_get.resolve(r);
                    return self.search_view_loaded(r);
                }).fail(function () {
                    self.ready.reject.apply(null, arguments);
                });
            }

            var view_manager = this.getParent();
            while (!(view_manager instanceof instance.web.ViewManager) &&
                    view_manager && view_manager.getParent) {
                view_manager = view_manager.getParent();
            }

//          if (view_manager) {
//              this.view_manager = view_manager;
//              if (view_manager.pop) {
//                  view_manager.pop.on('switch_mode', this, function (e) {
//                      self.drawer.toggle(e === 'graph');
//                  });
//              } else {
//                  view_manager.on('switch_mode', this, function (e) {
//                        self.drawer.toggle(e === 'graph');
//                    });
//              }
//          }
            return $.when(p, this.ready);
        },
    });
}