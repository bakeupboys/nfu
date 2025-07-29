from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_credit_warning_level = fields.Monetary(
        related="website_id.credit_warning_level", readonly=False
    )
    website_avoid_depts = fields.Boolean(
        related="website_id.avoid_depts", readonly=False
    )
