openerp.pos_weight_cust = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;
    var module = instance.point_of_sale;
    var select_query = '';
    var config = '';
    var config_price = '';
    var config_disc = '';
    var search_options = {};
   
    instance.point_of_sale.Order = instance.point_of_sale.Order.extend({
        init: function(parent, options){
            var self = this;
            this._super(parent,options); 
        },
       addProduct: function(product, options){
            console.log("product: " + JSON.stringify(product));
            if (product.to_weight === true){
                d_code = product.default_code;
            }
            else  {
                d_code = product.ean13;
            }
//            if(product.ean13){
//                d_code = product.ean13;
//            }
//            else
//            {
//                d_code = product.default_code;
//            }
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});
            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
//            if(options.price !== undefined){
//                line.set_unit_price(options.price);
//            }
            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }
            var barcode = select_query ? select_query : d_code;
            console.log("barcode: " + barcode);
            line.set_barcode(barcode);
            
            if(this.pos.config.barcode_weight && (options.quantity || search_options.quantity)){
//                console.log("barcode_weight");
                weight = this.pos.config.barcode_weight
                k = weight.split("N").length - 1;
                d = weight.split("D").length - 1;
                if((weight.length-2-k-d) == d_code.length){
                    if (weight && select_query && weight.substring(0,2) == select_query.substring(0,2)){
                        l = select_query.length;
                        s = l - (k + d);
                        if ( !(isNaN(select_query.substring(s, select_query.length)))){
                            qty = parseFloat(select_query.substring(s, l))
                            count = 0;
                            stringsearch = 'D';
                            for(var i=count=0; i<weight.length; count+=+(stringsearch===weight[i++]));
                            count = Math.pow(10, count)
                            weight_disc = parseFloat(qty)/parseFloat(count);
                            line.set_quantity(weight_disc);
                        }
                    }
                }
                
            }
            if(this.pos.config.barcode_price && (options.price || search_options.price)){
//                console.log("barcode_price");
                price = this.pos.config.barcode_price
                k = price.split("N").length - 1;
                d = price.split("D").length - 1;
                if((price.length-2-k-d) === d_code.length){
                    if (price && select_query && price.substring(0,2) === select_query.substring(0,2)){
                        l = select_query.length;
                        s = l - (k + d);
                        if ( !(isNaN(select_query.substring(s, select_query.length)))){
                            pr = parseFloat(select_query.substring(s, l))
                            count = 0;
                            stringsearch = 'D';
                            for(var i=count=0; i<price.length; count+=+(stringsearch===price[i++]));
                            count = Math.pow(10, count)
                            price_disc = parseFloat(pr)/parseFloat(count);
//                            alert("price_disc: " + price_disc);
                            quantity = price_disc / product.price;
                            line.set_quantity(quantity);
                            line.set_price_data(price_disc);
//                            line.set_unit_price(price_disc);
                        }
                    }
                }
                
            }
            if(this.pos.config.barcode_discount && (options.discount || search_options.discount)){
//                console.log("barcode_discount");
                discount = this.pos.config.barcode_discount
                k = discount.split("N").length - 1;
                if((discount.length-2-k) == d_code.length){
                    if (discount && select_query && discount.substring(0,2) == select_query.substring(0,2)){
                        l = select_query.length;
                        if ( !(isNaN(select_query.substring(2, select_query.length)))){
                            disc = parseFloat(select_query.substring(2, l))
                            count = 0;
                            stringsearch = 'N';
                            for(var i=0; i < discount.length; i++)
                            {
                                if(stringsearch===discount[i])
                                {
                                    count = count + 1;
                                }
                            }
                            k = l - count
                            disc_d = parseFloat(select_query.substring(k, l));
                            line.set_discount(disc_d);
                        }
                    }
                }
            }
            var last_orderline = this.getLastOrderline();
            if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                last_orderline.merge(line);
            }else{
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
            search_options = {};
            select_query = false;
        },
    });
    
    instance.point_of_sale.ProductCategoriesWidget = instance.point_of_sale.ProductCategoriesWidget.extend({
        init: function(parent, options){
            var self = this;
            this._super(parent,options);
            this.product_type = options.product_type || 'all';  // 'all' | 'weightable'
            this.onlyWeightable = options.onlyWeightable || false;
            this.category = this.pos.root_category;
            this.breadcrumb = [];
            this.subcategories = [];
            this.product_list_widget = options.product_list_widget || null;
            this.category_cache = new module.DomCache();
            this.set_category();
            
            this.switch_category_handler = function(event){
                self.set_category(self.pos.db.get_category_by_id(Number(this.dataset['categoryId'])));
                self.renderElement();
            };
            
            this.clear_search_handler = function(event){
                self.clear_search();
            };

            var search_timeout  = null;
            this.search_handler = function(event){
                clearTimeout(search_timeout);
               
                var query = this.value;

                search_timeout = setTimeout(function(){
                    self.perform_search(self.category, query, event.which === 13);
                },70);
            };
            config = this.pos.config.barcode_weight;
            config_price = this.pos.config.barcode_price;
            config_disc = this.pos.config.barcode_discount;
        },
        clear_search: function(){
            var products = this.pos.db.get_product_by_category(this.category.id);
            this.product_list_widget.set_product_list(products);
            var input = this.el.querySelector('.searchbox input');
                input.value = '';
                input.focus();
            select_query = '';
        },
    });
    
    instance.point_of_sale.PosDB = instance.point_of_sale.PosDB.extend({
        search_product_in_category: function(category_id, query){
            l = query.length;
            select_query = query;
            if(l > 2){
                if(l == config.length && query.substring(0,2) == config.substring(0,2)){
                    k = config.split("N").length - 1;
                    d = config.split("D").length - 1;
                    query = query.substring(2,l-k-d);
                    search_options = {'weight': true};
                }
                if(l == config_price.length && query.substring(0,2) == config_price.substring(0,2)){
                    k = config_price.split("N").length - 1;
                    d = config_price.split("D").length - 1;
                    query = query.substring(2,l-k-d);
                    search_options = {'price': true};
                }
                if(l == config_disc.length && query.substring(0,2) == config_disc.substring(0,2)){
                    k = config_disc.split("N").length - 1;
                    d = config_price.split("D").length - 1;
                    query = query.substring(2,l-k-d);
                    search_options = {'price': discount};
                }
            }
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(' ','.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            
            var results = [];
            for(var i = 0; i < this.limit; i++){
                r = re.exec(this.category_search_string[category_id]);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_product_by_id(id));
                }else{
                    break;
                }
            }
            results = _.uniq(results)
            return results;
        },
        
    });
    
    
    instance.point_of_sale.BarcodeReader = instance.point_of_sale.BarcodeReader.extend({
        add_barcode_patterns: function(patterns){
            this.patterns = this.patterns || {};
            for(type in patterns){
                this.patterns[type] = this.patterns[type] || [];

                var patternlist = patterns[type];
                if( typeof patternlist === 'string'){
                    patternlist = patternlist.split(',');
                }
                for(var i = 0; i < patternlist.length; i++){
                    var pattern = patternlist[i].trim().substring(0,13);
                    if(!pattern.length){
                        continue;
                    }
                    pattern = pattern.replace(/[x\*]/gi,'x');
                    while(pattern.length < 12){
                        pattern += 'x';
                    }
                    this.patterns[type].push(pattern);
                }
            }

            this.sorted_patterns = [];
            for (var type in this.patterns){
                var patterns = this.patterns[type];
                for(var i = 0; i < patterns.length; i++){
                    var pattern = patterns[i];
                    var score = 0;
                    for(var j = 0; j < pattern.length; j++){
                        if(pattern[j] != 'x'){
                            score++;
                        }
                    }
                    this.sorted_patterns.push({type:type, pattern:pattern,score:score});
                }
            }
            this.sorted_patterns.sort(function(a,b){
                return b.score - a.score;
            });

        },

        match_pattern: function(reference,pattern){
            
                function is_number(char){
                    n = char.charCodeAt(0);
                    return n >= 48 && n <= 57;
                }
                for(var i = 0; i < pattern.length; i++){
                    var p = pattern[i];
                    var e = reference[i];
                    if( is_number(p) && p !== e ){
                        return false;
                    }
                }
                return true;
        },
        get_value: function(reference,pattern){
                var value = 0;
                var decimals = 0;
                for(var i = 0; i < pattern.length; i++){
                    var p = pattern[i];
                    var v = parseInt(reference[i]);
                    if( p === 'N'){
                        value *= 10;
                        value += v;
                    }else if( p === 'D'){
                        decimals += 1;
                        value += v * Math.pow(10,-decimals);
                    }
                }
                return value;
        },
        scan: function(full_code){
//            alert(full_code);
            if (this.pos.get('selectedOrder')._printed) {
                alert("Click on Next Order to contune!!!");
                return false;
            }
//            alert('innn');
//            full_code = "2198765400202,2398765450000,2298765450000,2112345640000,2212345640000,2312345640000";
            codes  = full_code.trim().split(",");
//            alert(codes.length);
            for(s=0; s < codes.length; s++){
                code = codes[s];
                console.log("code: " + code);
                ccode = parseInt(code.substring(0,2));
                price = parseInt(this.pos.config.barcode_price.substring(0,2));
                discount = parseInt(this.pos.config.barcode_discount.substring(0,2));
                weight = parseInt(this.pos.config.barcode_weight.substring(0,2));
                //Get N and D length
                if (ccode == weight) {
                    k = this.pos.config.barcode_weight.split("N").length - 1;
                    d = this.pos.config.barcode_weight.split("D").length - 1;
                }
                else if (ccode == price) {
                    k = this.pos.config.barcode_price.split("N").length - 1;
                    d = this.pos.config.barcode_price.split("D").length - 1;
                }
                else if (ccode == discount) {
                    k = this.pos.config.barcode_discount.split("N").length - 1;
                    d = this.pos.config.barcode_discount.split("D").length - 1;
                }
                
                if(code.length < 3){
                    return;
                }
                else if(code.length === 13 && this.check_ean(code) && ccode != weight && ccode != price && ccode != discount){
                    var parse_result = this.parse_ean(code);
                }
                else if(code.length == 13 && (ccode == weight || ccode == price || ccode == discount)){
                    code = code.slice(0, -1);
                    select_query = code;
                    var patterns = this.sorted_patterns;
                    for(var j = 0; j < patterns.length; j++){
                        if(this.match_pattern(code, patterns[j].pattern)){
                            count = patterns[j].pattern.replace(/[0-9]/g, '');
                            break;
                        }
                    }
                    rcode = code.substring(2,code.length-(k+d));
                    var parse_result = {
                        encoding: 'reference',
                        type:'error',  
                        code : rcode,
                        base_code : rcode,
                        value: 0,
                    };
                    if(this.pos.db.get_product_by_reference(rcode)){
                        var patterns = this.sorted_patterns;
                        for(var i = 0; i < patterns.length; i++){
                            if(this.match_pattern(code, patterns[i].pattern)){
                                parse_result.type  = patterns[i].type;
                                parse_result.value = this.get_value(code,patterns[i].pattern);
                                parse_result.base_code = rcode;
                                break;
                            }
                        }

                    }
                }
                else if(this.pos.db.get_product_by_reference(code)){
                    var parse_result = {
                        encoding: 'reference',
                        type: 'product',
                        code: code,
                    };
                }
                else{
                    var parse_result = {
                        encoding: 'error',
                        type: 'error',
                        code: code,
                    };
                }
                if(parse_result.type in {'product':'', 'weight':'', 'price':'', 'discount' : ''}){    //ean is associated to a product
                    if(this.action_callback['product']){
                        this.action_callback['product'](parse_result);
                    }
                }
                else{

                    if(this.action_callback[parse_result.type]){
                        this.action_callback[parse_result.type](parse_result);
                    }
                }
            }
        },     
    });
    
//   instance.point_of_sale.PosModel = instance.point_of_sale.PosModel.extend({
//        init: function(parent, options){
//            var self = this;
//            this._super(parent,options);
//        },
//        scan_product: function(parsed_code){
//            var self = this;
//            var selectedOrder = this.get('selectedOrder');
//            if(parsed_code.encoding === 'ean13'){
//                var product = this.db.get_product_by_ean13(parsed_code.base_code);
//                if (product == undefined){
//                    var product = this.db.get_product_by_reference(parsed_code.code)
//                }
//            }
//            else if(parsed_code.encoding === 'reference'){
//                var product = this.db.get_product_by_reference(parsed_code.code);
//            }
//
//            if(!product){
//                return false;
//            }
//            
//            unic = true;
//            if(parsed_code.type == 'price'){
//                selectedOrder.addProduct(product, {price:parsed_code.value});
//            }else if(parsed_code.type == 'weight'){
//                selectedOrder.addProduct(product, {quantity:parsed_code.value, merge:false});
//            }else if(parsed_code.type == 'discount'){
//                selectedOrder.addProduct(product, {discount:parsed_code.value, merge:false});
//            }else{
//                selectedOrder.addProduct(product);
//            }
//            return true;
//        },
//   });
   
//   var OrderlineParent = module.Orderline;
   var _super_orderline = instance.point_of_sale.Orderline.prototype;
   module.Orderline = module.Orderline.extend({
       initialize: function (attr, options) {
//            OrderlineParent.prototype.initialize.apply(this, arguments);
            this.price_data = false;
            this.adjustment = 0.0;
            this.barcode = false;
            _super_orderline.initialize.call(this, attr, options);
        },
        
        get_barcode: function(){
            return this.barcode;
        },
        
        set_barcode: function(value){
            this.barcode = value;
        },
        
        get_adjustment: function(){
            return this.adjustment;
        },
        
        set_adjustment: function(value){
            this.adjustment = value;
        },
        
        get_price_data: function(){
            return this.price_data;
        },
        
        set_price_data: function(value){
            this.price_data = value;
        },
        
        get_base_price: function(){
           /// With price barcode if price does not match exactly then we have to forcefully set the barcode price
            price_data = this.get_price_data(); 
            var rounding = this.pos.currency.rounding;
            var adjustment = 0.0;
//            console.log("unit_price quantity: " + this.get_unit_price() + " " + this.get_quantity());
            base_price = round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
            price_data = round_pr(price_data * (1 - this.get_discount()/100), rounding); // discount should be applied to price_data also
//            console.log("price_data base_price discount: " + price_data + " " + base_price + " " + this.get_discount());
            if ((price_data && base_price !== price_data) || this.get_discount() === 100.0) {
                adjustment = round_pr(price_data - base_price, rounding);
                this.set_adjustment(adjustment);
                base_price = base_price + adjustment;
            }
            return base_price;
        },
        
        get_all_prices: function(){
            var base = this.get_base_price();
            var totalTax = base;
            var totalNoTax = base;
            var taxtotal = 0;

            var product =  this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes =  this.pos.taxes;
            var taxdetail = {};
            var product_taxes = [];

            _(taxes_ids).each(function(el){
                product_taxes.push(_.detect(taxes, function(t){
                    return t.id === el;
                }));
            });

            var all_taxes = _(this.compute_all(product_taxes, base)).flatten();

            _(all_taxes).each(function(tax) {
                if (tax.price_include) {
                    totalNoTax -= tax.amount;
                } else {
                    totalTax += tax.amount;
                }
                taxtotal += tax.amount;
                taxdetail[tax.id] = tax.amount;
            });
            totalNoTax = round_pr(totalNoTax, this.pos.currency.rounding);

            return {
                "priceWithTax": totalTax,
                "priceWithoutTax": totalNoTax,
                "tax": taxtotal,
                "taxDetails": taxdetail,
            };
        },
        
        set_quantity: function(quantity){
            if(quantity === 'remove'){
                this.order.removeOrderline(this);
                return;
            }
            if (this.get_price_data()) {
                return;
            }
            return _super_orderline.set_quantity.call(this, quantity);
        },
        
        set_unit_price: function(price){
            if (this.get_price_data()) {
                return;
            }
            return _super_orderline.set_unit_price.call(this, price);
        },
        
//        set_discount: function(discount){
//            console.log("set_discount new called");
////            if (this.get_price_data()) {
////                return;
////            }
//            return _super_orderline.set_discount.call(this, discount);
//        },
        
        export_as_JSON: function() {
            var lines = _super_orderline.export_as_JSON.call(this);
            new_val = {
                adjustment: this.get_adjustment(),
                barcode: this.get_barcode(),
            };
            $.extend(lines, new_val);
            return lines;
        }
   });
    
};
