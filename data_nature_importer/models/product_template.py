from PIL import Image

from odoo import models

from .. import utils as dn_utils


# Increase the max image pixels limit for PIL to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = 2 * 189135000  # set custom limit for large images


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_sync_datanature_image(self):
        for product in self:
            product.with_delay()._sync_dn_images()

    def _get_dn_metadata(self):
        self.ensure_one()
        if not self.barcode:
            return False
        metadata = dn_utils.get_datanature_metadata(self, self.barcode)
        if not metadata:
            return False
        return metadata[0]

    def _sync_dn_images(self):
        self.ensure_one()
        metadata = self._get_dn_metadata()
        if not metadata or not metadata.get("images"):
            return False
        images = metadata.get("images")
        if not images:
            return False
        image_id = None
        for image in images:
            image_id = image.get("id")
            if image.get("mime_type") not in [
                "image/jpeg",
                "image/png",
            ]:
                continue
            image_data = dn_utils.get_datanature_image(self, image_id, token=None)
            if not image_data:
                continue
            if image.get("default") == "true":
                self.image_1920 = image_data
            else:
                ProductImage = self.env["product.image"]
                if (
                    ProductImage.search_count(
                        [
                            ("product_tmpl_id", "=", self.id),
                            ("name", "=", f"DATA Nature Image: {image_id}"),
                        ]
                    )
                    > 0
                ):
                    continue
                ProductImage.create(
                    {
                        "name": f"DATA Nature Image: {image_id}",
                        "product_tmpl_id": self.id,
                        "image_1920": image_data,
                    }
                )
        return True
