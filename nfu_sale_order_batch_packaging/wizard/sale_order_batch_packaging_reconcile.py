from odoo import api, fields, models


class SaleOrderBatchPackagingReconcile(models.TransientModel):
    _name = "sale.order.batch.packaging.reconcile"
    _description = "Batch Packaging Auto-Reconcile Wizard"

    batch_id = fields.Many2one("sale.order.batch", readonly=True)
    line_ids = fields.One2many("sale.order.batch.packaging.reconcile.line", "wizard_id")
    zero_line_ids = fields.One2many(
        "sale.order.batch.packaging.reconcile.zero.line", "wizard_id"
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

    def action_reconcile(self):
        for line in self.line_ids:
            rounding = 1.0 if line.use_whole_units else 0.1
            line.batch_product_id._reconcile_packaging(rounding)
        for zero_line in self.zero_line_ids.filtered(lambda l: not l.keep_qty):
            zero_line.batch_product_id._zero_packaging()
        return {"type": "ir.actions.act_window_close"}


class SaleOrderBatchPackagingReconcileLine(models.TransientModel):
    _name = "sale.order.batch.packaging.reconcile.line"
    _description = "Batch Packaging Auto-Reconcile Wizard Line"

    wizard_id = fields.Many2one(
        "sale.order.batch.packaging.reconcile", ondelete="cascade"
    )
    batch_product_id = fields.Many2one("sale.order.batch.product", required=True)
    product_id = fields.Many2one(
        related="batch_product_id.product_id", string="Product"
    )
    open_packaging_qty = fields.Float(
        related="batch_product_id.open_packaging_qty",
        string="Open Packaging Qty",
        digits=[12, 3],
    )
    use_whole_units = fields.Boolean(
        string="Round to 1",
        compute="_compute_use_whole_units",
        precompute=True,
        store=True,
        readonly=False,
    )

    @api.depends("batch_product_id.product_id.uom_id.reconcile_whole_units")
    def _compute_use_whole_units(self):
        for line in self:
            line.use_whole_units = (
                line.batch_product_id.product_id.uom_id.reconcile_whole_units
            )


class SaleOrderBatchPackagingReconcileZeroLine(models.TransientModel):
    _name = "sale.order.batch.packaging.reconcile.zero.line"
    _description = "Batch Packaging Auto-Reconcile Zero-Out Line"

    wizard_id = fields.Many2one(
        "sale.order.batch.packaging.reconcile", ondelete="cascade"
    )
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
