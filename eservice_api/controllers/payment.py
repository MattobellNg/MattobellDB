# -*- coding: utf-8 -*-
from datetime import date
from odoo import http, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


PAYMENT_READ_FIELDS = [
    'partner_id',
    'payment_type',
    'date',
    'ref',
    'amount',
]

PAYMENT_CREATE_FIELDS = PAYMENT_READ_FIELDS + [
    'journal_id',
]


class PaymentHome(http.Controller):

    @http.route('/fb_api/payments/json', auth='public', type='json', csrf=False, cors="*")
    def get_payments_json(self):
        """Get a list of partners on the system.
        """
        domain = [('payment_type', '=', 'inbound')]
        partner_id = request.get_json_data().get("customer_id")
        invoice_number = request.get_json_data().get("invoice_number")
        if partner_id:
            domain += [('x_studio_partner_id', '=', partner_id)]
        if invoice_number:
            domain += [('ref', '=', invoice_number)]
        records = request.env['account.payment'].sudo().search(domain)
        return records.read(PAYMENT_READ_FIELDS)

    @http.route('/fb_api/create_payments/json', auth='public', type='json', csrf=False, cors="*")
    def add_payment_json(self):
        """Create a new payment on the system
        """
        AccountPayment = request.env['account.payment'].sudo()
        cleaned_data = self._get_cleaned_payment_create_values(
            request.get_json_data())
        payment = AccountPayment.create(cleaned_data)
        return payment.read(PAYMENT_READ_FIELDS)

    def _get_cleaned_payment_create_values(self, json_data={}):
        """Clean up values coming from the other system
        """
        cleaned_data = {}

        partner = request.env['res.partner'].sudo().search(
            [('email', '=', json_data.get('customer')['email'])], limit=1)
        journal = request.env['account.journal'].sudo().search(
            [
                ('type', '=', 'bank'),
                ('code', '=', 'BNK1')
            ], limit=1)
        _logger.info(f"************ {journal} ****************")
        for field in json_data:
            if field in PAYMENT_CREATE_FIELDS:
                cleaned_data[field] = json_data[field]
        cleaned_data['date'] = fields.Date.from_string(
            json_data['date'])
        cleaned_data['partner_id'] = partner.id
        cleaned_data['journal_id'] = journal.id
        cleaned_data['payment_type'] = 'inbound'
        return cleaned_data
