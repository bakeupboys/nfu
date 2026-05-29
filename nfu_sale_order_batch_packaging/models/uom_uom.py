from odoo import api, fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    batch_fill_precision = fields.Float(
        help="Rounding step used by the batch fill wizard for this UOM (e.g. 1.0 for whole units, 0.1 for one decimal).",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "batch_fill_precision" not in vals:
                vals["batch_fill_precision"] = vals.get("rounding", 0.01)
        return super().create(vals_list)
