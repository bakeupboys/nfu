from odoo import api, fields, models


class SaleOrderBatchProduct(models.Model):
    _inherit = "sale.order.batch.product"

    open_packaging_qty = fields.Float(compute="_compute_open_packagin_qty")

    @api.depends("sale_order_line_ids.product_uom_qty")
    def _compute_open_packagin_qty(self):
        for product in self:
            open_packaging_qty = product.product_packaging_qty - (
                sum(product.sale_order_line_ids.mapped("product_uom_qty"))
                % product.product_packaging_qty
                % product.product_packaging_qty
            )
            product.open_packaging_qty = (
                0 if open_packaging_qty == product.product_packaging_qty else open_packaging_qty
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if vals.get("product_id") and not vals.get("product_packaging_id"):
                product_id = vals.get("product_id")
                packaging = self.env["product.packaging"].search([("product_id", "=", product_id)], limit=1)
                vals["product_packaging_id"] = packaging.id
        return super().create(vals_list)
