{
 'name' : 'Product EAN13 Management',
 'summary' : 'Auto generate EAN13 & manage multiple EAN13 for a product',
 'version' : '9.0',
 'author' : 'Emipro Technologies Pvt. Ltd.',
 'maintainer': 'Emipro Technologies Pvt. Ltd.',
 'website': 'http://www.emiprotechnologies.com',
 'category': 'Sales Management',
 'complexity': "normal",
 'depends' : ['product'], #Just add point_of_sale module inside depends to activate EAN13 search inside POS.
 'description': """
By default Odoo allows to define only one EAN for a product. \n 
 
By Installing this module you will able to, \n

* Configure Multi EAN13 for a product \n
* Configure automatic EAN13 creation at the time of product create \n
* Configure 7 digit EAN prefix as per your preference \n 
* Create EAN for multi product in single click \n
* Create EAN for multi product categories in single click \n
* Search product with secondary EAN no. \n
* Create EAN13 no. manually at any time for a product \n 

Feel free to contact us at info@emiprotechnologies.com for more customisations in Odoo. 
""",

 'data': [
          'data/product_sequence_ean.xml',
          'view/product_view.xml',
          'view/res_company_view.xml',
          'security/ir.model.access.csv',
          'wizard/set_multiple_product_ean.xml',
        #'view/templates.xml', #Just uncomment this line to activate EAN13 search inside POS.
          ],
 'installable': True,
 'images': ['static/description/main_screen.png'],
 'auto_install': False,
 'application': True,
 'price': 18.00,
 'currency': 'EUR',
}
