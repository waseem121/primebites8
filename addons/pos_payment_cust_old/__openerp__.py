# -*- coding: utf-8 -*-
{
    'name': "POS Payment Customization",

    'summary': """
    """,

    'description': """
1. disable the scanning of barcode in the payment screen or else disable any values in the payment screen greater than 1000
2. make the option to make the payment line with the net payment instead of actual and change . Change should be there in the printout.
3. default the payment amount for cash payment with the sale amount
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
#        'templates.xml',
        'views/templates.xml',
    ],
    'js': [
        'static/src/js/pos_custom.js',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo.xml',
    ],
}