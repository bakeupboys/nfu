from odoo import fields, models


class ProductVariantBulkUploadWizard(models.TransientModel):
    _name = "product.variant.bulk.upload.wizard"
    _description = "Bulk Upload Images for Product Variants"

    file = fields.Binary(required=True)

    def action_upload_images(self):
        if not self.file:
            return

        # Get the active product variants from the context
        active_ids = self.env.context.get("active_ids", [])
        product_variants = self.env["product.product"].browse(active_ids)

        # Assign the uploaded image to each selected product variant
        for product_variant in product_variants:
            product_variant.image_1920 = self.file
