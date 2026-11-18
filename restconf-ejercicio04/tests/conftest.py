"""Fixtures compartidas: configuración de ejemplo y cliente falso (sin red)."""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def root():
    return ROOT


@pytest.fixture
def cfg():
    with open(ROOT / "config" / "vars.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


class FakeClient:
    """Sustituye a RestconfClient: guarda un 'estado' en memoria."""

    def __init__(self, state=None):
        self.state = dict(state or {})
        self.puts = []

    def get(self, path):
        return self.state.get(path)

    def put(self, path, payload):
        self.puts.append((path, payload))
        self.state[path] = payload
        return 201


@pytest.fixture
def fake_client_cls():
    return FakeClient
