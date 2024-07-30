from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_publish_on_website(self):
        for product in self:
            product.is_published = True

    def action_unpublish_on_website(self):
        for product in self:
            product.is_published = False
