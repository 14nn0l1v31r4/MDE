import pytest
from pydantic import ValidationError
from app.config.settings import Settings


def test_settings_fails_on_short_jwt_secret():
    with pytest.raises(ValidationError, match="pelo menos 32 caracteres"):
        Settings(jwt_secret_key="too_short_secret")


def test_settings_fails_on_insecure_default():
    with pytest.raises(ValidationError, match="não pode utilizar valores conhecidos"):
        Settings(jwt_secret_key="educational_analytics_super_secret_jwt_key_2026_dev_only")


def test_settings_accepts_valid_secret():
    valid = "this_is_a_very_secure_jwt_secret_key_32_chars"
    s = Settings(jwt_secret_key=valid)
    assert s.jwt_secret_key == valid
