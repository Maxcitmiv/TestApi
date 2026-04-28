from pydantic import BaseModel

class PetRequest(BaseModel):
    id: int
    category: Category
    name: str
    photoUrls: list[str]
    tags: list[Tag]
    status: str