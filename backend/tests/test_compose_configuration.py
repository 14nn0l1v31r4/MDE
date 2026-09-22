from pathlib import Path

import yaml


def test_backend_uvicorn_arguments_are_single_shell_command():
    compose_path = Path(__file__).parents[2] / "docker-compose.yml"
    compose = yaml.safe_load(compose_path.read_text(encoding="utf-8"))

    command = compose["services"]["backend"]["command"]

    assert "uvicorn app.interfaces.api.main:app --host 0.0.0.0 --port 8000" in command
