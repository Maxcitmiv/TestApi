from typing import Literal

from pydantic import BaseModel, ConfigDict


PetStatus = Literal["available", "pending", "sold"]


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Category(ApiModel):
    id: int
    name: str


class Tag(ApiModel):
    id: int
    name: str


class PetRequest(ApiModel):
    id: int
    category: Category
    name: str
    photoUrls: list[str]
    tags: list[Tag]
    status: PetStatus


class PetResponse(ApiModel):
    id: int
    category: Category
    name: str
    photoUrls: list[str]
    tags: list[Tag]
    status: PetStatus


class DeletePetResponse(ApiModel):
    code: int
    type: str
    message: str


class PetErrorResponse(ApiModel):
    code: int
    type: str
    message: str
