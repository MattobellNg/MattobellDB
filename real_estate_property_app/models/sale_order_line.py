# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    installment_id = fields.One2many(
        # 'account.invoice',
        'account.move', #migration_13
        'sale_order_id',
        string = "Installments",
    )
    is_counter = fields.Boolean(
        string='Is Installments create ?',
    )

    # @api.multi #migration_13
    def action_confirm(self):
        for order in self:
            if any(line.product_id.is_property_product for line in order.order_line) and len(order.order_line) > 1:
                raise UserError("You must be select only one order line.")
        return super(SaleOrder, self).action_confirm()

    # @api.multi #migration_13
    def create_installments_invoices(self):
        for order in self:
            if all(not line.product_id.is_property_product for line in order.order_line):
                raise UserError("You can't create installment because property product line not found..")
            order.is_counter = True
            if any(line.product_id.is_property_product for line in order.order_line):
                line = order.order_line and order.order_line[0] or False
                
                if not line:
                    continue
                count = 1
                for x in range(0, line.number_of_installment):
                    inv_data = order._prepare_invoice()
                    inv_data.update({
                        'sale_order_id': order.id,
                    })
                    # invoice = self.env['account.invoice'].create(inv_data)
                    invoice = self.env['account.move'].create(inv_data) #migration_13
                    # vals = line._prepare_invoice_line(line.product_uom_qty)
                    vals = line._prepare_invoice_line() #migration_13
                    vals.update({
                        # 'invoice_id': invoice.id, #migration_13
                        'price_unit':  line.installment_amount,
                        'name': vals['name']+ ' \n Installment -' + str(count),
                        'quantity': line.product_uom_qty #migration_13
                    })
                    inv_line_vals = [(0,0,vals)] #migration_13
                    invoice.write({
                        'invoice_line_ids':[(0,0,vals)],
                    }) #migration_13
                    # self.env['account.invoice.line'].create(vals)  #migration_13
                    # count += 1  #migration_13
        return True

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('price_subtotal','number_of_installment')
    def _compute_installment_amount(self):
        for rec in self:
            if rec.number_of_installment != 0.0 and rec.price_subtotal != 0.0:
                rec.installment_amount = rec.price_subtotal / rec.number_of_installment
            else: #migration_13
                rec.installment_amount = 0.0 #migration_13

    number_of_installment = fields.Integer(
        string='Number of Installment',
    )
    installment_amount = fields.Float(
        string='Installment Amount',
        compute=_compute_installment_amount,
    )

    # @api.multi #migration_13
    @api.onchange('product_id')
    def product_id_change(self):
        # result = super(SaleOrderLine ,self).product_id_change()
        for rec in self:
            rec.number_of_installment = rec.product_id.number_of_installment
        # return result
        
