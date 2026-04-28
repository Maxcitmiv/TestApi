import json
from pathlib import Path


BASE_PATH = Path(__file__).parent.parent / "schemas"


def load_schema(name: str) -> dict:
    with open(BASE_PATH / name, encoding="utf-8") as file:
        return json.load(file)