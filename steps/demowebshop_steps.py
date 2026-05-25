import allure
import requests
from bs4 import BeautifulSoup

from models.demowebshop import AddToCartResponse
from utils.api_client import ApiClient


ADD_LAPTOP_TO_CART_ENDPOINT = "/addproducttocart/catalog/31/1/1"
CART_ENDPOINT = "/cart"
LAPTOP_PRODUCT_CARD_SELECTOR = '[href="/141-inch-laptop"].product-name'


@allure.step("Добавить ноутбук в корзину через API")
def add_laptop_to_cart(
    api_client: ApiClient,
) -> tuple[requests.Response, dict[str, object], AddToCartResponse]:
    response = api_client.post(ADD_LAPTOP_TO_CART_ENDPOINT)
    response_data = response.json()
    response_model = AddToCartResponse.model_validate(response_data)

    return response, response_data, response_model


@allure.step("Получить cookie Nop.customer из API-ответа")
def get_customer_cookie(response: requests.Response) -> str:
    cookie = response.cookies.get("Nop.customer")
    if not cookie:
        raise AssertionError("Nop.customer cookie was not returned")

    return cookie


@allure.step("Получить идентификатор товара в корзине из HTML")
def get_cart_item_id(cart_html: str) -> str:
    soup = BeautifulSoup(cart_html, "html.parser")
    checkbox = soup.find("input", {"type": "checkbox", "name": "removefromcart"})
    if checkbox is None:
        raise AssertionError("Cart item checkbox was not found")

    return checkbox["value"]
