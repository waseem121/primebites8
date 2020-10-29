{
    'name': 'Pos Weight Customization',
    'version': '1.0',
    'category': 'Point of Sale',
    'description': """
* It supports scanning of code 128 barcode where there is no checksum digit.
* It allows scanning of weight, price and discount barcode.
* It scans price barcode and pulls right weight.
* It also supports 2D barcode scanning where barcodes should be comma separated.
* After receipt printing if user fails to click on Next Order button, then an alert message pops up.
""",
    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",
    'depends': ['point_of_sale', 'base'],
    'data': [
            'views/pos_weight_view.xml',
            ],
    'js': ['static/src/js/pos_weight_cust.js'],
    'demo': [],
    'test': [],
    'qweb': [],
    'css': [],
    'installable': True,
    'auto_install': False,          
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: