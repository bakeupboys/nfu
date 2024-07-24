from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacturer_abbr = fields.Char(string="Manufacturer Abbreviation")
    # Should be moved to product.product at some point
    additional_information = fields.Char()
    quality = fields.Char()
    origin = fields.Char()
    packaging_qty = fields.Float(string="Packaging Quantity")
    packaging_name = fields.Char()
