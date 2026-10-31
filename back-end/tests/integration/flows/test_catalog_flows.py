def ids(payload):
    return [product["product_id"] for product in payload["products"]]


def test_search_by_category_and_max_price_returns_only_available(call_tool):
    payload = call_tool("search_products", {"category": "acoustic guitar", "max_price": 1000})

    assert ids(payload) == [101, 102, 110]
    assert payload["total_found"] == 3
    assert {product["availability"] for product in payload["products"]} == {"available"}


def test_search_shows_promotional_price_with_original(call_tool):
    payload = call_tool("search_products", {"query": "AG-200"})

    assert payload["products"][0] == {
        "product_id": 102,
        "name": "Acme AG-200 Steel Sunburst",
        "category": "Acoustic Guitars",
        "price": "R$ 899,00",
        "promotional_price": "R$ 719,20",
        "discount_percent": 20,
        "availability": "available",
    }


def test_search_respects_limit(call_tool):
    payload = call_tool("search_products", {"limit": 2})

    assert len(payload["products"]) == 2
    assert payload["total_found"] == 7


def test_search_unknown_category_offers_available_ones(call_tool):
    payload = call_tool("search_products", {"category": "saxophone"})

    assert payload["error"] == "unknown_category"
    assert "Ukuleles" in payload["available_categories"]


def test_product_with_only_expired_promotion_offers_pix_price(call_tool):
    payload = call_tool("get_product_details", {"product": "northwind d-50"})

    assert payload["pricing"] == {"list_price": "R$ 2.199,00", "pix_price": "R$ 2.089,05"}
    assert payload["expired_promotions"] == [{"label": "Black Friday", "discount_percent": 12}]


def test_product_with_active_promotions_uses_largest_and_no_pix(call_tool):
    payload = call_tool("get_product_details", {"product": "acme e-300", "installments": 12})

    pricing = payload["pricing"]
    assert pricing["list_price"] == "R$ 3.499,00"
    assert pricing["promotion"] == {
        "label": "Musician Week",
        "discount_percent": 15,
        "price": "R$ 2.974,15",
    }
    assert "pix_price" not in pricing
    assert pricing["installments"] == {
        "requested": 12,
        "allowed": True,
        "installment_value": "R$ 247,85",
        "max_installments": 12,
    }


def test_installments_not_allowed_report_maximum(call_tool):
    payload = call_tool("get_product_details", {"product": "108", "installments": 6})

    assert payload["pricing"]["installments"] == {
        "requested": 6,
        "allowed": False,
        "max_installments": 3,
    }


def test_unavailable_product_offers_available_alternatives(call_tool):
    payload = call_tool("get_product_details", {"product": "northwind c-10"})

    assert payload["availability"] == "out_of_stock"
    assert payload["alternatives"]
    assert {item["availability"] for item in payload["alternatives"]} == {"available"}


def test_ambiguous_product_returns_priced_candidates(call_tool):
    payload = call_tool("get_product_details", {"product": "acme"})

    assert payload["error"] == "ambiguous_product"
    assert {item["product_id"] for item in payload["candidates"]} == {101, 102, 107, 110}
    assert all("price" in item for item in payload["candidates"])


def test_unknown_product(call_tool):
    assert call_tool("get_product_details", {"product": "theremin"})["error"] == "product_not_found"


def test_price_filter_includes_products_cheaper_under_promotion(call_tool):
    payload = call_tool("search_products", {"max_price": 750})

    assert 102 in ids(payload)
    assert payload["products"][-1]["promotional_price"] == "R$ 719,20"
