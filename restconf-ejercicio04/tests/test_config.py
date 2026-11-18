"""Valida que config/vars.yml tenga datos correctos antes de tocar el equipo."""
import ipaddress


def test_claves_obligatorias(cfg):
    assert {"host", "loopback", "snmp"} <= cfg.keys()
    assert {"id", "description", "ip", "mask"} <= cfg["loopback"].keys()
    assert {"community", "location", "contact"} <= cfg["snmp"].keys()


def test_ip_y_mascara_validas(cfg):
    ipaddress.IPv4Address(cfg["loopback"]["ip"])
    ipaddress.IPv4Address(cfg["loopback"]["mask"])


def test_id_loopback_en_rango(cfg):
    assert isinstance(cfg["loopback"]["id"], int)
    assert 0 <= cfg["loopback"]["id"] <= 2147483647


def test_comunidad_y_contacto(cfg):
    assert cfg["snmp"]["community"].strip() != ""
    assert "@" in cfg["snmp"]["contact"]


def test_puerto_https(cfg):
    assert cfg.get("port", 443) == 443


def test_sin_credenciales_en_el_repo(root):
    texto = (root / "config" / "vars.yml").read_text(encoding="utf-8").lower()
    assert "password" not in texto
    assert "pass:" not in texto
