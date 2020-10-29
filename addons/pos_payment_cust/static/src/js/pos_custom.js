openerp.pos_payment_cust= function (instance) {

    var module = instance.point_of_sale;
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision;
    
    instance.point_of_sale.Order = instance.point_of_sale.Order.extend({
        addPaymentline: function(cashregister) {
            // If journal type is cash then also it will set due amount
            var paymentLines = this.get('paymentLines');
            var newPaymentline = new module.Paymentline({},{cashregister:cashregister, pos:this.pos});
            newPaymentline.set_amount( Math.max(this.getDueLeft(),0) );
            paymentLines.add(newPaymentline);
            this.selectPaymentline(newPaymentline);
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
            console.log("date_order: " + this.get('creationDate'));
            return {
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
                date_order: this.get('creationDate'),
            };
        },
        
    });
    
    var _super_barcode_reader = instance.point_of_sale.BarcodeReader.prototype;
    instance.point_of_sale.BarcodeReader = instance.point_of_sale.BarcodeReader.extend({
        scan: function(code){
            if(code.length < 3){
                return;
            }
            else {
                var self = this;
                var ss = self.pos.pos_widget.screen_selector;
                console.log("Current Screen: " + ss.get_current_screen());
                if(ss.get_current_screen() === 'receipt' || ss.get_current_screen() === 'payment'){
                    alert("Scanning is disabled on this screen!!!");
                }
                _super_barcode_reader.scan.call(this, code);
            }
        }
    });
    
}