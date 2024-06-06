{
    "name": "NFU EKG Stock",
    "summary": "NFU EKG Stock Improvements",
    "author": "BAKEUP",
    "website": "https://www.bakeup.org",
    "category": "Stock",
    "version": "16.0.1.0.2",
    "depends": ["stock", "partner_firstname"],
    "data": [
        "views/report_deliveryslip.xml",
        "views/report_deliveryslip_compact.xml",
        "views/report_packing_list.xml",
        "report/stock_report_views.xml",
    ],
    "assets": {"web.report_assets_common": ["nfu_ekg_stock/static/src/scss/report_stock_rule.scss"]},
    "license": "LGPL-3",
    "application": True,
}
