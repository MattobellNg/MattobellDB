# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

PARTNER_FIELDS = ['name', 'email', 'phone',
                  'street', 'city', 'state_id', 'country_id']


class CustomerHome(http.Controller):

    @http.route('/fb_api/customers/json', auth='public', type='json', csrf=False, cors="*")
    def get_customers_json(self):
        """Get a list of partners on the system.
        """
        domain = [('customer_rank', '>', 0)]
        if customer_id := request.get_json_data() and request.get_json_data().get('customer_id'):
            domain += [("x_studio_partner_id", '=', customer_id)]
        records = request.env['res.partner'].sudo().search(domain)
        response_data = [dict(name=partner.name, partner_id=partner.x_studio_partner_id, email=partner.email, phone=partner.phone) for partner in records]
        return response_data

    @http.route('/fb_api/create_customers/json', auth='public', type='json', csrf=False, cors="*")
    def add_customer_json(self):
        """Create a new customer on the system
        """
        ResPartner = request.env['res.partner'].sudo()
        cleaned_data = self._get_cleaned_customer_create_values(
            request.get_json_data())
        customer = ResPartner.create(cleaned_data)
        return customer.read(PARTNER_FIELDS)

    def _get_cleaned_customer_create_values(self, json_data={}):
        """Clean up values coming from the other system
        """
        cleaned_data = {}
        for field in json_data:
            if field in PARTNER_FIELDS:
                cleaned_data[field] = json_data[field]
        cleaned_data['street'] = json_data['address']['street']
        cleaned_data['customer_rank'] = 1
        cleaned_data['city'] = json_data['address']['city']
        # cleaned_data['state'] = json_data['address'][''] #TODO: find a way to address having multiple states on the system
        cleaned_data['country_id'] = request.env.ref(
            "base.ng") and int(request.env.ref("base.ng")) or False
        return cleaned_data
