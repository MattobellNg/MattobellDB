# -*- coding: utf-8 -*-

from odoo import models,fields,api

class PropertyTemplate(models.Model):
    _inherit = 'product.template'

    partner_id = fields.Many2one(
        'res.partner',
        string='Property Location',
    )
    property_type_id = fields.Many2one(
        'property.type',
        string='Property Type',
    )
    is_property_product = fields.Boolean(
        string='Is Property Product',
    )
    website_product_attachment = fields.Many2many(
        'ir.attachment',
        copy=True,
        help="Select attachment/documents which will be show on website shop on product page.",
        string="Website Attachments")  #website_product_shop_attachment

    # @api.multi #migration13
    def google_map_img(self, zoom=8, width=298, height=298):
        partner = self.sudo().partner_id
        return partner and partner.google_map_img(zoom, width, height) or None

    # @api.multi #migration13
    def google_map_link(self, zoom=8):
        partner = self.sudo().partner_id
        return partner and partner.google_map_link(zoom) or None


class PropertyProduct(models.Model):
    _inherit = 'product.product'

    number_of_installment = fields.Integer(
        string='Number of Installment',
    )
    
