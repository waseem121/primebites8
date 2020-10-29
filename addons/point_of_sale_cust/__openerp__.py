# -*- coding: utf-8 -*-
{
    'name': "Point of Sale Customization",

    'summary': """
        Point of sale customizations
     """,

    'description': """
* Mark done wizard in picking        
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/stock_picking_done_view.xml',
        'security/pos_security.xml',
        'point_of_sale_view.xml',
        'report/pos_order_report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo.xml',
    ],
}