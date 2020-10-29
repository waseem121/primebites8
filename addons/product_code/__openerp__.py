# -*- coding: utf-8 -*-
{
    'name': "Product Code",

    'summary': """
    """,

    'description': """
        A new field is added called product code. This will be used in product name and search.
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'product_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo.xml',
    ],
}