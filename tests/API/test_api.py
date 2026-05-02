import requests
from jsonschema import validate
from schemas.schemas import pet_create_and_get_schema
from data.pets import pets_create_payload
from utils.schema_loader import load_schema
import allure

@allure.title('Создание рандомного питомца')
def test_create_pets_random():
    response=requests.post('https://petstore.swagger.io/v2/pet',
    json={
    "id": 0,
    "category": {
        "id": 0,
        "name": "string"
    },
    "name": "doggie",
    "photoUrls": [
        "string"
    ],
    "tags": [
        {
            "id": 0,
            "name": "string"
        }
    ],
    "status": "available"
})
    assert response.status_code==200
    validate(response.json(), schema=pet_create_and_get_schema)

def test_create_pet():

    payload = pets_create_payload()

    response = requests.post('https://petstore.swagger.io/v2/pet',json=payload)

    data = response.json()

    assert response.status_code == 200

    validate(data, schema=pet_create_and_get_schema)

    assert data["id"] == payload["id"]
    assert data["category"] == payload["category"]
    assert data["name"] == payload["name"]
    assert data["photoUrls"] == payload["photoUrls"]
    assert data["tags"] == payload["tags"]
    assert data["status"] == payload["status"]

def test_get_pet():
    payload = pets_create_payload()

    response = requests.post('https://petstore.swagger.io/v2/pet',json=payload)

    data = response.json()

    assert response.status_code == 200
    validate(data, schema=pet_create_and_get_schema)

    response_get=requests.get(f'https://petstore.swagger.io/v2/pet/{payload["id"]}')

    data_get = response_get.json()

    assert response_get.status_code == 200
    validate(data_get, schema=pet_create_and_get_schema)

    assert data_get["id"] == payload["id"]
    assert data_get["category"] == payload["category"]
    assert data_get["name"] == payload["name"]
    assert data_get["photoUrls"] == payload["photoUrls"]
    assert data_get["tags"] == payload["tags"]
    assert data_get["status"] == payload["status"]

def test_update_pet():
    payload = pets_create_payload()

    response = requests.post('https://petstore.swagger.io/v2/pet',json=payload)

    data = response.json()

    assert response.status_code == 200
    validate(data, schema=pet_create_and_get_schema)

    payload_put=pets_create_payload(pet_id=payload["id"])

    response_put=requests.put('https://petstore.swagger.io/v2/pet',json=payload_put)

    data_put = response_put.json()
    assert response_put.status_code == 200
    validate(data_put, schema=pet_create_and_get_schema)

    assert data_put["id"] == payload["id"]
    assert data_put["category"] == payload_put["category"]
    assert data_put["name"] == payload_put["name"]
    assert data_put["photoUrls"] == payload_put["photoUrls"]
    assert data_put["tags"] == payload_put["tags"]
    assert data_put["status"] == payload_put["status"]

def test_delete_pet():
    payload = pets_create_payload()

    response = requests.post('https://petstore.swagger.io/v2/pet', json=payload)

    data = response.json()

    assert response.status_code == 200
    validate(data, schema=pet_create_and_get_schema)

    response_delete=requests.delete(f'https://petstore.swagger.io/v2/pet/{payload["id"]}')
    data_delete = response_delete.json()

    assert response_delete.status_code == 200
    schema_delete_response=load_schema('delete_response_schema.json')

    validate(data_delete, schema=schema_delete_response)

    assert data_delete['type']=='unknown'
    assert data_delete['message']==str(payload['id'])

def test_negative_get():
    payload = pets_create_payload()

    response = requests.post('https://petstore.swagger.io/v2/pet', json=payload)

    data = response.json()

    assert response.status_code == 200
    validate(data, schema=pet_create_and_get_schema)

    response_delete=requests.delete(f'https://petstore.swagger.io/v2/pet/{payload["id"]}')
    data_delete = response_delete.json()

    assert response_delete.status_code == 200
    schema_delete_response=load_schema('delete_response_schema.json')

    validate(data_delete, schema=schema_delete_response)

    assert data_delete['type']=='unknown'
    assert data_delete['message']==str(payload['id'])

    response_get=requests.get(f'https://petstore.swagger.io/v2/pet/{payload["id"]}')

    data_get = response_get.json()

    assert response_get.status_code==404
    schema_get_error_response=load_schema('error_get_schema.json')
    validate(data_get, schema=schema_get_error_response)

    assert data_get['type']=='error'
    assert data_get['message']=='Pet not found'

def test_delete_error():

    payload = pets_create_payload()

    response = requests.post('https://petstore.swagger.io/v2/pet', json=payload)

    data = response.json()

    assert response.status_code == 200
    validate(data, schema=pet_create_and_get_schema)

    response_delete=requests.delete(f'https://petstore.swagger.io/v2/pet/{payload["id"]}')
    data_delete = response_delete.json()

    assert response_delete.status_code == 200
    schema_delete_response=load_schema('delete_response_schema.json')

    validate(data_delete, schema=schema_delete_response)

    assert data_delete['type']=='unknown'
    assert data_delete['message']==str(payload['id'])

    response_delete_2=requests.delete(f'https://petstore.swagger.io/v2/pet/{payload["id"]}')
    assert response_delete_2.status_code==404
    assert not response_delete_2.content
