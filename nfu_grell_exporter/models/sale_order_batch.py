import base64

from odoo import models


class SaleOrderBatch(models.Model):
    _inherit = "sale.order.batch"

    def export_grell_csv(self):
        self.ensure_one()
        # Prepare CSV content
        csv_content = "Default Code,Quantity\n"
        for product in self.product_ids:
            if product.product_id.default_code:
                csv_content += f"{product.product_id.default_code},{product.product_uom_qty}\n"

        # Encode CSV content to base64
        csv_base64 = base64.b64encode(csv_content.encode("utf-8"))

        # Create attachment
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"grell-{self.name}.csv",
                "type": "binary",
                "datas": csv_base64,
                "res_model": self._name,
                "res_id": self.id,
            }
        )

        return {"type": "ir.actions.act_url", "url": f"/web/content/{attachment.id}?download=true", "target": "self"}
