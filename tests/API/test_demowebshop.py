import requests
import pytest
from jsonschema import validate
from selene import browser, have, be

from utils.demowebshop import (
    CART_ENDPOINT,
    LAPTOP_PRODUCT_CARD_SELECTOR,
    add_laptop_to_cart,
    get_cart_item_id,
    get_customer_cookie,
)
from utils.api_client import ApiClient
from utils.schema_loader import load_schema


pytestmark = pytest.mark.ui

notebook_product_card = browser.element(LAPTOP_PRODUCT_CARD_SELECTOR)


def test_add_to_cart_one_item(demowebshop_api: ApiClient):
    response, response_data, response_model = add_laptop_to_cart(demowebshop_api)

    assert response.status_code == 200

    schema = load_schema("response_add_to_card.json")
    validate(response_data, schema)
    assert response_model.success is True

    customer_cookie = get_customer_cookie(response)
    browser.open(CART_ENDPOINT)
    browser.driver.add_cookie({"name": "Nop.customer", "value": customer_cookie})
    browser.driver.refresh()
    notebook_product_card.should(have.text("14.1-inch Laptop"))


def test_delete_item_from_cart(demowebshop_api: ApiClient):
    session = requests.Session()
    session_api = demowebshop_api.with_session(session)
    response, response_data, response_model = add_laptop_to_cart(session_api)

    assert response.status_code == 200

    schema = load_schema("response_add_to_card.json")
    validate(response_data, schema)
    assert response_model.success is True

    customer_cookie = get_customer_cookie(response)
    browser.open(CART_ENDPOINT)
    browser.driver.add_cookie({"name": "Nop.customer", "value": customer_cookie})
    browser.driver.refresh()
    browser.element(LAPTOP_PRODUCT_CARD_SELECTOR).should(have.text("14.1-inch Laptop"))

    response_get = session_api.get(CART_ENDPOINT)
    assert response_get.status_code == 200

    value = get_cart_item_id(response_get.text)
    request_data = {
        "removefromcart": value,
        f"itemquantity{value}": 1,
        "updatecart": "Update shopping cart",
    }
    validate(request_data, load_schema("cart_delete_request_schema.json"))

    response_delete = session_api.post(CART_ENDPOINT, data=request_data)
    assert response_delete.status_code == 200
    browser.driver.refresh()
    notebook_product_card.should(be.not_.in_dom)
