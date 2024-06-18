from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    additional_information = fields.Char()
    quality = fields.Char()
    origin = fields.Char()
    manufacturer_abbr = fields.Char(string="Manufacturer Abbreviation")
