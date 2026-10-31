Search the store catalog by free text and filters. Use it when the customer looks for instruments, asks for options or recommendations, or needs alternatives.
Put instrument types in `category` (for example "acoustic guitar", "ukulele", "keyboard"), written as the customer wrote them, and brands or models in `query`. Fill only the filters the customer mentioned; do not ask for optional ones.
Returns up to `limit` products with price, promotional price when a promotion is active, and availability. For final price, PIX price, installments or details of one product, call `get_product_details`.
Errors: `unknown_category` lists the available categories to offer; `invalid_price_range` means the customer should confirm the price range.
