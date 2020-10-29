# -*- coding: utf-8 -*-
{
    'name': "pos_session_cust",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    ### mrp- _bom_find(); stock- one2many with stock.picking; stock_alwani- period_id in stock.picking;
    ### pos_force_period_alwani- inheriting create_picking() function
    'depends': ['base','point_of_sale'], 

    # always loaded
    'data': [
        'views/report_detailsofsales.xml',
        'views/report_session_order_summary.xml',
        'point_of_sale_report.xml',
    ],
    'qweb': [],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}