from odoo import models

from .. import utils as dn_utils


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_sync_datanature_image(self):
        for product in self:
            product.with_delay()._sync_datanature_image()

    def _get_dn_metadata(self):
        self.ensure_one()
        if not self.barcode:
            return False
        metadata = dn_utils.get_datanature_metadata(self, self.barcode)
        if not metadata:
            return False
        return metadata[0]

    def _get_dn_image(self):
        self.ensure_one()
        metadata = self._get_dn_metadata()
        if not metadata or not metadata.get("images"):
            return False
        images = metadata.get("images")
        if not images:
            return False
        image_id = None
        for img in images:
            if img.get("default") == "true":
                image_id = img.get("id")
                break
        image_data = dn_utils.get_datanature_image(self, image_id, token=None)
        if image_data:
            return image_data
        return False

    def _sync_datanature_image(self):
        self.ensure_one()
        image_data = self._get_dn_image()
        if image_data:
            self.image_1920 = image_data
