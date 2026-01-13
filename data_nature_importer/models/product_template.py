import base64

from odoo import models

from .. import utils as dn_utils


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_sync_datanature_image(self):
        for product in self:
            image_data = product._get_dn_image()
            if image_data:
                product.image_1920 = base64.b64encode(image_data).decode("ascii")

    def _get_dn_metadata(self):
        self.ensure_one()
        if not self.barcode:
            return False
        metadata = dn_utils.get_datanature_metadata(self, self.barcode)[0]
        return metadata

    def _get_dn_image(self):
        self.ensure_one()
        metadata = self._get_dn_metadata()
        if not metadata or not metadata.get("images"):
            return False
        image_id = metadata.get("images")[0].get("id")
        image_data = dn_utils.get_datanature_image(self, image_id, token=None)
        if image_data:
            return base64.b64encode(image_data).decode("ascii")
        return False
