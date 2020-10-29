# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, _
from reportlab.graphics import barcode 
from base64 import b64encode
from openerp.exceptions import Warning


class product_barcode_report_templete(models.AbstractModel):
    _name = 'report.aces_barcode_label.product_barcode_report_template'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('aces_barcode_label.product_barcode_report_template')
        docargs = {
           'doc_ids': self.env["aces.small.barcode.label"].browse(data["ids"]),
           'doc_model': report.model,
           'docs': self,
           'get_label_data': self._get_label_data,
           'draw_style': self._draw_style,
           'data': data
        }
        if 'ean13' in [x.name for x in self.env['aces.small.barcode.label.line'].browse(data['form']['field_lines'])] \
            and data['form']['barcode_type']:
            for product in self.env['aces.small.product.label.qty'].browse(data['form']['product_lines']):
                if not product.product_id.ean13:
                    continue
                try:
                    barcode_str = barcode.createBarcodeDrawing(
                                    data['form']['barcode_type'], value=product.product_id.ean13, format='png', width=2000, height=2000)
                except:
                    raise Warning('Select valid barcode type according product barcode value !')
        return report_obj.render('aces_barcode_label.product_barcode_report_template', docargs)

    def _get_barcode_string(self, ean13, data):
       barcode_str = barcode.createBarcodeDrawing(
                           data['barcode_type'], value=ean13, format='png', width=2000,
                           height=2000)
       encoded_string = b64encode(barcode_str.asString('png'))
       barcode_str = "<img style='width:" + str(data['disp_width']) + "px;height:" + str(data['disp_height']) + "px;' src='data:image/png;base64,{0}'>".format(encoded_string)
       return barcode_str

    def _get_label_data(self, form):
        currency_symbol = ''
        company_obj = self.env['res.company']
        if form['currency_id']:
            currency_symbol = self.env['res.currency'].browse(form['currency_id'][0]).symbol
        line_ids = []
        selected_fields = {}
        for line in self.env['aces.small.barcode.label.line'].browse(form['field_lines']):
            selected_fields.update({line.sequence : line.name})
        for product in self.env['aces.small.product.label.qty'].browse(form['product_lines']):
            product_dict = {}
            if 'ean13' in selected_fields.values() and not product.product_id.ean13:
                continue
            product_data = product.product_id.read(selected_fields.values())
            for key, value in selected_fields.iteritems():
                if product_data[0].get(value):
                    if value == 'ean13':
                        barcode_str = self._get_barcode_string(product_data[0].get(value), form)
                        if barcode_str:
                            product_dict.update({key: barcode_str})
                    elif value == 'lst_price':
                        if form['currency_position'] == 'before':
                            product_dict.update({key: currency_symbol + ' ' + str(product_data[0].get(value))})
                        else:
                            product_dict.update({key: str(product_data[0].get(value)) + ' ' + currency_symbol})
                    elif value == "company_id":
                        company_id = company_obj.search([], order="id", limit=1)
                        if company_id:
                            product_dict.update({key: company_id.name})
                    else:
                        product_dict.update({key: product_data[0].get(value)})
            for no in range(0, product.qty):
                line_ids.append(product_dict)
        return line_ids

    def _draw_style(self, data, field):
        style = ''
        selected_fields = {}
        flag = False
        for line in self.env['aces.small.barcode.label.line'].browse(data['field_lines']):
            selected_fields.update({line.name: str(line.font_size) + '-' + (line.font_color or 'black') + '-' + str(line.text_margin_top or 0)})
        for product in self.env['aces.small.product.label.qty'].browse(data['product_lines']):
            if product.product_id.name == field:
                style = 'font-size:' + str(selected_fields.get('name').split('-')[0]) + 'px;margin-top:' + str(selected_fields.get('name').split('-')[2]) + 'px;color:' + str(selected_fields.get('name').split('-')[1]) + ';'
                flag = True
            elif product.product_id.default_code == field:
                style = 'font-size:' + str(selected_fields.get('default_code').split('-')[0]) + 'px;margin-top:' + str(selected_fields.get('default_code').split('-')[2]) + 'px;color:' + str(selected_fields.get('default_code').split('-')[1]) + ';'
                flag = True
            elif str(product.product_id.lst_price) in field:
                style = 'font-size:' + str(selected_fields.get('lst_price').split('-')[0]) + 'px;margin-top:' + str(selected_fields.get('lst_price').split('-')[2]) + 'px;color:' + str(selected_fields.get('lst_price').split('-')[1]) + ';'
                flag = True
            elif not flag and selected_fields.get('company_id'):
                style = 'font-size:' + str(selected_fields.get('company_id').split('-')[0]) + 'px;margin-top:' + str(selected_fields.get('company_id').split('-')[2]) + 'px;color:' + str(selected_fields.get('company_id').split('-')[1]) + ';'
        return style

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: