from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderLineDescription(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

    def _make_order_line(self, product):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        return self.env["sale.order.line"].create(
            {"order_id": order.id, "product_id": product.id}
        )

    def test_description_skips_variant_attributes(self):
        """A small and a large baguette ordered on the same product keep the
        product description but never show their size attribute value."""
        attribute = self.env["product.attribute"].create(
            {
                "name": "Size",
                "create_variant": "no_variant",
                "value_ids": [
                    (0, 0, {"name": "Small"}),
                    (0, 0, {"name": "Large"}),
                ],
            }
        )
        template = self.env["product.template"].create(
            {
                "name": "Baguette",
                "description_sale": "Crusty loaf",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                ],
            }
        )
        product = template.product_variant_ids[0]
        ptavs = template.attribute_line_ids.product_template_value_ids
        small = ptavs.filtered(lambda p: p.name == "Small")
        large = ptavs.filtered(lambda p: p.name == "Large")
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        for size in (small, large):
            line = self.env["sale.order.line"].create(
                {
                    "order_id": order.id,
                    "product_id": product.id,
                    "product_no_variant_attribute_value_ids": [(6, 0, size.ids)],
                }
            )
            self.assertIn("Baguette", line.name)
            self.assertIn("Crusty loaf", line.name)
            self.assertNotIn(size.name, line.name)
