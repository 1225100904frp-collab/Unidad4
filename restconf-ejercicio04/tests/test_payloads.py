"""Pruebas unitarias de payloads.py (sin conexión al switch)."""
from payloads import NATIVE, build_items, is_subset


def test_cuatro_recursos(cfg):
    assert len(build_items(cfg)) == 4


def test_rutas_yang(cfg):
    paths = [p for p, _ in build_items(cfg)]
    assert paths[0] == f"{NATIVE}/interface/Loopback=201"
    assert paths[1].endswith("snmp:community=DEVOPS-RO")
    assert paths[2].endswith("snmp:location")
    assert paths[3].endswith("snmp:contact")


def test_loopback_ip_en_payload(cfg):
    path, body = build_items(cfg)[0]
    assert "Loopback=201" in path
    lb = body["Cisco-IOS-XE-native:Loopback"]
    prim = lb["ip"]["address"]["primary"]
    assert prim["address"] == cfg["loopback"]["ip"]
    assert prim["mask"] == cfg["loopback"]["mask"]


def test_loopback_nombre_y_descripcion(cfg):
    lb = build_items(cfg)[0][1]["Cisco-IOS-XE-native:Loopback"]
    assert lb["name"] == cfg["loopback"]["id"]
    assert lb["description"] == cfg["loopback"]["description"]


def test_snmp_comunidad_solo_lectura(cfg):
    body = build_items(cfg)[1][1]["Cisco-IOS-XE-snmp:community"]
    assert body["name"] == cfg["snmp"]["community"]
    assert "RO" in body


def test_snmp_location_y_contact(cfg):
    assert build_items(cfg)[2][1] == {
        "Cisco-IOS-XE-snmp:location": cfg["snmp"]["location"]}
    assert build_items(cfg)[3][1] == {
        "Cisco-IOS-XE-snmp:contact": cfg["snmp"]["contact"]}


def test_cambiar_id_cambia_la_ruta(cfg):
    cfg["loopback"]["id"] = 777
    assert build_items(cfg)[0][0].endswith("Loopback=777")


def test_is_subset_basico():
    assert is_subset({"a": 1}, {"a": 1, "b": 2})
    assert not is_subset({"a": 1}, {"a": 2})


def test_is_subset_anidado():
    deseado = {"ip": {"address": {"primary": {"address": "10.0.0.1"}}}}
    primario = {"address": "10.0.0.1", "mask": "255.0.0.0"}
    actual = {"ip": {"address": {"primary": primario}}}
    assert is_subset(deseado, actual)
    actual["ip"]["address"]["primary"]["address"] = "10.0.0.2"
    assert not is_subset(deseado, actual)


def test_is_subset_clave_faltante():
    assert not is_subset({"a": 1}, {"b": 1})


def test_is_subset_listas_y_tipos():
    assert is_subset({"RO": [None]}, {"RO": [None]})
    assert not is_subset({"RO": [None]}, {"RO": []})
    assert is_subset({"id": 201}, {"id": "201"})  # compara como texto
    assert not is_subset({"a": 1}, None)
