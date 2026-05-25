import allure
import pytest
from jsonschema import validate

from data.pets import pets_create_payload
from models.pets import DeletePetResponse, PetErrorResponse, PetResponse
from schemas.schemas import pet_create_and_get_schema
from steps.pet_steps import create_pet
from utils.api_client import ApiClient
from utils.schema_loader import load_schema


pytestmark = pytest.mark.api


@allure.epic("API-тестирование")
@allure.feature("Petstore API")
@allure.story("Создание питомца")
@allure.title("Создание рандомного питомца")
@allure.description("Проверяем, что API создаёт питомца и возвращает данные из request body.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("api", "petstore", "post", "питомцы")
def test_create_pets_random(petstore_api: ApiClient):
    payload = pets_create_payload()

    response_model = create_pet(petstore_api, payload)

    with allure.step("Проверить, что response совпадает с request body"):
        assert response_model.id == payload.id
        assert response_model.category == payload.category
        assert response_model.name == payload.name
        assert response_model.photoUrls == payload.photoUrls
        assert response_model.tags == payload.tags
        assert response_model.status == payload.status


@allure.epic("API-тестирование")
@allure.feature("Petstore API")
@allure.story("Создание питомца")
@allure.title("Создание питомца")
@allure.description("Проверяем успешное создание питомца через POST /pet.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("api", "petstore", "post", "питомцы")
def test_create_pet(petstore_api: ApiClient):
    payload = pets_create_payload()

    response_model = create_pet(petstore_api, payload)

    with allure.step("Проверить значения в response body"):
        assert response_model.id == payload.id
        assert response_model.category == payload.category
        assert response_model.name == payload.name
        assert response_model.photoUrls == payload.photoUrls
        assert response_model.tags == payload.tags
        assert response_model.status == payload.status


@allure.epic("API-тестирование")
@allure.feature("Petstore API")
@allure.story("Получение питомца")
@allure.title("Получение созданного питомца")
@allure.description("Создаём питомца через API, затем получаем его по id через GET /pet/{id}.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("api", "petstore", "get", "питомцы")
def test_get_pet(petstore_api: ApiClient):
    payload = pets_create_payload()

    create_pet(petstore_api, payload)

    with allure.step("Получить питомца по id и проверить статус код"):
        response_get = petstore_api.get(f"/pet/{payload.id}")
        assert response_get.status_code == 200

    with allure.step("Десериализовать и проверить схему response body"):
        data_get = response_get.json()
        response_get_model = PetResponse.model_validate(data_get)

        validate(data_get, schema=pet_create_and_get_schema)

    with allure.step("Проверить, что GET вернул созданного питомца"):
        assert response_get_model.id == payload.id
        assert response_get_model.category == payload.category
        assert response_get_model.name == payload.name
        assert response_get_model.photoUrls == payload.photoUrls
        assert response_get_model.tags == payload.tags
        assert response_get_model.status == payload.status


@allure.epic("API-тестирование")
@allure.feature("Petstore API")
@allure.story("Обновление питомца")
@allure.title("Обновление данных питомца")
@allure.description("Создаём питомца и обновляем его данные через PUT /pet.")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("api", "petstore", "put", "питомцы")
def test_update_pet(petstore_api: ApiClient):
    payload = pets_create_payload()

    create_pet(petstore_api, payload)

    with allure.step("Сформировать и проверить request body для обновления"):
        payload_put = pets_create_payload(pet_id=payload.id)
        request_data = payload_put.model_dump(mode="json")
        validate(request_data, schema=load_schema("pet_request_schema.json"))

    with allure.step("Отправить PUT /pet и проверить статус код"):
        response_put = petstore_api.put("/pet", json=request_data)
        assert response_put.status_code == 200

    with allure.step("Десериализовать и проверить схему response body"):
        data_put = response_put.json()
        response_put_model = PetResponse.model_validate(data_put)

        validate(data_put, schema=pet_create_and_get_schema)

    with allure.step("Проверить, что данные питомца обновились"):
        assert response_put_model.id == payload.id
        assert response_put_model.category == payload_put.category
        assert response_put_model.name == payload_put.name
        assert response_put_model.photoUrls == payload_put.photoUrls
        assert response_put_model.tags == payload_put.tags
        assert response_put_model.status == payload_put.status


@allure.epic("API-тестирование")
@allure.feature("Petstore API")
@allure.story("Удаление питомца")
@allure.title("Удаление созданного питомца")
@allure.description("Создаём питомца, удаляем его через DELETE /pet/{id} и проверяем ответ удаления.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("api", "petstore", "delete", "питомцы")
def test_delete_pet(petstore_api: ApiClient):
    payload = pets_create_payload()

    create_pet(petstore_api, payload)

    with allure.step("Удалить питомца по id и проверить статус код"):
        response_delete = petstore_api.delete(f"/pet/{payload.id}")
        assert response_delete.status_code == 200

    with allure.step("Десериализовать и проверить схему response body"):
        data_delete = response_delete.json()
        delete_response_model = DeletePetResponse.model_validate(data_delete)

        schema_delete_response = load_schema("delete_response_schema.json")

        validate(data_delete, schema=schema_delete_response)

    with allure.step("Проверить, что API вернул id удалённого питомца"):
        assert delete_response_model.type == "unknown"
        assert delete_response_model.message == str(payload.id)


@allure.epic("API-тестирование")
@allure.feature("Petstore API")
@allure.story("Негативные проверки")
@allure.title("Получение удалённого питомца")
@allure.description("Проверяем, что после удаления питомца GET /pet/{id} возвращает 404.")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("api", "petstore", "negative", "get", "delete")
def test_negative_get(petstore_api: ApiClient):
    payload = pets_create_payload()

    create_pet(petstore_api, payload)

    with allure.step("Удалить питомца по id и проверить статус код"):
        response_delete = petstore_api.delete(f"/pet/{payload.id}")
        assert response_delete.status_code == 200

    with allure.step("Проверить response body удаления"):
        data_delete = response_delete.json()
        delete_response_model = DeletePetResponse.model_validate(data_delete)

        schema_delete_response = load_schema("delete_response_schema.json")

        validate(data_delete, schema=schema_delete_response)

        assert delete_response_model.type == "unknown"
        assert delete_response_model.message == str(payload.id)

    with allure.step("Запросить удалённого питомца и проверить статус 404"):
        response_get = petstore_api.get(f"/pet/{payload.id}")
        assert response_get.status_code == 404

    with allure.step("Проверить тело ошибки"):
        data_get = response_get.json()
        error_response_model = PetErrorResponse.model_validate(data_get)

        schema_get_error_response = load_schema("error_get_schema.json")
        validate(data_get, schema=schema_get_error_response)

        assert error_response_model.type == "error"
        assert error_response_model.message == "Pet not found"


@allure.epic("API-тестирование")
@allure.feature("Petstore API")
@allure.story("Негативные проверки")
@allure.title("Повторное удаление питомца")
@allure.description("Проверяем, что повторный DELETE /pet/{id} для уже удалённого питомца возвращает 404.")
@allure.severity(allure.severity_level.NORMAL)
@allure.tag("api", "petstore", "negative", "delete")
def test_delete_error(petstore_api: ApiClient):
    payload = pets_create_payload()

    create_pet(petstore_api, payload)

    with allure.step("Удалить питомца по id и проверить статус код"):
        response_delete = petstore_api.delete(f"/pet/{payload.id}")
        assert response_delete.status_code == 200

    with allure.step("Проверить response body первого удаления"):
        data_delete = response_delete.json()
        delete_response_model = DeletePetResponse.model_validate(data_delete)

        schema_delete_response = load_schema("delete_response_schema.json")

        validate(data_delete, schema=schema_delete_response)

        assert delete_response_model.type == "unknown"
        assert delete_response_model.message == str(payload.id)

    with allure.step("Повторно удалить питомца и проверить ошибку 404"):
        response_delete_2 = petstore_api.delete(f"/pet/{payload.id}")
        assert response_delete_2.status_code == 404
        assert not response_delete_2.content
