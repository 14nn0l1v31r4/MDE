from pathlib import Path
from uuid import uuid4


class LocalFileStorage:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
    def __init__(self, base_dir: str, max_size_bytes: int = 50 * 1024 * 1024):
        self.base_dir = Path(base_dir).resolve()
        self.max_size_bytes = max_size_bytes
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        safe_name = filename.replace("/", "_").replace("\\", "_")
        path = self.base_dir / f"{uuid4()}_{safe_name}"
    def save(self, filename: str, content: bytes, user_id: str = "") -> str:
        if len(content) > self.max_size_bytes:
            raise ValueError(
                f"Arquivo excede o tamanho máximo permitido de {self.max_size_bytes} bytes."
            )

        # Sanitize filename (strip directory traversal attempts)
        clean_filename = Path(filename).name.replace("/", "_").replace("\\", "_").strip()
        if not clean_filename:
            clean_filename = "dataset.csv"

        target_dir = self.base_dir
        if user_id:
            safe_user_id = "".join(c for c in user_id if c.isalnum() or c in "-_")
            target_dir = (self.base_dir / safe_user_id).resolve()
            # Guard against directory escape
            if not str(target_dir).startswith(str(self.base_dir)):
                target_dir = self.base_dir
            target_dir.mkdir(parents=True, exist_ok=True)

        file_id = str(uuid4())
        path = target_dir / f"{file_id}_{clean_filename}"
        path.write_bytes(content)
        return str(path)

    def get_path(self, stored_path: str) -> str:
        return stored_path
        resolved = Path(stored_path).resolve()
        if not str(resolved).startswith(str(self.base_dir)):
            raise ValueError("Caminho de arquivo inválido ou fora do diretório de armazenamento permitido")
        return str(resolved)
