# -*- coding: utf-8 -*-
import logging
from dateutil.relativedelta import relativedelta
from odoo import http, fields
from odoo.tests import Form
from odoo.http import request

_logger = logging.getLogger(__name__)


INVOICE_READ_FIELDS = [
    'name',
    'invoice_date',
    'date',
    'invoice_payment_term_id',
    'journal_id',
    'invoice_date_due',
    'invoice_line_ids',
    'source',
]

INVOICE_CREATE_FIELDS = INVOICE_READ_FIELDS + [
    'move_type',
]


class InvoiceHome(http.Controller):

    @http.route('/fb_api/invoices/json', auth='public', type='json', csrf=False, cors="*")
    def get_invoices_json(self):
        """Get a list of partners on the system.

        Args:
            None

        Returns:
            list: List of serialized invoice records.
        """
        domain = [('move_type', '=', 'out_invoice')]
        invoice_number = request.get_json_data().get("invoice_number")
        if invoice_number:
            domain += [('name', '=', invoice_number)]
        records = request.env['account.move'].sudo().search(domain, limit=1)
        return records.read(INVOICE_READ_FIELDS)

    @http.route('/fb_api/invoices/update/invoice_date', methods=["PUT"], auth='public', type='http', csrf=False, cors="*")
    def update_invoice(self, **kwargs):
        """Update invoice 

        Update invoice with the arbitratry values coming from kwargs

        Args:
            **kwargs: Arbitrary keyword arguments.
                - invoice_number (str): Invoice number.
                - installation_date (str): String formatted date.

        Returns:
            dict: Dictionary of serilaized invoice data.
        """
        installation_date_str = kwargs.get("installation_date")
        invoice_number = kwargs.get("invoice_number")
        eservice_company_id = request.env['res.config.settings'].with_user(
            request.env.ref("base.user_admin")).get_values()['eservice_company_id']
        invoice = request.env['account.move'].sudo().search(
            [
                ('move_type', '=', 'out_invoice'),
                ('company_id', '=', int(eservice_company_id)),
                ('name', '=', str(invoice_number.strip()))
            ]
        )
        _logger.info(f"How many invoices are there {invoice}")
        invoice.ensure_one()
        installation_date = fields.Date.from_string(installation_date_str)
        action_data = invoice.action_register_payment()
        wizard = Form(request.env['account.payment.register'].sudo(
        ).with_context(action_data['context'])).save()
        wizard.action_create_payments()
        invoice.update({'invoice_date': installation_date})
        [serialized_invoice_data] = invoice.read(['name', 'invoice_date'])
        return request.make_json_response(serialized_invoice_data)

    @http.route('/fb_api/create_invoices/json', auth='public', type='json', csrf=False, cors="*")
    def add_invoice_json(self):
        """Create a new invoice on the system

        Args:
            None

        Returns:
            dict: Dictionary of invoice properties.
        """
        AccountInvoice = request.env['account.move'].sudo()
        product_code = request.get_json_data().get("product")["code"]
        deferred_revenue_account_id = request.env['res.config.settings'].with_user(
            request.env.ref("base.user_admin")).get_values()['deferred_revenue_account_id']
        product = request.env['product.product'].sudo().search(
            [('eservice_code', '=', product_code)], limit=1)
        number_of_invoices = int(float(request.get_json_data().get(
            "product")["amount"]) // product.lst_price)
        invoices = AccountInvoice
        invoice_vals = []
        cleaned_data = self._get_cleaned_invoice_create_values(
            request.get_json_data())
        invoices += AccountInvoice.create(cleaned_data.copy())
        for _ in range(1, number_of_invoices):
            recognition_date = fields.Date.from_string(
                cleaned_data.get("invoice_date")) + relativedelta(months=1)
            vals = cleaned_data.copy()
            vals['is_deferred'] = True
            vals['recognition_date'] = recognition_date
            invoice_line_ids = vals['invoice_line_ids']
            for l in invoice_line_ids:
                l[2].update({"account_id": int(deferred_revenue_account_id)})
            invoice_vals.append(vals)
        invoices += AccountInvoice.create(invoice_vals)
        invoices.action_post()
        res = []
        partner = invoices.partner_id
        [partner_dict] = partner.read(
            ['name', 'email', 'phone', 'x_studio_partner_id'])
        for inv in invoices:
            [invoice_dict] = inv.read(INVOICE_READ_FIELDS)
            invoice_dict['customer'] = partner_dict
            res.append(invoice_dict)
        return res

    def _get_cleaned_invoice_create_values(self, json_data={}):
        """Return cleaned json_data.

        The values passed into the function are not necessarily the values required to the create the invoice record and thus
        the values have to be cleaned up removing those fields that are not needed to create a new invoice record.

        Args:
            json_data (dict): Dictonary of data coming from client system.
                partner_id (int): id of the customer for which invoice is to be generated
                journal (str): id of the journal to be used for the transaction
                invoice_payment_term_id (int): id of the payment terms on the invoice
                customer_id (str): FOBID of customer
                invoice_date (str): String representation of the invoice date
                date (str): String representation of the invoice date
                invoice_date_due (str): String representation of the invoice date
                invoice_line_ids (list): List containing invoice lines:
                    product (dict): Dictionary of product values:
                        name (str): Name of product
                        code (str): Eservice code for product
                        quantity (int): Quantity of product
                        unit_price (float): Unit price of product
                        source (str): Source sales order document coming from eService

        Returns:
            dict: Dictionary of cleaned data.
                invoice_date (str): Invoice date expressed as spring formatted date.
                company_id (int): Database id of the company the invoice is meant for.
                invoice_date_due (str): String-formatted invoice due date. 
                partner_id (int): Database id of the customer.
                journal_id (str): Database id of the journal used for this invoice.
                invoice_payment_term_id (str): Database id of the payment term.
                move_type (str): Move type. Default is 'out_invoice'.
                invoice_line_ids (list): List of invoice lines:
                    product_id (int): Database id of the product.
                    quantity (int): Quantity of product to add to the invoice.
                    price_unit: Unit price of product.  
        """
        cleaned_data = {}
        ResPartner = request.env['res.partner'].sudo()
        for field in json_data:
            if field in INVOICE_CREATE_FIELDS:
                cleaned_data[field] = json_data[field]
        eservice_company_id = request.env['res.config.settings'].with_user(
            request.env.ref("base.user_admin")).get_values()['eservice_company_id']
        cleaned_data['invoice_date'] = fields.Date.from_string(
            json_data['date'])
        cleaned_data.setdefault("company_id", int(eservice_company_id))
        cleaned_data['invoice_date_due'] = fields.Date.from_string(
            json_data['date'])
        partner = ResPartner.search(
            [('x_studio_partner_id', '=', json_data['customer_id'])], limit=1)
        journal = request.env['account.journal'].sudo().search(
            [('type', '=', 'sale'), ('eservice_code', '=', json_data['journal']), ('company_id', '=', int(eservice_company_id))], limit=1)
        payment_term = request.env['account.payment.term'].sudo().search([
        ], limit=1)
        cleaned_data['partner_id'] = partner.id
        cleaned_data['journal_id'] = journal.id
        cleaned_data['invoice_payment_term_id'] = payment_term.id
        cleaned_data['move_type'] = 'out_invoice'
        product_id = request.env['product.product']._get_product_from_code(
            json_data.get("product").get("code"))
        cleaned_data['invoice_line_ids'] = [(0, 0, {
            'product_id': product_id and product_id.id,
            'quantity': 1,
            'account_id': int(product_id.property_account_income_id),
            'price_unit': product_id and product_id.list_price,
        })]
        return cleaned_data
