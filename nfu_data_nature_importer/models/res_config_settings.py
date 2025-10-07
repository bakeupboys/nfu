from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    data_nature_username = fields.Char(string="API Username")
    data_nature_key = fields.Char(string="API Key")

    def set_values(self):
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "nfu_data_nature_importer.data_nature_username", self.data_nature_username
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "nfu_data_nature_importer.data_nature_key", self.data_nature_key
        )

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(
            data_nature_username=self.env["ir.config_parameter"]
            .sudo()
            .get_param("nfu_data_nature_importer.data_nature_username", default=""),
            data_nature_key=self.env["ir.config_parameter"]
            .sudo()
            .get_param("nfu_data_nature_importer.data_nature_key", default=""),
        )
        return res
