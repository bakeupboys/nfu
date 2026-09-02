from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    nfu_merge_cart_lines = fields.Boolean(
        string="Merge Cart Lines",
        help="Only relevant for attributes that never create a variant "
        "(Variant Creation Mode = 'Never'). When enabled, adding a product to "
        "the cart from the webshop with the same selection for this attribute "
        "increases the quantity of the existing cart line instead of creating a "
        "new line.",
    )
