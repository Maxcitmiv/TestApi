import allure
import requests
from jsonschema import validate

from data.pets import pets_create_payload
from models.pets import DeletePetResponse, PetErrorResponse, PetRequest, PetResponse
from schemas.schemas import pet_create_and_get_schema
from utils.schema_loader import load_schema


PETSTORE_PET_URL = "https://petstore.swagger.io/v2/pet"


def create_pet(payload: PetRequest) -> PetResponse:
    response = requests.post(PETSTORE_PET_URL, json=payload.model_dump(mode="json"))
    assert response.status_code == 200

    response_data = response.json()
    response_model = PetResponse.model_validate(response_data)

    validate(response_data, schema=pet_create_and_get_schema)

    return response_model


@allure.title("Создание рандомного питомца")
def test_create_pets_random():
    payload = pets_create_payload()

    response_model = create_pet(payload)

    assert response_model.id == payload.id
    assert response_model.category == payload.category
    assert response_model.name == payload.name
    assert response_model.photoUrls == payload.photoUrls
    assert response_model.tags == payload.tags
    assert response_model.status == payload.status


def test_create_pet():
    payload = pets_create_payload()

    response_model = create_pet(payload)

    assert response_model.id == payload.id
    assert response_model.category == payload.category
    assert response_model.name == payload.name
    assert response_model.photoUrls == payload.photoUrls
    assert response_model.tags == payload.tags
    assert response_model.status == payload.status


def test_get_pet():
    payload = pets_create_payload()

    create_pet(payload)

    response_get = requests.get(f"{PETSTORE_PET_URL}/{payload.id}")
    assert response_get.status_code == 200

    data_get = response_get.json()
    response_get_model = PetResponse.model_validate(data_get)

    validate(data_get, schema=pet_create_and_get_schema)

    assert response_get_model.id == payload.id
    assert response_get_model.category == payload.category
    assert response_get_model.name == payload.name
    assert response_get_model.photoUrls == payload.photoUrls
    assert response_get_model.tags == payload.tags
    assert response_get_model.status == payload.status


def test_update_pet():
    payload = pets_create_payload()

    create_pet(payload)

    payload_put = pets_create_payload(pet_id=payload.id)

    response_put = requests.put(
        PETSTORE_PET_URL,
        json=payload_put.model_dump(mode="json"),
    )
    assert response_put.status_code == 200

    data_put = response_put.json()
    response_put_model = PetResponse.model_validate(data_put)

    validate(data_put, schema=pet_create_and_get_schema)

    assert response_put_model.id == payload.id
    assert response_put_model.category == payload_put.category
    assert response_put_model.name == payload_put.name
    assert response_put_model.photoUrls == payload_put.photoUrls
    assert response_put_model.tags == payload_put.tags
    assert response_put_model.status == payload_put.status


def test_delete_pet():
    payload = pets_create_payload()

    create_pet(payload)

    response_delete = requests.delete(f"{PETSTORE_PET_URL}/{payload.id}")
    assert response_delete.status_code == 200

    data_delete = response_delete.json()
    delete_response_model = DeletePetResponse.model_validate(data_delete)

    schema_delete_response = load_schema("delete_response_schema.json")

    validate(data_delete, schema=schema_delete_response)

    assert delete_response_model.type == "unknown"
    assert delete_response_model.message == str(payload.id)


def test_negative_get():
    payload = pets_create_payload()

    create_pet(payload)

    response_delete = requests.delete(f"{PETSTORE_PET_URL}/{payload.id}")
    assert response_delete.status_code == 200

    data_delete = response_delete.json()
    delete_response_model = DeletePetResponse.model_validate(data_delete)

    schema_delete_response = load_schema("delete_response_schema.json")

    validate(data_delete, schema=schema_delete_response)

    assert delete_response_model.type == "unknown"
    assert delete_response_model.message == str(payload.id)

    response_get = requests.get(f"{PETSTORE_PET_URL}/{payload.id}")
    assert response_get.status_code == 404

    data_get = response_get.json()
    error_response_model = PetErrorResponse.model_validate(data_get)

    schema_get_error_response = load_schema("error_get_schema.json")
    validate(data_get, schema=schema_get_error_response)

    assert error_response_model.type == "error"
    assert error_response_model.message == "Pet not found"


def test_delete_error():
    payload = pets_create_payload()

    create_pet(payload)

    response_delete = requests.delete(f"{PETSTORE_PET_URL}/{payload.id}")
    assert response_delete.status_code == 200

    data_delete = response_delete.json()
    delete_response_model = DeletePetResponse.model_validate(data_delete)

    schema_delete_response = load_schema("delete_response_schema.json")

    validate(data_delete, schema=schema_delete_response)

    assert delete_response_model.type == "unknown"
    assert delete_response_model.message == str(payload.id)

    response_delete_2 = requests.delete(f"{PETSTORE_PET_URL}/{payload.id}")
    assert response_delete_2.status_code == 404
    assert not response_delete_2.content
