from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_uom_ordered_qty = fields.Float(string="Ordered Qty", digits="Product Unit of Measure", default=1.0)
    product_uom_max_qty = fields.Float(string="Max Qty", digits="Product Unit of Measure")
    batch_uom_qty = fields.Float(compute="_compute_batch_uom_qty")
    batch_uom_max_qty = fields.Float(compute="_compute_batch_uom_qty")

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

    @api.depends("product_uom_qty", "product_uom_max_qty")
    def _compute_batch_uom_qty(self):
        for line in self:
            if line.order_id.batch_id:
                batch_id = line.batch_id
                product_id = line.product_id
                batch_lines = (
                    self.env["sale.order.line"]
                    .sudo()
                    .search([("batch_id", "=", batch_id.id), ("product_id", "=", product_id.id)])
                )
                line.batch_uom_qty = sum(batch_lines.mapped("product_uom_qty"))
                line.batch_uom_max_qty = sum(batch_lines.mapped("product_uom_max_qty"))
            else:
                line.batch_uom_max_qty = line.batch_uom_qty = 0

    @api.depends("product_packaging_id", "product_uom", "product_uom_qty", "batch_id")
    def _compute_product_packaging_qty(self):
        for line in self:
            if line.batch_id and line.product_packaging_id:
                packaging_uom = line.product_packaging_id.product_uom_id
                batch_uom_qty = line.product_uom._compute_quantity(line.batch_uom_qty, packaging_uom)
                line.product_packaging_qty = float_round(
                    batch_uom_qty / line.product_packaging_id.qty, precision_rounding=packaging_uom.rounding
                )
            else:
                super()._compute_product_packaging_qty()
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("product_id") and not vals.get("product_packaging_id"):
                product_id = vals.get("product_id")
                packaging = self.env["product.packaging"].search([("product_id", "=", product_id)], limit=1)
                vals["product_packaging_id"] = packaging.id
        return super().create(vals_list)
