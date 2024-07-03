from odoo import fields, models


class SaleMaxQtyChooser(models.TransientModel):
    """Wizard to Allow user to adjust the sale order amout to fit to a packaging size"""

    _name = "sale.max.qty.chooser"
    _description = "Sale Max Quantity Chhooser"

    # fill from init or compute from given sale order lines
    # sale_order_ids = fields.Many2many("sale.order")
    sale_max_qty_ids = fields.One2many("sale.max.qty.line", "sale_max_qty_chooser")

    def update_and_confirm_sale_order(self):
        """
        Confirm sale orders where the quantity is fine. Create new Sale Orders for SO Lines with reset to draft
        Through user error when total order amount of a product is not equal to packaging size (first package in the
        list or smalles package sale_order_line.product_id.product.packaging_ids.qty)
        we can use write({'key':'value'}) to update all sale order lines and action_confirm() to validate all sale
        orders

        Also see this methode on how to create new records. It creates a invoice with invoice lines. we need to do the
        same for sale orders

        def action_sold(self):
            res = super().action_sold()
            self.env["account.move"].create(
                {
                    "property_id": self.id,
                    "partner_id": self.buyer_id.id,
                    "move_type": "out_invoice",
                    "line_ids": [
                        fields.Command.create(
                            {
                                "name": f"Property {self.name} - 10% Tax",
                                "quantity": 1,
                                "price_unit": self.selling_price * 1.1,
                            }
                        ),
                        fields.Command.create({"name": "Administration Fees", "quantity": 1, "price_unit": 1000}),
                    ],
                }
            )
            return res
        """
