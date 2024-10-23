# service/file_service.py
import uuid
from typing import List, Dict, Union
from urllib.parse import unquote
from pathlib import Path

from config import STATIC_DIR

EXCLUDED_DIRECTORIES = [
    # "Backgrounds",
    "unreachable",
]


class FileService:
    @staticmethod
    def get_file_structure() -> Dict[str, Union[str, dict]]:
        """Returns a nested dictionary representing the file structure."""

        def build_structure(path: Path) -> Union[Dict, str]:
            if path.is_file():
                return str(path.relative_to(STATIC_DIR))

            structure = {}
            for item in path.iterdir():
                if item.name.startswith('.') or item.name in EXCLUDED_DIRECTORIES:
                    continue

                if item.is_dir():
                    sub_structure = build_structure(item)
                    if sub_structure:  # Only add non-empty directories
                        structure[item.name] = sub_structure
                else:
                    structure[item.name] = str(item.relative_to(STATIC_DIR))

            return structure

        return build_structure(STATIC_DIR)

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
        if not file:
            return False, ""
        decoded_file = unquote(file)
        file_path = STATIC_DIR / decoded_file
        if not file_path.exists() or not file_path.is_file():
            return False, decoded_file
        return True, decoded_file

    @staticmethod
    def generate_unique_url(file: str) -> str:
        unique_id = str(uuid.uuid4())
        return f"/display/{unique_id}"