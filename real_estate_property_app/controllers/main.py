# -*- coding: utf-8 -*-

import base64

from odoo import http
from odoo.http import request
# from odoo.addons.website_sale.controllers.main import QueryURL
# from odoo.addons.website_sale.controllers.main import WebsiteSale


# class website_sale(WebsiteSale):
#    def product_quotation_user(self, values):
#        return values

#    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
#    def product(self, product, category='', search='', **kwargs):

#        product_context = dict(request.env.context, active_id=product.id)
#        ProductCategory = request.env['product.public.category']
#        Rating = request.env['rating.rating']

#        if category:
#            category = ProductCategory.browse(int(category)).exists()

#        attrib_list = request.httprequest.args.getlist('attrib')
#        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]

#        attrib_set = set([v[1] for v in attrib_values])

#        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

#        categs = ProductCategory.search([('parent_id', '=', False)])

#        pricelist = request.website.get_current_pricelist()

#        from_currency = request.env.user.company_id.currency_id
#        to_currency = pricelist.currency_id
#        compute_currency = lambda price: from_currency.compute(price, to_currency)

#        # get the rating attached to a mail.message, and the rating stats of the product
#        ratings = Rating.search([('message_id', 'in', product.website_message_ids.ids)])
#        rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])
#        rating_product = product.rating_get_stats([('website_published', '=', True)])

#        if not product_context.get('pricelist'):
#            product_context['pricelist'] = pricelist.id
#            product = product.with_context(product_context)

#        values = {
#            'search': search,
#            'category': category,
#            'pricelist': pricelist,
#            'attrib_values': attrib_values,
#            'compute_currency': compute_currency,
#            'attrib_set': attrib_set,
#            'keep': keep,
#            'categories': categs,
#            'main_object': product,
#            'product': product,
#            # 'get_attribute_value_ids': self.get_attribute_value_ids,# not in odoo12
#            'rating_message_values': rating_message_values,
#            # 'get_attribute_exclusions': self._get_attribute_exclusions, # added in odoo12
#            'get_attribute_exclusions': product._get_attribute_exclusions, # migration13
#            'optional_product_ids': [p.with_context({'active_id': p.id}) for p in product.optional_product_ids], #added in odoo12
#            'rating_product': rating_product
#        }
#        values = self.product_quotation_user(values)
#        return request.render("website_sale.product", values)


class Product_Quotations(http.Controller):
    @http.route(['/shop_quote/product_quote'], type='http', auth="public", website=True)
    def create_quote(self, **kwargs):
        user_id = request.env.user
        product_id = int(kwargs.get('product_id'))
        product = request.env['product.product'].browse(product_id)
        if request.env.ref('base.public_user') == user_id:
            email = kwargs.get('email')
            partner_id = request.env['res.partner'].sudo().search([('email', '=', email)])
            if not partner_id:
                values = {
                    'name':kwargs.get('name'),
                    'email':kwargs.get('email'),
                    'phone':kwargs.get('phone'),
                }
                partner_id = request.env['res.partner'].sudo().create(values)
            else:
                partner_id = partner_id[0]
        else:
            partner_id = user_id.partner_id
        values = {
                'partner_id' : partner_id.id,
                'note':'"Website quote"' + '\n' + '\n' + kwargs.get('note'),
                }
        order_id = request.env['sale.order'].sudo().create(values)
        product_uom_qty = float(kwargs.get('quantity'))
        values={
               'product_id':product_id,
               'product_uom_qty':product_uom_qty,
               'order_id':order_id.id,
               'product_uom': product.uom_id.id,#to fix sale_margin issue
               'price_unit': product.lst_price,
               'number_of_installment':product.number_of_installment,
               }
        line_id = request.env['sale.order.line'].sudo().create(values)
        return request.render('real_estate_property_app.quote_thanks')

    @http.route(['/web/real_estat_attach',
        '/web/real_estat_attach/<string:xmlid>',
        '/web/real_estat_attach/<string:xmlid>/<string:filename>',
        '/web/real_estat_attach/<int:id>',
        '/web/real_estat_attach/<int:id>/<string:filename>',
        '/web/real_estat_attach/<int:id>-<string:unique>',
        '/web/real_estat_attach/<int:id>-<string:unique>/<string:filename>',
        '/web/real_estat_attach/<int:id>-<string:unique>/<path:extra>/<string:filename>',
        '/web/real_estat_attach/<string:model>/<int:id>/<string:field>',
        '/web/real_estat_attach/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def real_estat_attach_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        http_obj = request.env['ir.http']
        if kw.get("product_tmp_id"):
            product_id = request.env['product.template'].sudo().browse(int(kw.get("product_tmp_id")))
            if id in product_id.website_product_attachment.ids:
                http_obj = request.env['ir.http'].sudo()
        status, headers, content = http_obj.binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype, access_token=access_token)
        if status != 200:
            return request.env['ir.http']._response_by_status(status, headers, content)
        else:
            content_base64 = base64.b64decode(content)
            headers.append(('Content-Length', len(content_base64)))
            response = request.make_response(content_base64, headers)
        if token:
            response.set_cookie('fileToken', token)
        return response

