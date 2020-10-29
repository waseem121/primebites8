# -*- coding: utf-8 -*-
{
    'name': "POS Global Discount",

    'summary': """
    """,

    'description': """
        Point of Sale Global Discount
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'point_of_sale_view.xml',
        'views/point_of_sale.xml',
    ],
    'qweb': ['static/src/xml/pos_custom.xml'],
    'js': ['static/src/js/pos_custom.js'],
#    'css': ['static/src/css/pos_custom.css'],
    'price': 10.00,
    'currency': 'EUR',
}