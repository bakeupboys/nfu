from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_uom_ordered_qty = fields.Float(string="Ordered Qty", digits="Product Unit of Measure", default=1.0)
    product_uom_max_qty = fields.Float(string="Max Qty", digits="Product Unit of Measure")
    batch_uom_qty = fields.Float(related="batch_product_id.product_uom_qty", string="Batch UOM Qty")
    batch_uom_max_qty = fields.Float(related="batch_product_id.product_uom_max_qty", string="Batch UOM Max Qty")

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("product_id") and not vals.get("product_packaging_id"):
                product_id = vals.get("product_id")
                packaging = self.env["product.packaging"].search([("product_id", "=", product_id)], limit=1)
                vals["product_packaging_id"] = packaging.id
        return super().create(vals_list)
