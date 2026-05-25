import requests
import allure
import pytest
from jsonschema import validate
from selene import browser, have, be

from steps.demowebshop_steps import (
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


@allure.epic("API-тестирование")
@allure.feature("DemoWebShop API + UI")
@allure.story("Подготовка UI-состояния через API")
@allure.title("Добавление товара в корзину через API и проверка в UI")
@allure.description(
    "Добавляем ноутбук в корзину через API, передаём cookie в браузер и проверяем товар в корзине."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("api", "ui", "demowebshop", "корзина")
def test_add_to_cart_one_item(demowebshop_api: ApiClient):
    with allure.step("Добавить товар в корзину через API"):
        response, response_data, response_model = add_laptop_to_cart(demowebshop_api)

    with allure.step("Проверить статус код, схему и значение success в API-ответе"):
        assert response.status_code == 200

        schema = load_schema("response_add_to_card.json")
        validate(response_data, schema)
        assert response_model.success is True

    with allure.step("Открыть корзину в браузере с cookie пользователя"):
        customer_cookie = get_customer_cookie(response)
        browser.open(CART_ENDPOINT)
        browser.driver.add_cookie({"name": "Nop.customer", "value": customer_cookie})
        browser.driver.refresh()

    with allure.step("Проверить, что товар отображается в корзине"):
        notebook_product_card.should(have.text("14.1-inch Laptop"))


@allure.epic("API-тестирование")
@allure.feature("DemoWebShop API + UI")
@allure.story("Подготовка UI-состояния через API")
@allure.title("Удаление товара из корзины через API и проверка в UI")
@allure.description(
    "Добавляем товар через API, проверяем его в UI, удаляем через API и убеждаемся, что товар исчез."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("api", "ui", "demowebshop", "корзина")
def test_delete_item_from_cart(demowebshop_api: ApiClient):
    session = requests.Session()
    session_api = demowebshop_api.with_session(session)
    with allure.step("Добавить товар в корзину через API"):
        response, response_data, response_model = add_laptop_to_cart(session_api)

    with allure.step("Проверить статус код, схему и значение success в API-ответе"):
        assert response.status_code == 200

        schema = load_schema("response_add_to_card.json")
        validate(response_data, schema)
        assert response_model.success is True

    with allure.step("Открыть корзину в браузере с cookie пользователя"):
        customer_cookie = get_customer_cookie(response)
        browser.open(CART_ENDPOINT)
        browser.driver.add_cookie({"name": "Nop.customer", "value": customer_cookie})
        browser.driver.refresh()

    with allure.step("Проверить, что товар отображается в корзине"):
        browser.element(LAPTOP_PRODUCT_CARD_SELECTOR).should(have.text("14.1-inch Laptop"))

    with allure.step("Получить HTML корзины через API"):
        response_get = session_api.get(CART_ENDPOINT)
        assert response_get.status_code == 200

    with allure.step("Сформировать и проверить request body для удаления товара"):
        value = get_cart_item_id(response_get.text)
        request_data = {
            "removefromcart": value,
            f"itemquantity{value}": 1,
            "updatecart": "Update shopping cart",
        }
        validate(request_data, load_schema("cart_delete_request_schema.json"))

    with allure.step("Удалить товар из корзины через API"):
        response_delete = session_api.post(CART_ENDPOINT, data=request_data)
        assert response_delete.status_code == 200

    with allure.step("Проверить в UI, что товар удалён из корзины"):
        browser.driver.refresh()
        notebook_product_card.should(be.not_.in_dom)
