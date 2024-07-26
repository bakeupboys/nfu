from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_uom_ordered_qty = fields.Float(string="Ordered Qty", digits="Product Unit of Measure", default=1.0)
    product_uom_max_qty = fields.Float(string="Max Qty", digits="Product Unit of Measure")

    @api.constrains("product_uom_qty", "product_uom_max_qty")
    def _check_product_uom_qty(self):
        for order_line in self:
            if order_line.product_uom_max_qty != 0 and order_line.product_uom_qty > order_line.product_uom_max_qty:
                raise UserError(
                    _(
                        f"{order_line.order_id.name},{order_line.product_id.name}:"
                        "The quantity must be less than or equal to the maximum quantity."
                    )
                )
