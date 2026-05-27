from odoo import fields, models


class UomUom(models.Model):
    _inherit = "uom.uom"

    reconcile_whole_units = fields.Boolean(
        string="Reconcile as Whole Units",
        default=False,
        help="When set, the packaging reconciliation wizard defaults to rounding=1 for this UOM.",
    )
