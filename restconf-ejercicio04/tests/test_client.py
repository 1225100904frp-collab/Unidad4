"""Pruebas de RestconfClient con requests simulado (sin red)."""
import pytest

import restconf_client
from restconf_client import RestconfClient


class FakeResponse:
    def __init__(self, status=200, body=None, text=None):
        self.status_code = status
        self._body = body
        self.text = text if text is not None else ("x" if body else "")

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SANDBOX_USER", "usuario")
    monkeypatch.setenv("SANDBOX_PASS", "clave")
    monkeypatch.delenv("VERIFY_SSL", raising=False)
    return RestconfClient("switch.example.com")


def test_url_base(client):
    assert client.base == "https://switch.example.com:443/restconf/data"
    assert client._url("a/b") == client.base + "/a/b"


def test_credenciales_desde_entorno(client):
    assert client.auth == ("usuario", "clave")


def test_verify_ssl_apagado_por_defecto(client):
    assert client.verify is False


def test_verify_ssl_activable(monkeypatch):
    monkeypatch.setenv("SANDBOX_USER", "u")
    monkeypatch.setenv("SANDBOX_PASS", "p")
    monkeypatch.setenv("VERIFY_SSL", "true")
    assert RestconfClient("h").verify is True


def test_sin_credenciales_falla(monkeypatch):
    monkeypatch.delenv("SANDBOX_USER", raising=False)
    monkeypatch.delenv("SANDBOX_PASS", raising=False)
    with pytest.raises(KeyError):
        RestconfClient("h")


def test_get_devuelve_json(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "get",
                        lambda *a, **k: FakeResponse(200, {"ok": 1}))
    assert client.get("ruta") == {"ok": 1}


def test_get_404_devuelve_none(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "get",
                        lambda *a, **k: FakeResponse(404))
    assert client.get("ruta") is None


def test_get_cuerpo_vacio_devuelve_none(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "get",
                        lambda *a, **k: FakeResponse(200, text=""))
    assert client.get("ruta") is None


def test_get_error_500_lanza(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "get",
                        lambda *a, **k: FakeResponse(500))
    with pytest.raises(RuntimeError):
        client.get("ruta")


@pytest.mark.parametrize("codigo", [201, 204])
def test_put_devuelve_codigo(client, monkeypatch, codigo):
    visto = {}

    def falso_put(url, **kwargs):
        visto.update(url=url, **kwargs)
        return FakeResponse(codigo)

    monkeypatch.setattr(restconf_client.requests, "put", falso_put)
    assert client.put("ruta", {"a": 1}) == codigo
    assert visto["url"].endswith("/ruta")
    assert visto["json"] == {"a": 1}
    assert visto["headers"]["Content-Type"] == "application/yang-data+json"


def test_put_error_400_lanza(client, monkeypatch):
    monkeypatch.setattr(restconf_client.requests, "put",
                        lambda *a, **k: FakeResponse(400))
    with pytest.raises(RuntimeError):
        client.put("ruta", {})
