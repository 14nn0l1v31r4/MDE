from pathlib import Path
from typing import BinaryIO
from uuid import uuid4


class LocalFileStorage:
    def __init__(self, base_dir: str, max_size_bytes: int = 50 * 1024 * 1024):
        self.base_dir = Path(base_dir).resolve()
        self.max_size_bytes = max_size_bytes
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes, user_id: str = "") -> str:
        return self.save_stream(filename, _BytesReader(content), user_id=user_id)

    def save_stream(self, filename: str, stream: BinaryIO, user_id: str = "") -> str:
        clean_filename = self._validate_filename(filename)
        target_dir = self._target_dir(user_id)
        target_path = target_dir / f"{uuid4()}_{clean_filename}"
        partial_path = target_path.with_suffix(target_path.suffix + ".part")
        total_bytes = 0

        try:
            with partial_path.open("wb") as destination:
                while chunk := stream.read(64 * 1024):
                    total_bytes += len(chunk)
                    if total_bytes > self.max_size_bytes:
                        raise ValueError(
                            f"Arquivo excede o tamanho máximo permitido de {self.max_size_bytes} bytes."
                        )
                    destination.write(chunk)
            partial_path.replace(target_path)
        except Exception:
            partial_path.unlink(missing_ok=True)
            raise

        return str(target_path)

    def get_path(self, stored_path: str) -> str:
        resolved = Path(stored_path).resolve()
        if not resolved.is_relative_to(self.base_dir):
            raise ValueError("Caminho de arquivo inválido ou fora do diretório de armazenamento permitido")
        return str(resolved)

    def _target_dir(self, user_id: str) -> Path:
        if not user_id:
            return self.base_dir

        safe_user_id = "".join(c for c in user_id if c.isalnum() or c in "-_")
        target_dir = (self.base_dir / safe_user_id).resolve()
        if not target_dir.is_relative_to(self.base_dir):
            raise ValueError("Identificador de usuário inválido")
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    @staticmethod
    def _validate_filename(filename: str) -> str:
        if "\x00" in filename or "/" in filename or "\\" in filename:
            raise ValueError("Nome de arquivo inválido")
        clean_filename = Path(filename).name.strip()
        if not clean_filename or clean_filename in {".", ".."}:
            raise ValueError("Nome de arquivo inválido")
        return clean_filename


class _BytesReader:
    def __init__(self, content: bytes):
        self.content = content
        self.offset = 0

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self.content) - self.offset
        chunk = self.content[self.offset : self.offset + size]
        self.offset += len(chunk)
        return chunk
