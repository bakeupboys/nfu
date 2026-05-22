from PIL import Image

from odoo import fields, models

from .. import utils as dn_utils


# Increase the max image pixels limit for PIL to avoid DecompressionBombError
Image.MAX_IMAGE_PIXELS = 2 * 189135000  # set custom limit for large images

ERNAEHRUNGSHINWEISE_FIELDS = [
    ("ernhinweis_vegan", "data_nature_importer.attr_ernaehrungshinweise_val_vegan"),
    (
        "ernhinweis_vegetarisch",
        "data_nature_importer.attr_ernaehrungshinweise_val_vegetarisch",
    ),
    (
        "ernhinweis_laktosefrei",
        "data_nature_importer.attr_ernaehrungshinweise_val_laktosefrei",
    ),
    (
        "ernhinweis_glutenfrei",
        "data_nature_importer.attr_ernaehrungshinweise_val_glutenfrei",
    ),
    ("ernhinweis_rohkost", "data_nature_importer.attr_ernaehrungshinweise_val_rohkost"),
    (
        "ernhinweis_ohne_schweinefleisch",
        "data_nature_importer.attr_ernaehrungshinweise_val_ohne_schweinefleisch",
    ),
    (
        "ernhinweis_zuckerfrei",
        "data_nature_importer.attr_ernaehrungshinweise_val_zuckerfrei",
    ),
    (
        "ernhinweis_ohne_zuckerzusatz",
        "data_nature_importer.attr_ernaehrungshinweise_val_ohne_zuckerzusatz",
    ),
]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    producer_id = fields.Many2one(
        "res.partner",
        string="Producer",
        domain=[("is_company", "=", True)],
        index=True,
    )
    producer_name = fields.Char(
        related="producer_id.name", store=True, string="Producer Name"
    )

    def action_sync_datanature_information(self):
        if len(self) == 1:
            self._sync_dn_information()
        else:
            for product in self:
                product.with_delay()._sync_dn_information()

    def _get_dn_metadata(self):
        self.ensure_one()
        if not self.barcode:
            return False
        metadata = dn_utils.get_datanature_metadata(self, self.barcode)
        if not metadata:
            return False
        return metadata[0]

    def _sync_dn_information(self):
        self.ensure_one()
        metadata = self._get_dn_metadata()
        if not metadata:
            return False
        self._sync_dn_category(metadata)
        self._sync_dn_images(metadata)
        self._sync_dn_verband(metadata)
        self._sync_dn_ernaehrungshinweise(metadata)
        self._sync_dn_producer(metadata)
        return True

    def _sync_dn_category(self, metadata):
        warengruppe_id = metadata.get("warengruppe_id")
        if not warengruppe_id:
            return
        category = self.env["product.public.category"].search(
            [("datanature_warengruppe_id", "=", warengruppe_id)], limit=1
        )
        if category and category not in self.public_categ_ids:
            self.public_categ_ids = [(4, category.id)]

    def _sync_dn_verband(self, metadata):
        verband_id = metadata.get("bio_verband_id")
        if not verband_id:
            return
        attr_value = self.env.ref(
            "data_nature_importer.attr_verband_val_%s" % verband_id,
            raise_if_not_found=False,
        )
        if not attr_value:
            return
        attribute = self.env.ref("data_nature_importer.attr_verband")
        attr_line = self.attribute_line_ids.filtered(
            lambda l: l.attribute_id == attribute
        )
        if attr_line:
            if attr_line.value_ids != attr_value:
                attr_line.value_ids = [(6, 0, [attr_value.id])]
        else:
            self.env["product.template.attribute.line"].create(
                {
                    "product_tmpl_id": self.id,
                    "attribute_id": attribute.id,
                    "value_ids": [(6, 0, [attr_value.id])],
                }
            )

    def _sync_dn_ernaehrungshinweise(self, metadata):
        active_ids = [
            self.env.ref(xmlid).id
            for field, xmlid in ERNAEHRUNGSHINWEISE_FIELDS
            if metadata.get(field)
        ]
        attribute = self.env.ref("data_nature_importer.attr_ernaehrungshinweise")
        attr_line = self.attribute_line_ids.filtered(
            lambda l: l.attribute_id == attribute
        )
        if not active_ids:
            attr_line.unlink()
            return
        if attr_line:
            if set(attr_line.value_ids.ids) != set(active_ids):
                attr_line.value_ids = [(6, 0, active_ids)]
        else:
            self.env["product.template.attribute.line"].create(
                {
                    "product_tmpl_id": self.id,
                    "attribute_id": attribute.id,
                    "value_ids": [(6, 0, active_ids)],
                }
            )

    def _sync_dn_producer(self, metadata):
        name = metadata.get("pbm_markenname")
        if not name:
            return
        partner = self.env["res.partner"].search(
            [("name", "=", name), ("is_company", "=", True)], limit=1
        )
        if not partner:
            partner = self.env["res.partner"].create({"name": name, "is_company": True})
        if self.producer_id != partner:
            self.producer_id = partner

    # TODO: remove legacy methode aber cleaning up failed jobs
    def _sync_datanature_image(self, metadata):
        return self._sync_dn_images(metadata)

    def _sync_dn_images(self, metadata):
        images = metadata.get("images")
        if not images:
            return False
        for image in images:
            image_id = image.get("id")
            if image.get("mime_type") not in ["image/jpeg", "image/png"]:
                continue
            image_data = dn_utils.get_datanature_image(self, image_id, token=None)
            if not image_data:
                continue
            if image.get("default") == "true":
                self.image_1920 = image_data
            else:
                ProductImage = self.env["product.image"]
                if ProductImage.search_count(
                    [
                        ("product_tmpl_id", "=", self.id),
                        ("name", "=", f"DATA Nature Image: {image_id}"),
                    ]
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
