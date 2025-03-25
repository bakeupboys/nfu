from odoo import api, fields, models


PACKAGING_STATES = [("open", "Open"), ("full", "Full"), ("last_open", "Last package open")]


class SaleOrderBatchProduct(models.Model):
    _inherit = "sale.order.batch.product"

    product_uom_max_qty = fields.Float("Max Qty", compute="_compute_product_uom_max_qty")
    open_packaging_qty = fields.Float(compute="_compute_open_packagin_qty", store=True)
    open_packaging_state = fields.Selection(selection=PACKAGING_STATES, compute="_compute_open_packagin_state")

    @api.depends("sale_order_line_ids.product_uom_max_qty")
    def _compute_product_uom_max_qty(self):
        for product in self:
            if product.sale_order_line_ids:
                product.product_uom_max_qty = sum(product.sale_order_line_ids.mapped("product_uom_max_qty"))
            else:
                product.product_uom_max_qty = False

    @api.depends("product_uom_qty")
    def _compute_open_packagin_qty(self):
        for product in self:
            open_packaging_qty = product.product_packaging_qty - (
                product.product_uom_qty % product.product_packaging_qty
            )
            product.open_packaging_qty = (
                0 if open_packaging_qty == product.product_packaging_qty else open_packaging_qty
            )

    @api.depends("open_packaging_qty")
    def _compute_open_packagin_state(self):
        for product in self:
            if product.open_packaging_qty == 0:
                product.open_packaging_state = "full"
            elif (product.product_uom_max_qty - product.product_uom_qty) >= product.open_packaging_qty:
                product.open_packaging_state = "full"
            elif product.product_uom_qty < product.product_packaging_qty:
                product.open_packaging_state = "open"
            else:
                product.open_packaging_state = "last_open"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("product_id") and not vals.get("product_packaging_id"):
                packaging = (
                    self.env["product.product"].search([("id", "=", vals.get("product_id"))])._get_nfu_packaging()
                )
                if packaging:
                    vals["product_packaging_id"] = packaging.id
        return super().create(vals_list)
