from odoo import fields, models


class ProductImage(models.Model):
    _inherit = "product.image"

    # TODO: Remove as soon as data_nature thumbnails work
    image_1920 = fields.Image(verify_resolution=False)
