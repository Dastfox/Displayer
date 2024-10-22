import uuid
from typing import List
from urllib.parse import unquote

from config import STATIC_DIR

EXCLUDED_DIRECTORIES = [
    "Backgrounds",
    "unreachable",
]

class FileService:
    @staticmethod
    def get_all_files() -> List[str]:
        files = []
        for file_path in STATIC_DIR.rglob("*"):
            if file_path.is_file() and file_path.parent.name not in EXCLUDED_DIRECTORIES:
                rel_path = file_path.relative_to(STATIC_DIR)
                files.append(str(rel_path))
        return files

    @staticmethod
    def get_file_content(file_path: str) -> str:
        try:
            with open(f'{STATIC_DIR}/{file_path}', 'r') as f:
                return f.read()
        except:
            return ""

    @staticmethod
    def verify_file(file: str) -> tuple[bool, str]:
        decoded_file = unquote(file)
        file_path = STATIC_DIR / decoded_file
        if not file_path.exists() or not file_path.is_file():
            return False, decoded_file
        return True, decoded_file

    @staticmethod
    def generate_unique_url(file: str) -> str:
        unique_id = str(uuid.uuid4())
        return f"/display/{unique_id}"