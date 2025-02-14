odoo.define("nfu_ecommerce.sale_product_configurator", function (require) {
    "use strict";

    var ProductConfiguratorMixin = require("sale_product_configurator.ProductConfiguratorMixin");
    var publicWidget = require("web.public.widget");

    publicWidget.registry.ProductConfigurator = publicWidget.Widget.extend(ProductConfiguratorMixin, {
        selector: ".oe_website_sale",
        events: _.extend({}, publicWidget.Widget.prototype.events, {
            'change input[name="add_max_qty"]': "_onChangeAddMaxQty",
        }),

        /**
         * @private
         * @param {Event} ev
         */
        _onChangeAddMaxQty: function (ev) {
            var $input = $(ev.currentTarget);
            var lineId = $input.data("line-id");
            var productId = $input.data("product-id");
            var addMaxQty = $input.val();

            this._rpc({
                route: "/shop/cart/update",
                params: {
                    line_id: lineId,
                    product_id: productId,
                    add_max_qty: addMaxQty,
                },
            }).then(function (result) {
                if (result) {
                    window.location.reload();
                }
            });
        },
    });
});
