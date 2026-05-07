from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path.cwd()


class DocumentGeneratorSchema(BaseModel):
    file_path: str
    name: str


def get_path(relative_path: str) -> Path:
    try:
        rel = Path(relative_path).resolve().relative_to(BASE_DIR)
        return rel
    except ValueError:
        raise ValueError("Path is outside BASE_DIR")
