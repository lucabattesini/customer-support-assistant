Get the status, items, total, tracking code and estimated delivery of a customer order. Use it for questions about an order, delivery or tracking.
When `delivery_overdue` is true, the estimated delivery date has passed and the order has not been delivered: apologize for the delay and offer a handoff to the team.
Required: the order number and the customer's email or phone. If any is missing, ask the customer before calling this tool.
Errors: `missing_contact` means you must ask for the email or phone. `verification_failed` means you must ask the customer to check the order number and contact, without saying whether the order exists.
