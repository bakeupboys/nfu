from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    nfu_credit = fields.Monetary(
        string="Customer Credit", compute="_compute_nfu_credit"
    )

    @api.depends("commercial_partner_id.credit")
    def _compute_nfu_credit(self):
        for partner in self:
            partner.nfu_credit = -partner.commercial_partner_id.credit
