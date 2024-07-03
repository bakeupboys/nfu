from odoo import fields, models


class SaleMaxQtyLine(models.TransientModel):
    """
    Lines to shown in Wizard
    """

    _name = "sale.max.qty.line"
    _description = "Max qty Sale Order Lines"

    sale_max_qty_chooser = fields.Many2one("sale.max.qty.chooser")
    qty = fields.Float()
    sale_line_id = fields.Many2one("sale.order.line")
    product_id = fields.Many2one(related="sale_line_id.product_id")
    reset_to_draft = fields.Boolean()
