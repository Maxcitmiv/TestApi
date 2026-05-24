from pydantic import BaseModel, ConfigDict


class AddToCartResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    message: str
    updatetopcartsectionhtml: str
    updateflyoutcartsectionhtml: str
