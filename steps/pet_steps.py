import allure
from jsonschema import validate

from models.pets import PetRequest, PetResponse
from schemas.schemas import pet_create_and_get_schema
from utils.api_client import ApiClient
from utils.schema_loader import load_schema


@allure.step("Создать питомца через API")
def create_pet(api_client: ApiClient, payload: PetRequest) -> PetResponse:
    with allure.step("Сформировать и проверить request body"):
        request_data = payload.model_dump(mode="json")
        validate(request_data, schema=load_schema("pet_request_schema.json"))

    with allure.step("Отправить POST /pet и проверить статус код"):
        response = api_client.post("/pet", json=request_data)
        assert response.status_code == 200

    with allure.step("Десериализовать и проверить response body"):
        response_data = response.json()
        response_model = PetResponse.model_validate(response_data)

        validate(response_data, schema=pet_create_and_get_schema)

    return response_model
