# Ejercicio 04 - DevOps con RESTCONF (Cisco IOS-XE)

Configura Loopback de gestión y SNMP **sin tocar la consola**: todo cambio
pasa por Git -> Pull Request -> pipeline -> RESTCONF.

## Uso local (solo para pruebas)
    pip install -r requirements.txt
    pytest -v                      # 36 pruebas, no necesitan el switch
    export SANDBOX_USER=...  SANDBOX_PASS=...   # Windows: set VAR=valor
    python src/deploy.py --check   # prueba en seco
    python src/deploy.py           # aplica
    python src/verify.py           # monitoreo

## Mapeo al ciclo DevOps
| Fase | Evidencia |
|---|---|
| Plan | Issue con requisitos |
| Code | config/vars.yml, src/*.py |
| Build | yamllint + flake8 en el pipeline |
| Test | pytest + deploy.py --check |
| Release | PR aprobado, merge a main, tag v1.0 |
| Deploy | job deploy (PUT RESTCONF) |
| Operate | PUT idempotente; re-ejecutar corrige desviaciones |
| Monitor | verify.py + snmpwalk |

## Controles contra cambios manuales
- Rama main protegida (PR + revisión obligatoria)
- Credenciales solo en GitHub Secrets
- Despliegue únicamente desde el pipeline

## Pruebas (tests/)
| Archivo | Qué prueba |
|---|---|
| test_payloads.py | rutas YANG, contenido de los 4 payloads, `is_subset` |
| test_config.py | `vars.yml` válido (IP, máscara, id, comunidad, contacto) |
| test_client.py | cliente RESTCONF con `requests` simulado (200, 404, 400/500, PUT 201/204) |
| test_deploy.py | `--check` no modifica, aplica, idempotencia, corrige desviaciones |
| test_verify.py | `verify.py` devuelve PASS/FAIL y código de salida |

Todas corren sin conexión al switch, por eso pasan en cualquier runner.

## Sandbox por VPN (reserva)
El switch tiene IP privada: los runners de GitHub no llegan a él.
Por eso los pasos con el equipo solo corren si existe la variable de
repositorio `RESTCONF_REACHABLE=true` (Settings > Secrets and variables >
Actions > Variables). Sin ella el pipeline hace lint y pruebas unitarias, y
el despliegue se ejecuta desde la computadora con la VPN activa:

    set SANDBOX_USER=developer
    set SANDBOX_PASS=<contraseña de la ficha>
    python src/deploy.py --check
    python src/deploy.py
    python src/deploy.py          (2.a vez: [OK] sin cambios)
    python src/verify.py
