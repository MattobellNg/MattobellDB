# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

PRODUCT_READ_FIELDS = [
    'name',
    'lst_price',
    'eservice_code',
]


class ProductHome(http.Controller):

    @http.route('/fb_api/products', auth='public', methods=["GET"], type='http', csrf=False)
    def get_products(self, filter_is_eservice=False, limit=None):
        """Return a list of eservice products on the system.
        """
        domain = []
        if filter_is_eservice:
            domain = [('eservice_code', '!=', False)]
        limit = limit
        records = request.env['product.product'].sudo().search(
            domain, limit=limit)
        _logger.info(f"Fetched Products = {records}")
        return request.make_json_response(records.read(PRODUCT_READ_FIELDS))
