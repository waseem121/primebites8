openerp.pos_global_discount = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    var round_di = instance.web.round_decimals;
    disc_check = false;
    disc_check1 = false;
    use_disc = 0.00;
    tot = 0.0
    type = ''
    
    instance.point_of_sale.PaymentScreenWidget = instance.point_of_sale.PaymentScreenWidget.extend({
        init: function() {
            this._super.apply(this, arguments);
        },
        
        get_discount_on_order:function(){
            var discount = use_disc;
            return discount
        },
        show: function(){
            this._super();
            var self = this;

            this.add_action_button({
                    label: _t('(%)'),
                    icon: '/pos_global_discount/static/src/img/PercentageDiscount.png',
                    click: function(){  
                        self.apply_discount();
                    },
                });
            this.add_action_button({
                    label: _t('(Fixed)'),
                    icon: '/pos_global_discount/static/src/img/FixedDiscount.png',
                    click: function(){  
                        self.apply_fixed_discount();
                    },
                });
        },  
        
        apply_fixed_discount:function(){
            var self = this;
            pos = self.pos;
            pos = pos;
            selectedOrder = pos.get('selectedOrder');
            dialog = new instance.web.Dialog(this, {
                title: _t("Order Fixed Discount"),
                buttons: [{
                        text: _t("Apply"), click: function(){
                            var inp_val = dialog.$el.find("input#fixed_discount_on_order").val();
                            if(selectedOrder.getTotalTaxIncluded() < inp_val){
                                alert('Amount must be greater');
                            }
                            else{
                                disc_check1 = true;
                                disc_check = true;
                                use_disc = parseFloat(inp_val)
                                this.parents('.modal').modal('hide');
                                self.update_discount_summary();
                                self.update_payment_summary();
                            }
                        }
                    },
                    {text: _t("Cancel"), click: function() { this.parents('.modal').modal('hide'); }}
                    ]
           }).open();
           dialog.$el.html(QWeb.render("discount-on-fixed-order-view", self));
           dialog.$el.find("input#fixed_discount_on_order").focus();
        },
        
        apply_discount:function(){
            var self = this;
           pos = self.pos;
           pos = pos;
           var def_discount = this.pos.config.discount;
           var pwd_discount = this.pos.config.password_discount;
           selectedOrder = pos.get('selectedOrder');
           dialog = new instance.web.Dialog(this, {
                title: _t("Order Discount"),
                buttons: [
                    {text: _t("Apply"), click: function(){
                        var inp_val = dialog.$el.find("input#discount_on_order").val();
                        var pwd_inp_val = dialog.$el.find("input#discount_password").val();
                       
                        if (def_discount && inp_val > def_discount){
                            if (pwd_inp_val == pwd_discount){
                                    pos = self.pos;
                                    selectedOrder = pos.get('selectedOrder');
                                    selectedOrder.get('orderLines').each(function(orderline){
                                        orderline.set_discount(inp_val);
                                    });
                                    this.parents('.modal').modal('hide');
                                    self.update_discount_summary();
                                    self.update_payment_summary();
                                    if( type !== 'cash'){
                                        self.set_value(tot);
                                    }
                            }
                            else
                            {
                                alert('Invalid Password');
                                dialog.$el.find("input#discount_password").focus();
                            }
                        }
                        else{
                            pos = self.pos;
                            selectedOrder = pos.get('selectedOrder');
                            selectedOrder.get('orderLines').each(function(orderline){
                                orderline.set_discount(inp_val);
                            });
                            this.parents('.modal').modal('hide');
                            self.update_discount_summary();
                            self.update_payment_summary();
                            if( type !== 'cash'){
                                self.set_value(tot);
                            }
                        }
                       
                        }
                    },
                    {text: _t("Cancel"), click: function() { this.parents('.modal').modal('hide'); }}
                    ]
           }).open();
           dialog.$el.html(QWeb.render("discount-on-order-view", self));
           dialog.$el.find("input#discount_on_order").focus();
           dialog.$el.find("input#discount_password").attr("disabled", true);
           $("input#discount_on_order").keyup(function(event) {
            var inp_val = dialog.$el.find("input#discount_on_order").val();
            if (def_discount && inp_val > def_discount){
                dialog.$el.find("input#discount_password").removeAttr("disabled");
            }
            else
                {
                    dialog.$el.find("input#discount_password").val('');
                    dialog.$el.find("input#discount_password").attr("disabled", true);
                }
           });
        },
         
         update_payment_summary: function() {
            var currentOrder = this.pos.get('selectedOrder');
            var paidTotal = currentOrder.getPaidTotal();
            var dueTotal = currentOrder.getTotalTaxIncluded();
            var remaining = dueTotal > paidTotal ? dueTotal - paidTotal : 0;
            var change = paidTotal > dueTotal ? paidTotal - dueTotal : 0;
            tot = dueTotal;
            this.$('.payment-due-total').html(this.format_currency(dueTotal));
            this.$('.payment-paid-total').html(this.format_currency(paidTotal));
            this.$('.payment-remaining').html(this.format_currency(remaining));
            this.$('.payment-change').html(this.format_currency(change));
            if(currentOrder.selected_orderline === undefined){
                remaining = 1;  // What is this ? 
            }
                
            if(this.pos_widget.action_bar){
                this.pos_widget.action_bar.set_button_disabled('validation', !this.is_paid());
                this.pos_widget.action_bar.set_button_disabled('invoice', !this.is_paid());
            }
        },
        update_discount_summary: function() {
            this.$('.payment-fixed-discount').html(this.format_currency(use_disc));
        },
         
        validate_order: function(options) {
            var self = this;
            options = options || {};

            var currentOrder = this.pos.get('selectedOrder');

            if(currentOrder.get('orderLines').models.length === 0){
                this.pos_widget.screen_selector.show_popup('error',{
                    'message': _t('Empty Order'),
                    'comment': _t('There must be at least one product in your order before it can be validated'),
                });
                return;
            }

            var plines = currentOrder.get('paymentLines').models;
            for (var i = 0; i < plines.length; i++) {
                if (plines[i].get_type() === 'bank' && plines[i].get_amount() < 0) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Negative Bank Payment'),
                        'comment': _t('You cannot have a negative amount in a Bank payment. Use a cash payment method to return money to the customer.'),
                    });
                    return;
                }
		else if (plines[i].get_amount() > 1000) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        'message': _t('Amount Too Large'),
                        'comment': _t('You cannot have an amount greater than 1000.'),
                    });
                    return;
                }
            }
            if (disc_check == false){
                if(!this.is_paid()){
                    return;
                }
            }
            else
            {
                disc_check1 = disc_check;
            }

            // The exact amount must be paid if there is no cash payment method defined.
            if (Math.abs(currentOrder.getTotalTaxIncluded() - currentOrder.getPaidTotal()) > 0.00001) {
                var cash = false;
                for (var i = 0; i < this.pos.cashregisters.length; i++) {
                    cash = cash || (this.pos.cashregisters[i].journal.type === 'cash');
                }
                if (!cash) {
                    this.pos_widget.screen_selector.show_popup('error',{
                        message: _t('Cannot return change without a cash payment method'),
                        comment: _t('There is no cash payment method available in this point of sale to handle the change.\n\n Please pay the exact amount or add a cash payment method in the point of sale configuration'),
                    });
                    return;
                }
            }

            if (this.pos.config.iface_cashdrawer) {
                    this.pos.proxy.open_cashbox();
            }

            if(options.invoice){
                // deactivate the validation button while we try to send the order
                this.pos_widget.action_bar.set_button_disabled('validation',true);
                this.pos_widget.action_bar.set_button_disabled('invoice',true);

                var invoiced = this.pos.push_and_invoice_order(currentOrder);

                invoiced.fail(function(error){
                    if(error === 'error-no-client'){
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('An anonymous order cannot be invoiced'),
                            comment: _t('Please select a client for this order. This can be done by clicking the order tab'),
                        });
                    }else{
                        self.pos_widget.screen_selector.show_popup('error',{
                            message: _t('The order could not be sent'),
                            comment: _t('Check your internet connection and try again.'),
                        });
                    }
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                });

                invoiced.done(function(){
                    self.pos_widget.action_bar.set_button_disabled('validation',false);
                    self.pos_widget.action_bar.set_button_disabled('invoice',false);
                    self.pos.get('selectedOrder').destroy();
                });

            }else{
                this.pos.push_order(currentOrder) 
                if(this.pos.config.iface_print_via_proxy){
                    var receipt = currentOrder.export_for_printing();
                    this.pos.proxy.print_receipt(QWeb.render('XmlReceipt',{
                        receipt: receipt, widget: self,
                    }));
                    this.pos.get('selectedOrder').destroy();    //finish order and go back to scan screen
                }else{
                    this.pos_widget.screen_selector.set_current_screen(this.next_screen);
                }
            }

            // hide onscreen (iOS) keyboard 
            setTimeout(function(){
                document.activeElement.blur();
                $("input").blur();
            },250);
            use_disc = 0.00;
            disc_check = false;
            disc_check1 = false;
        },
       
    });
    
    instance.point_of_sale.Paymentline = instance.point_of_sale.Paymentline.extend({
        initialize: function(attributes, options) {
            this.amount = 0;
            this.cashregister = options.cashregister;
            type = this.cashregister.journal.type
            this.name = this.cashregister.journal_id[1];
            this.selected = false;
            this.pos = options.pos;
        },
        set_amount: function(value){
            this.amount = round_di(parseFloat(value) || 0, this.pos.currency.decimals);
            this.trigger('change:amount',this);
        },
        get_amount: function(){
            amt = this.amount;
            return amt;
        },
    }),
            
    instance.point_of_sale.Order = instance.point_of_sale.Order.extend({
        get_discount_on_order:function(){
            var discount = use_disc;
            return discount
        },
        getTotalTaxIncluded: function() {
            if (disc_check === true){
                return (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_with_tax() ;
            }), 0) - use_disc;
            }
            else
            {
                return (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_with_tax();
            }), 0);
            }
            
        },
        export_as_JSON: function() {
            var orderLines, paymentLines;
            orderLines = [];
            (this.get('orderLines')).each(_.bind( function(item) {
                return orderLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            paymentLines = [];
            (this.get('paymentLines')).each(_.bind( function(item) {
                return paymentLines.push([0, 0, item.export_as_JSON()]);
            }, this));
            if (disc_check1 == true)
            {
                mydic = {
                name: this.getName(),
                amount_paid: this.getPaidTotal(),
                amount_total: this.getTotalTaxIncluded(),
                amount_tax: this.getTax(),
                amount_return: this.getChange(),
                lines: orderLines,
                statement_ids: paymentLines,
                pos_session_id: this.pos.pos_session.id,
                partner_id: this.get_client() ? this.get_client().id : false,
                user_id: this.pos.cashier ? this.pos.cashier.id : this.pos.user.id,
                uid: this.uid,
                sequence_number: this.sequence_number,
                disc_checked: disc_check1,
                disc_amount: this.get_discount_on_order(),
            };
            }
            else
            {
                mydic = {
                name: this.getName(),
                amount_paid: this.getPaidTotal(),
                amount_total: this.getTotalTaxIncluded(),
                amount_tax: this.getTax(),
                amount_return: this.getChange(),
                lines: orderLines,
                statement_ids: paymentLines,
                pos_session_id: this.pos.pos_session.id,
                partner_id: this.get_client() ? this.get_client().id : false,
                user_id: this.pos.cashier ? this.pos.cashier.id : this.pos.user.id,
                uid: this.uid,
                sequence_number: this.sequence_number,
                
                };
            }
            return mydic;
        },
        getPaidTotal: function() {
                return (this.get('paymentLines')).reduce((function(sum, paymentLine) {
                return sum + paymentLine.get_amount();
            }), 0);
        },
        getTotalAmount: function() {
                return (this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_with_tax();
            }), 0)- use_disc;
            
        },
    });
};
