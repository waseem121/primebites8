# -*- coding: utf-8 -*-
from openerp import http

# class PurchaseOrderLineScanAdv(http.Controller):
#     @http.route('/purchase_order_line_scan_adv/purchase_order_line_scan_adv/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_order_line_scan_adv/purchase_order_line_scan_adv/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_order_line_scan_adv.listing', {
#             'root': '/purchase_order_line_scan_adv/purchase_order_line_scan_adv',
#             'objects': http.request.env['purchase_order_line_scan_adv.purchase_order_line_scan_adv'].search([]),
#         })

#     @http.route('/purchase_order_line_scan_adv/purchase_order_line_scan_adv/objects/<model("purchase_order_line_scan_adv.purchase_order_line_scan_adv"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_order_line_scan_adv.object', {
#             'object': obj
#         })