{
    "name": "DATA Nature Importer",
    "summary": "Enrich Products with attributes from DATA Nature",
    "author": "BAKEUP",
    "website": "https://www.bakeup.org",
    "category": "product",
    "version": "16.0.1.2.3",
    "depends": ["product", "queue_job", "website_sale"],
    "data": [
        "security/ir.model.access.csv",
        "data/datanature_warengruppen.xml",
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "license": "LGPL-3",
}
