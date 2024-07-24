from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Should be moved to product.product at some point
    # additional_information = fields.Char()
    # quality = fields.Char()
    # origin = fields.Char()
    # packaging_qty = fields.Float(string="Packaging Quantity")
    # packaging_name = fields.Char()
