from pathlib import Path
from uuid import uuid4


class LocalFileStorage:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        path = self.base_dir / f"{uuid4()}_{safe_name}"
        path.write_bytes(content)
        return str(path)

    def get_path(self, stored_path: str) -> str:
        return stored_path
