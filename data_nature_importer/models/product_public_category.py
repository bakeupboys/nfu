from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    datanature_warengruppe_id = fields.Char(
        string="DataNature Warengruppe ID",
        index=True,
        copy=False,
    )
