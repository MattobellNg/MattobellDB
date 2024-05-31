from odoo import models, fields


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    eservice_code = fields.Char('eService Reference')


class Product(models.Model):

    _inherit = 'product.product'

    def _get_product_from_code(self, code):
        """Get product from code.

        :param str code: code to use to search for product
        :return: An matching product record
        :rtype: recordset of `product.product`
        """
        product = Product = self.env['product.product'].sudo()
        if not code:
            return product
        domain = [('eservice_code', '=', code)]
        product = Product.search(domain)
        return product
