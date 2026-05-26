import allure
import requests
from bs4 import BeautifulSoup

from models.demowebshop import AddToCartResponse
from utils.api_client import ApiClient


ADD_LAPTOP_TO_CART_ENDPOINT = "/addproducttocart/catalog/31/1/1"
CART_ENDPOINT = "/cart"
LAPTOP_PRODUCT_CARD_SELECTOR = '[href="/141-inch-laptop"].product-name'


def add_laptop_to_cart(
    api_client: ApiClient,
) -> tuple[requests.Response, dict[str, object], AddToCartResponse]:
    with allure.step("Добавить ноутбук в корзину через API"):
        response = api_client.post(ADD_LAPTOP_TO_CART_ENDPOINT)
        response_data = response.json()
        response_model = AddToCartResponse.model_validate(response_data)

        return response, response_data, response_model


def get_customer_cookie(response: requests.Response) -> str:
    with allure.step("Получить cookie Nop.customer из API-ответа"):
        cookie = response.cookies.get("Nop.customer")
        if not cookie:
            raise AssertionError("Nop.customer cookie was not returned")

        return cookie


def get_cart_item_id(cart_html: str) -> str:
    with allure.step("Получить идентификатор товара в корзине из HTML"):
        soup = BeautifulSoup(cart_html, "html.parser")
        checkbox = soup.find("input", {"type": "checkbox", "name": "removefromcart"})
        if checkbox is None:
            raise AssertionError("Cart item checkbox was not found")

        return checkbox["value"]
