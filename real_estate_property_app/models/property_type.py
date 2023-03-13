# -*- coding: utf-8 -*-
from odoo import models,fields,api


class PropertyType(models.Model):
    _name = "property.type"
    _description = "Property Type"

    name = fields.Char(
        string='Property Type',
        required=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
    )
