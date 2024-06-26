odoo.define('nfu_sale_product_min_max_qty.website_min_max_qty', function (require) {
    'use strict';
    var core = require('web.core');
    var _t = core._t;
    var core = require('web.core');
    var ajax = require('web.ajax');
    var wSaleUtils = require('website_sale.utils');
    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale');
    console.log('here1');
    publicWidget.registry.WebsiteSale.include({

        onClickAddCartJSON: function (ev) {

            ev.preventDefault();
            $('.css_quantity').popover('dispose');
            var $link = $(ev.currentTarget);
            var $input = $link.closest('.input-group').find("input");
            var min = parseFloat($input.data("min") || 0);
            var previousQty = parseFloat($input.val() || 0, 10);
            var quantity = ($link.has(".fa-minus").length ? -1 : 1) + previousQty;
            if (quantity < min) {
                $input.closest('.css_quantity').popover({
                    content: _t(`Minimum Quantity is ${min}.`),
                    title: _t("Warning"),
                    placement: "left",
                    trigger: 'focus',
                    html: true,
                });
                $input.closest('.css_quantity').popover('show');

                setTimeout(function () {
                    $('.css_quantity').popover('dispose')
                }, 3000);
            }
            this._super(ev);

        },

        /**
         * Adds the max qty to the POST request when adding a product to the cart.
         * @override
         */
        _changeCartQuantity: function ($input, value, $dom_optional, line_id, productIDs) {
            _.each($dom_optional, function (elem) {
                $(elem).find('.js_quantity').text(value);
                productIDs.push($(elem).find('span[data-product-id]').data('product-id'));
            });
            $input.data('update_change', true);
            var max_qty = parseInt($input.closest('tr').find('input[name="max-qty"]').val(), 0);
            var set_qty = parseInt($input.closest('tr').find('input[name!="max-qty"]').val(), 0);
            this._rpc({
                route: "/shop/cart/update_json",
                params: {
                    line_id: line_id,
                    product_id: parseInt($input.data('product-id'), 10),
                    set_qty: set_qty,
                    max_qty: max_qty,
                },
            }).then(function (data) {
                $input.data('update_change', false);
                var check_value = parseInt($input.val() || 0, 10);
                if (isNaN(check_value)) {
                    check_value = 1;
                }
                if (value !== check_value) {
                    $input.trigger('change');
                    return;
                }
                sessionStorage.setItem('website_sale_cart_quantity', data.cart_quantity);
                if (!data.cart_quantity) {
                    return window.location = '/shop/cart';
                }
                $input.val(data.quantity);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).text(data.quantity);
    
                wSaleUtils.updateCartNavBar(data);
                wSaleUtils.showWarning(data.warning);
                // Propagating the change to the express checkout forms
                core.bus.trigger('cart_amount_changed', data.amount, data.minor_amount);
            });
        }
    });

});
