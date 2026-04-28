import random
from faker import Faker
fake = Faker()

def pets_create_payload(pet_id=None):
    if pet_id is None:
        pet_id = random.randint(9182733, 123123123123)
    category_id=random.randint(9182733, 123123123123)
    name_category=fake.word()
    name=fake.name()
    url=fake.url()
    tag_id=random.randint(9182733, 123123123123)
    tag_name=fake.word()
    status = random.choice(["available", "pending", "sold"])

    payload={
    "id": pet_id,
    "category": {
        "id": category_id,
        "name": name_category
    },
    "name": name,
    "photoUrls": [
        url
    ],
    "tags": [
        {
            "id": tag_id,
            "name": tag_name
        }
    ],
    "status": status
    }

    return payload