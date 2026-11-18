"""Pruebas de deploy.py: --check, aplicar e idempotencia (sin switch real)."""
import sys

import deploy
from payloads import build_items


def _ejecutar(monkeypatch, root, cliente, *extra):
    monkeypatch.setattr(deploy, "RestconfClient", lambda *a, **k: cliente)
    argv = ["deploy.py", "--config", str(root / "config" / "vars.yml"), *extra]
    monkeypatch.setattr(sys, "argv", argv)
    return deploy.main()


def test_check_no_modifica_el_equipo(monkeypatch, root, capsys, fake_client_cls):
    cliente = fake_client_cls()  # switch vacío
    assert _ejecutar(monkeypatch, root, cliente, "--check") == 0
    salida = capsys.readouterr().out
    assert cliente.puts == []                     # nunca hizo PUT
    assert salida.count("[CAMBIO]") == 4
    assert "4 cambio(s) pendiente(s)" in salida


def test_aplica_los_cuatro_recursos(monkeypatch, root, capsys, fake_client_cls):
    cliente = fake_client_cls()
    assert _ejecutar(monkeypatch, root, cliente) == 0
    salida = capsys.readouterr().out
    assert len(cliente.puts) == 4
    assert salida.count("[APLICADO] HTTP 201") == 4
    assert "4 cambio(s) aplicado(s)" in salida


def test_segunda_ejecucion_es_idempotente(monkeypatch, root, capsys,
                                          fake_client_cls, cfg):
    estado = {p: body for p, body in build_items(cfg)}
    cliente = fake_client_cls(estado)             # ya está configurado
    assert _ejecutar(monkeypatch, root, cliente) == 0
    salida = capsys.readouterr().out
    assert cliente.puts == []
    assert salida.count("[OK]") == 4
    assert "0 cambio(s) aplicado(s)" in salida


def test_corrige_solo_la_desviacion(monkeypatch, root, capsys,
                                    fake_client_cls, cfg):
    items = build_items(cfg)
    estado = {p: body for p, body in items}
    ruta_snmp = items[2][0]                       # alguien cambió location
    estado[ruta_snmp] = {"Cisco-IOS-XE-snmp:location": "OTRO-LUGAR"}
    cliente = fake_client_cls(estado)
    _ejecutar(monkeypatch, root, cliente)
    assert [p for p, _ in cliente.puts] == [ruta_snmp]
    assert "[APLICADO]" in capsys.readouterr().out
