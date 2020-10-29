openerp.purchase_order_line_scan_adv = function (instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    local.HomePage = instance.Widget.extend({
        events: {
            "click .scan_button": "perform_scan",
            "click .btn-default": "quit",
        },
        
        init: function(parent, context) {
            this._super(parent);
            this.active_id = context.context.order_id;
        },
        
        perform_scan: function() {
            var self = this;
            var barcode = this.$(".barcode_field").val();
            var quantity = this.$(".quantity_field").val();
            console.log("inside perform_scan: " + barcode.length);
            if (barcode.length < 1 || quantity.length < 1) {
                dialog = new instance.web.Dialog(this, {
                    title: _t("Fields cannot be empty!!!"),
                    buttons: [
                        {text: _t("OK"), click: function() { this.parents('.modal').modal('hide'); }}
                    ]
                }).open();
            }
            var purchaseOrderLineModel = new instance.web.Model('purchase.order.line');
            return purchaseOrderLineModel.call('create_from_ui', [
                this.active_id, barcode, quantity]
            ).then(function (line_id) {
                console.log("line_id: " + line_id);
                self.$(".barcode_field").val('').focus();
                self.$(".quantity_field").val('');
            });
        },
        quit: function(){
            console.log("Window Location: " + this.active_id.toString());
            var self = this;
            return new instance.web.Model("ir.model.data").get_func("search_read")([['name', '=', 'purchase_rfq']], ['res_id']).pipe(function(res) {
                    var path = '/web#id=' + self.active_id.toString() + '&view_type=form&model=purchase.order&action=' + res[0]['res_id']
//                    var path = '/web#id=13&view_type=form&model=purchase.order&action=' + res[0]['res_id']
                    console.log("path: " + path);
                    window.location = path;
                });
        },
        start: function() {
            console.log("pet store home page loaded: " + this.order_id);
//            this.$el.append("<div>Hello dear Odoo user!</div>");
            this.$el.prepend(QWeb.render("order_line_scan"));
            this.$(".barcode_field").focus();
        },
    });
    
    instance.web.client_actions.add('purchase_order_line_scan_view', 'instance.purchase_order_line_scan_adv.HomePage');
}