import os
import sys
from pathlib import Path

# Set test JWT_SECRET_KEY before any module imports settings
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test_jwt_secret_key_minimum_thirty_two_chars_long_123456",
)

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
