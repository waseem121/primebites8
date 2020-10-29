# -*- coding: utf-8 -*-
from openerp import http

# class PosSessionNoConstraint(http.Controller):
#     @http.route('/pos_session_no_constraint/pos_session_no_constraint/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_session_no_constraint/pos_session_no_constraint/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_session_no_constraint.listing', {
#             'root': '/pos_session_no_constraint/pos_session_no_constraint',
#             'objects': http.request.env['pos_session_no_constraint.pos_session_no_constraint'].search([]),
#         })

#     @http.route('/pos_session_no_constraint/pos_session_no_constraint/objects/<model("pos_session_no_constraint.pos_session_no_constraint"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_session_no_constraint.object', {
#             'object': obj
#         })