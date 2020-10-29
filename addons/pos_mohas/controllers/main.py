# -*- coding: utf-8 -*-
import werkzeug
import simplejson

from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect

class DataSet(http.Controller):

    @http.route('/web/dataset/load_products', type='http', auth="user")
    def load_products(self, **kw):
        domain = str(kw.get('domain'))
        domain = domain.replace('true', 'True')
        domain = domain.replace('false', 'False')
        domain = eval(domain)

        ctx1 = str(kw.get('context'))
        ctx1 = ctx1.replace('true', 'True')
        ctx1 = ctx1.replace('false', 'False')
        ctx1 = eval(ctx1)
        records = []
        fields = eval(kw.get('fields'))
        cr, uid, context = request.cr, request.uid, request.context
        Model = request.session.model(kw.get('model'))
        context.update(ctx1)
        try:
            records = Model.search_read(domain, fields, 0, False, False, context)
        except Exception, e:
            print "Error......", e
        return simplejson.dumps(records)
        return ''

# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4: