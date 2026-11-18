"""Pruebas de verify.py (fase Monitor)."""
import verify
from payloads import build_items


def _ejecutar(monkeypatch, root, cliente):
    monkeypatch.chdir(root)  # verify.py lee config/vars.yml con ruta relativa
    monkeypatch.setattr(verify, "RestconfClient", lambda *a, **k: cliente)
    return verify.main()


def test_todo_pass_devuelve_cero(monkeypatch, root, capsys, fake_client_cls, cfg):
    cliente = fake_client_cls({p: b for p, b in build_items(cfg)})
    assert _ejecutar(monkeypatch, root, cliente) == 0
    assert capsys.readouterr().out.count("[PASS]") == 4


def test_recurso_faltante_devuelve_uno(monkeypatch, root, capsys, fake_client_cls):
    cliente = fake_client_cls()  # switch sin configurar
    assert _ejecutar(monkeypatch, root, cliente) == 1
    assert capsys.readouterr().out.count("[FAIL]") == 4


def test_desviacion_detectada(monkeypatch, root, capsys, fake_client_cls, cfg):
    items = build_items(cfg)
    estado = {p: b for p, b in items}
    estado[items[3][0]] = {"Cisco-IOS-XE-snmp:contact": "otro@correo.com"}
    assert _ejecutar(monkeypatch, root, fake_client_cls(estado)) == 1
    salida = capsys.readouterr().out
    assert salida.count("[PASS]") == 3
    assert salida.count("[FAIL]") == 1
