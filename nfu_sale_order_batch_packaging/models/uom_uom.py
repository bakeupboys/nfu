from odoo import api, fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    batch_fill_precision = fields.Float(
        compute="_compute_batch_fill_precision",
        store=True,
        readonly=False,
        help="Rounding step used by the batch fill wizard for this UOM (e.g. 1.0 for whole units, 0.1 for one decimal).",
    )

    @api.depends("rounding")
    def _compute_batch_fill_precision(self):
        for uom in self:
            uom.batch_fill_precision = uom.rounding
