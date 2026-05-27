from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    stueck = env.ref(
        "nfu_sale_order_batch_packaging.product_uom_stueck",
        raise_if_not_found=False,
    )
    if not stueck:
        return
    imd = env["ir.model.data"].search(
        [("module", "=", "_import_"), ("name", "=", "uom.product_uom_piece")]
    )
    if imd:
        imd.write({"res_id": stueck.id})
