import base64

from odoo import models


class SaleOrderBatch(models.Model):
    _inherit = "sale.order.batch"

    def export_wholesaler_csv(self):
        self.ensure_one()
        # Prepare CSV content
        csv_content = "Artnr,Menge\n"
        for product in self.product_ids.filtered(lambda p: p.product_id.default_code):
            wholesaler_qty = int(product.product_uom_qty / product.product_packaging_qty)
            csv_content += f"{product.product_id.default_code},{wholesaler_qty}\n"

        # Encode CSV content to base64
        csv_base64 = base64.b64encode(csv_content.encode("utf-8"))

        # Create attachment
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"wholesaler-{self.name}.csv",
                "type": "binary",
                "datas": csv_base64,
                "res_model": self._name,
                "res_id": self.id,
            }
        )

        return {"type": "ir.actions.act_url", "url": f"/web/content/{attachment.id}?download=true", "target": "self"}
