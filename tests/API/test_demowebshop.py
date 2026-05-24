import requests
from jsonschema import validate
from selene import browser, have, be

from utils.demowebshop import (
    DEMO_WEBSHOP_BASE_URL,
    LAPTOP_PRODUCT_CARD_SELECTOR,
    add_laptop_to_cart,
    get_cart_item_id,
    get_customer_cookie,
)
from utils.schema_loader import load_schema


notebook_product_card = browser.element(LAPTOP_PRODUCT_CARD_SELECTOR)


def test_add_to_cart_one_item():
    response, response_data, response_model = add_laptop_to_cart()

    assert response.status_code == 200

    schema = load_schema("response_add_to_card.json")
    validate(response_data, schema)
    assert response_model.success is True

    customer_cookie = get_customer_cookie(response)
    browser.open(f"{DEMO_WEBSHOP_BASE_URL}/cart")
    browser.driver.add_cookie({"name": "Nop.customer", "value": customer_cookie})
    browser.driver.refresh()
    notebook_product_card.should(have.text("14.1-inch Laptop"))


def test_delete_item_from_cart():
    session = requests.Session()
    response, response_data, response_model = add_laptop_to_cart(session)

    assert response.status_code == 200

    schema = load_schema("response_add_to_card.json")
    validate(response_data, schema)
    assert response_model.success is True

    customer_cookie = get_customer_cookie(response)
    browser.open(f"{DEMO_WEBSHOP_BASE_URL}/cart")
    browser.driver.add_cookie({"name": "Nop.customer", "value": customer_cookie})
    browser.driver.refresh()
    browser.element(LAPTOP_PRODUCT_CARD_SELECTOR).should(have.text("14.1-inch Laptop"))

    response_get = session.get(f"{DEMO_WEBSHOP_BASE_URL}/cart")

    value = get_cart_item_id(response_get.text)

    response_delete = session.post(
        f"{DEMO_WEBSHOP_BASE_URL}/cart",
        data={
            "removefromcart": value,
            f"itemquantity{value}": 1,
            "updatecart": "Update shopping cart",
        },
    )
    assert response_delete.status_code == 200
    browser.driver.refresh()
    notebook_product_card.should(be.not_.in_dom)
