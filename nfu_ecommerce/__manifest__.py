{
    "name": "NFU eCommerce",
    "summary": "Qty ranges, packagings and credit in webshop",
    "author": "BAKEUP",
    "website": "https://www.bakeup.org",
    "category": "website",
    "version": "16.0.1.6.0",
    "depends": [
        "sale_product_configurator",
        "website_sale",
        "nfu_sale_order_batch_packaging",
        "website_decimal_quantity",
        "nfu_product_bnn_attributes",
        "nfu_account",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/product_attribute_views.xml",
        "views/product_template_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "nfu_ecommerce/static/src/js/*.js",
            "nfu_ecommerce/static/src/scss/portal.scss",
        ]
    },
    "license": "LGPL-3",
}
