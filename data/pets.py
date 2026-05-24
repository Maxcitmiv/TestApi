import random

from faker import Faker

from models.pets import Category, PetRequest, Tag

fake = Faker()


def pets_create_payload(pet_id=None):
    if pet_id is None:
        pet_id = random.randint(9182733, 123123123123)
    category_id = random.randint(9182733, 123123123123)
    name_category = fake.word()
    name = fake.name()
    url = fake.url()
    tag_id = random.randint(9182733, 123123123123)
    tag_name = fake.word()
    status = random.choice(["available", "pending", "sold"])

    return PetRequest(
        id=pet_id,
        category=Category(id=category_id, name=name_category),
        name=name,
        photoUrls=[url],
        tags=[Tag(id=tag_id, name=tag_name)],
        status=status,
    )
