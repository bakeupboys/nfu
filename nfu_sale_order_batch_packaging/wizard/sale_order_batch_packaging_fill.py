from odoo import api, fields, models


class SaleOrderBatchPackagingFill(models.TransientModel):
    _name = "sale.order.batch.packaging.fill"
    _description = "Batch Packaging Auto-Fill Wizard"

    batch_id = fields.Many2one("sale.order.batch", readonly=True)
    line_ids = fields.One2many("sale.order.batch.packaging.fill.line", "wizard_id")
    zero_line_ids = fields.One2many(
        "sale.order.batch.packaging.fill.zero.line", "wizard_id"
    )
    has_fill_lines = fields.Boolean(compute="_compute_has_fill_lines")
    has_zero_lines = fields.Boolean(compute="_compute_has_zero_lines")

    @api.depends("line_ids")
    def _compute_has_fill_lines(self):
        for wizard in self:
            wizard.has_fill_lines = bool(wizard.line_ids)

    @api.depends("zero_line_ids")
    def _compute_has_zero_lines(self):
        for wizard in self:
            wizard.has_zero_lines = bool(wizard.zero_line_ids)

    def action_fill(self):
        for line in self.line_ids:
            line.batch_product_id._fill_packaging(line.batch_fill_precision)
        for zero_line in self.zero_line_ids.filtered(lambda l: not l.keep_qty):
            zero_line.batch_product_id._zero_packaging()
        return {"type": "ir.actions.act_window_close"}


class SaleOrderBatchPackagingFillLine(models.TransientModel):
    _name = "sale.order.batch.packaging.fill.line"
    _description = "Batch Packaging Auto-Fill Wizard Line"

    wizard_id = fields.Many2one("sale.order.batch.packaging.fill", ondelete="cascade")
    batch_product_id = fields.Many2one("sale.order.batch.product", required=True)
    product_id = fields.Many2one(
        related="batch_product_id.product_id", string="Product"
    )
    open_packaging_qty = fields.Float(
        related="batch_product_id.open_packaging_qty",
        string="Open Packaging Qty",
        digits=[12, 3],
    )
    batch_fill_precision = fields.Float(
        string="Precision",
        compute="_compute_batch_fill_precision",
        precompute=True,
        store=True,
        readonly=False,
    )

    @api.depends("batch_product_id.product_id.uom_id.batch_fill_precision")
    def _compute_batch_fill_precision(self):
        for line in self:
            line.batch_fill_precision = (
                line.batch_product_id.product_id.uom_id.batch_fill_precision
            )


class SaleOrderBatchPackagingFillZeroLine(models.TransientModel):
    _name = "sale.order.batch.packaging.fill.zero.line"
    _description = "Batch Packaging Auto-Fill Zero-Out Line"

    wizard_id = fields.Many2one("sale.order.batch.packaging.fill", ondelete="cascade")
    batch_product_id = fields.Many2one("sale.order.batch.product", required=True)
    product_id = fields.Many2one(
        related="batch_product_id.product_id", string="Product"
    )
    open_packaging_qty = fields.Float(
        related="batch_product_id.open_packaging_qty",
        string="Open Packaging Qty",
        digits=[12, 3],
    )
    keep_qty = fields.Boolean(string="Keep", default=False)
