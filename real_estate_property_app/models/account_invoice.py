# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    # _inherit = "account.invoice"
    _inherit = "account.move" #migration13
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string="Sale Order Id",
    )
