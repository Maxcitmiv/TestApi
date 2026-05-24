import requests
from bs4 import BeautifulSoup

from models.demowebshop import AddToCartResponse


DEMO_WEBSHOP_BASE_URL = "https://demowebshop.tricentis.com"
LAPTOP_PRODUCT_CARD_SELECTOR = '[href="/141-inch-laptop"].product-name'


def add_laptop_to_cart(
    session: requests.Session | None = None,
) -> tuple[requests.Response, dict[str, object], AddToCartResponse]:
    client = session or requests
    response = client.post(
        url=f"{DEMO_WEBSHOP_BASE_URL}/addproducttocart/catalog/31/1/1"
    )
    response_data = response.json()
    response_model = AddToCartResponse.model_validate(response_data)

    return response, response_data, response_model


def get_customer_cookie(response: requests.Response) -> str:
    cookie = response.cookies.get("Nop.customer")
    if not cookie:
        raise AssertionError("Nop.customer cookie was not returned")

    return cookie


def get_cart_item_id(cart_html: str) -> str:
    soup = BeautifulSoup(cart_html, "html.parser")
    checkbox = soup.find("input", {"type": "checkbox", "name": "removefromcart"})
    if checkbox is None:
        raise AssertionError("Cart item checkbox was not found")

    return checkbox["value"]
