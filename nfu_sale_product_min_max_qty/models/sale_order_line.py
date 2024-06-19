from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_uom_min_qty = fields.Float(string="Max quantity", digits="Product Unit of Measure")
    product_uom_max_qty = fields.Float(string="Min quantity", digits="Product Unit of Measure")
