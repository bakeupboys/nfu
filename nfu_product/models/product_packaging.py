from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = ["multi.company.abstract", "product.packaging"]
    _name = "product.packaging"

    company_ids = fields.Many2many(related="product_id.company_ids")
