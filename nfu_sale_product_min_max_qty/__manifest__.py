{
    "name": "NFU Sale Min Max Quantitiy",
    "summary": "Add minimum and maximum order quantities to sale orders",
    "author": "BAKEUP",
    "website": "https://www.bakeup.org",
    "category": "Stock",
    "version": "16.0.0.0.1",
    "depends": ["sale_management", "website_sale"],
    "data": [
        "views/sale_order_views.xml",
        "views/sale_order_line_views.xml",
        "wizard/sale_max_qty_line_views.xml",
        "wizard/sale_max_qty_chooser_views.xml",
        "views/templates.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {"web.assets_frontend": ["nfu_sale_product_min_max_qty/static/src/js/website_sale.js"]},
    "license": "LGPL-3",
}
