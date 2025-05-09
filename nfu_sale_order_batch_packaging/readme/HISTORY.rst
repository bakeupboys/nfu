:0.0.1: Initial module.
:1.0.0: rename to nfu_sale_order_batch_packaging
:1.1.0: Live
:1.2.0: Add regeneration action for batch products
:1.2.1: refactoring
:1.3.0: add packaging states
:1.3.1: add open_max_qty
:1.3.2: fix color indicator
:1.3.3: Enable packagings on installation
:1.3.4: 
    - on creation set max_qty to product_uom_qty if not set
    - remove zero exception for max_qty
    - store open_packaging_qty on batch product module to make it sortable