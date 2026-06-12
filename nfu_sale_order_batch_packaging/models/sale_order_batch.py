from odoo import api, fields, models
from odoo.addons.sale_order_batch.models.sale_order_batch import READONLY_FIELD_STATES


class SaleOrderBatch(models.Model):
    _inherit = "sale.order.batch"

    has_qty_adjusted = fields.Boolean(
        compute="_compute_has_qty_adjusted",
    )
    has_fillable_packages = fields.Boolean(
        compute="_compute_has_fillable_packages",
    )
    open_product_ids = fields.Many2many(
        comodel_name="sale.order.batch.product",
        compute="_compute_open_product_ids",
        inverse="_inverse_open_product_ids",
        states=READONLY_FIELD_STATES,
    )

    @api.depends(
        "sale_order_line_ids.product_uom_qty",
        "sale_order_line_ids.product_uom_ordered_qty",
    )
    def _compute_has_qty_adjusted(self):
        for batch in self:
            batch.has_qty_adjusted = any(
                line.product_uom_qty != line.product_uom_ordered_qty
                for line in batch.sale_order_line_ids
            )

    @api.depends("product_ids.open_packaging_qty")
    def _compute_has_fillable_packages(self):
        for batch in self:
            batch.has_fillable_packages = any(
                p.open_packaging_qty > 0 for p in batch.product_ids
            )

    @api.depends("product_ids.open_packaging_qty")
    def _compute_open_product_ids(self):
        for batch in self:
            batch.open_product_ids = batch.product_ids.filtered(
                lambda p: p.open_packaging_qty > 0
            )

    def _inverse_open_product_ids(self):
        pass

    def action_restore_ordered_qty(self):
        self.ensure_one()
        lines = self.sale_order_line_ids.filtered(
            lambda l: l.product_uom_qty != l.product_uom_ordered_qty
        )
        for line in lines:
            line.write({"product_uom_qty": line.product_uom_ordered_qty})

    def action_fill_packages(self):
        self.ensure_one()
        eligible = self.product_ids.filtered(
            lambda p: p.open_packaging_qty > 0 and float_is_zero(p.open_packaging_max_qty)
        )
        ineligible = self.product_ids.filtered(
            lambda p: p.open_packaging_qty > 0 and not float_is_zero(p.open_packaging_max_qty)
        )
        wizard = self.env["sale.order.batch.packaging.fill"].create(
            {
                "batch_id": self.id,
                "line_ids": [(0, 0, {"batch_product_id": p.id}) for p in eligible],
                "zero_line_ids": [
                    (0, 0, {"batch_product_id": p.id}) for p in ineligible
                ],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Fill Open Packages",
            "res_model": "sale.order.batch.packaging.fill",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
        }
