import requests
from utils.schema_loader import load_schema
from jsonschema import validate
from selene import browser, have, be
from bs4 import BeautifulSoup
notebook_product_card=browser.element('[href="/141-inch-laptop"].product-name')

def test_add_to_card_one_buy():
    response_add_to_card_one_buy = requests.post(url='https://demowebshop.tricentis.com/addproducttocart/catalog/31/1/1')

    assert response_add_to_card_one_buy.status_code == 200

    schema=load_schema('response_add_to_card.json')
    response_data=response_add_to_card_one_buy.json()
    validate(response_data,schema)
    assert response_data['success'] == True

    cookies_user=response_add_to_card_one_buy.cookies.get('Nop.customer')
    browser.open('https://demowebshop.tricentis.com/cart')
    browser.driver.add_cookie({'name': 'Nop.customer', 'value': cookies_user})
    browser.driver.refresh()
    notebook_product_card.should(have.text('14.1-inch Laptop'))

def test_delete():
    session=requests.Session()
    response_add_to_card_one_buy = session.post(url='https://demowebshop.tricentis.com/addproducttocart/catalog/31/1/1')

    assert response_add_to_card_one_buy.status_code == 200

    schema=load_schema('response_add_to_card.json')
    response_data=response_add_to_card_one_buy.json()
    validate(response_data,schema)
    assert response_data['success'] == True

    cookies_user = response_add_to_card_one_buy.cookies.get('Nop.customer')
    browser.open('https://demowebshop.tricentis.com/cart')
    browser.driver.add_cookie({'name': 'Nop.customer', 'value': cookies_user})
    browser.driver.refresh()
    browser.element('[href="/141-inch-laptop"].product-name').should(have.text('14.1-inch Laptop'))

    response_get = session.get("https://demowebshop.tricentis.com/cart")

    soup = BeautifulSoup(response_get.text, "html.parser")

    checkbox = soup.find("input", {
        "type": "checkbox",
        "name": "removefromcart"
    })

    value = checkbox["value"]

    response_delete=session.post('https://demowebshop.tricentis.com/cart',data={"removefromcart": value, f'itemquantity{value}': 1, 'updatecart': 'Update shopping cart'})
    assert response_delete.status_code == 200
    browser.driver.refresh()
    notebook_product_card.should(be.not_.in_dom)