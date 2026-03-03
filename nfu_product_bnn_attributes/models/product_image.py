from PIL import Image

from odoo import fields, models


# Increase the max image pixels limit for PIL to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = 2 * 189135000  # set custom limit for large images


class ProductImage(models.Model):
    _inherit = "product.image"

    # TODO: Remove as soon as data_nature thumbnails work
    image_1920 = fields.Image(
        "Image", max_width=1920, max_height=1920, verify_resolution=False
    )
