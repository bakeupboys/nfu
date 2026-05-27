from odoo import api, fields, models
from odoo.tools import float_is_zero, float_round


PACKAGING_STATES = [
    ("open", "Open"),
    ("full", "Full"),
    ("last_open", "Last package open"),
]


class SaleOrderBatchProduct(models.Model):
    _inherit = "sale.order.batch.product"

    product_uom_max_qty = fields.Float(
        "Max Qty",
        compute="_compute_product_uom_max_qty",
        precompute=True,
        store=True,
        digits=[12, 3],
    )
    open_packaging_qty = fields.Float(
        compute="_compute_open_packaging_qty", store=True, digits=[12, 3]
    )
    open_packaging_max_qty = fields.Float(
        compute="_compute_open_packaging_max_qty", store=True, digits=[12, 3]
    )
    open_packaging_state = fields.Selection(
        selection=PACKAGING_STATES, compute="_compute_open_packaging_state"
    )

    @api.depends("sale_order_line_ids.product_uom_max_qty")
    def _compute_product_uom_max_qty(self):
        for product in self:
            product.product_uom_max_qty = sum(
                product.sale_order_line_ids.mapped("product_uom_max_qty")
            )

    @api.depends("product_uom_qty")
    def _compute_open_packaging_qty(self):
        for product in self:
            if product.product_packaging_id:
                open_packaging_qty = product.product_packaging_qty - round(
                    product.product_uom_qty % product.product_packaging_qty, 3
                )
                product.open_packaging_qty = (
                    0.0
                    if open_packaging_qty == product.product_packaging_qty
                    else open_packaging_qty
                )
            else:
                product.open_packaging_qty = 0.0

    @api.depends("product_uom_max_qty")
    def _compute_open_packaging_max_qty(self):
        for product in self:
            if product.product_packaging_id:
                if (
                    product.product_uom_max_qty
                    < product.product_uom_qty + product.open_packaging_qty
                ):
                    product.open_packaging_max_qty = (
                        product.product_packaging_qty
                        - round(
                            product.product_uom_max_qty % product.product_packaging_qty,
                            3,
                        )
                    )
                else:
                    product.open_packaging_max_qty = 0.0
            else:
                product.open_packaging_max_qty = 0.0

    @api.depends("open_packaging_qty")
    def _compute_open_packaging_state(self):
        for product in self:
            if product.open_packaging_qty == 0 or product.open_packaging_max_qty == 0:
                product.open_packaging_state = "full"
            elif product.product_uom_qty < product.product_packaging_qty:
                product.open_packaging_state = "open"
            else:
                product.open_packaging_state = "last_open"

    has_qty_adjusted = fields.Boolean(
        compute="_compute_has_qty_adjusted",
    )

    @api.depends(
        "sale_order_line_ids.product_uom_qty",
        "sale_order_line_ids.product_uom_ordered_qty",
    )
    def _compute_has_qty_adjusted(self):
        for product in self:
            product.has_qty_adjusted = any(
                line.product_uom_qty != line.product_uom_ordered_qty
                for line in product.sale_order_line_ids
            )

    def action_restore_ordered_qty(self):
        self.ensure_one()
        lines = self.sale_order_line_ids.filtered(
            lambda l: l.product_uom_qty != l.product_uom_ordered_qty
        )
        for line in lines:
            line.write({"product_uom_qty": line.product_uom_ordered_qty})

    def _reconcile_packaging(self, rounding):
        self.ensure_one()
        target = self.open_packaging_qty
        eligible = sorted(
            [
                (line, line.product_uom_max_qty - line.product_uom_qty)
                for line in self.sale_order_line_ids
                if line.product_uom_max_qty > line.product_uom_qty
            ],
            key=lambda x: x[1],
        )
        n = len(eligible)
        distributed = 0.0
        last_line = None
        for line, room in eligible:
            remaining = target - distributed
            fair_share = float_round(remaining / n, precision_rounding=rounding)
            addition = min(room, fair_share)
            if addition > 0:
                line.write({"product_uom_qty": line.product_uom_qty + addition})
                distributed += addition
            last_line = line
            n -= 1
            if float_is_zero(target - distributed, precision_rounding=rounding):
                break
        # Attach any sub-rounding remainder directly to the last eligible line
        remainder = target - distributed
        if remainder > 1e-9 and last_line:
            last_line.write({"product_uom_qty": last_line.product_uom_qty + remainder})

    def _zero_packaging(self):
        self.ensure_one()
        for line in self.sale_order_line_ids:
            line.write({"product_uom_qty": 0.0})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("product_id") and not vals.get("product_packaging_id"):
                packaging = (
                    self.env["product.product"]
                    .search([("id", "=", vals.get("product_id"))])
                    ._get_nfu_packaging()
                )
                if packaging:
                    vals["product_packaging_id"] = packaging.id
        return super().create(vals_list)
