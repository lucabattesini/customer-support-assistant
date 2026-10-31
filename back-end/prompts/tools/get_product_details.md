Get full details and the final pricing of one product: list price, active promotion, PIX price and an optional installment simulation. Use it for questions about the price, availability, specifications, PIX or installments of a specific product.
`product` accepts the product id or its name as written by the customer. When the customer already mentioned a product in the conversation, use it. Set `installments` only when the customer asks about paying in installments.
Present the original price, promotional price and discount exactly as returned. When the product is unavailable, offer the returned alternatives.
Errors: `ambiguous_product` returns candidates; ask the customer which one they mean. `product_not_found` means you should ask for more details or use `search_products`.
