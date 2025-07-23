from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    credit_warning_level = fields.Monetary(
        string="Credit Warning",
        readonly=False,
        help="When the credit of a customer is lower than the warning level the credit is shown in red on the website.",
    )
    avoid_depts = fields.Boolean(string="Avoid depths")
