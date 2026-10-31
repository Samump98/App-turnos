import json

import pytest

from turno import RAZAS, Ejercito, crear_tirador, simular
from turno.historial import crear_registro, exportar_json, fusionar, importar_json


def registro():
    a, d = Ejercito(RAZAS["elfo"], 4, 1), Ejercito(RAZAS["enano"], 3)
    res = simular(a, d, tirar=crear_tirador(1))
    return crear_registro(a, d, "Montaña", False, res)


def test_registro_tiene_los_campos_esperados():
    r = registro()
    assert r["atacante"]["raza"] == "Elfo" and r["terreno"] == "Montaña"
    assert r["ganador"] in ("atacante", "defensor")
    assert len(r["rondas"]) >= 3


def test_exportar_e_importar_es_ida_y_vuelta():
    regs = [registro(), registro()]
    assert importar_json(exportar_json(regs)) == regs


@pytest.mark.parametrize("texto", ["no es json", "[]", '{"registros": 3}',
                                   '{"registros": [{"id": "x"}]}'])
def test_importar_rechaza_archivos_invalidos(texto):
    with pytest.raises(ValueError):
        importar_json(texto)


def test_fusionar_no_duplica_ids():
    r1, r2 = registro(), registro()
    lista, n = fusionar([r1], [r1, r2])
    assert n == 1 and len(lista) == 2


def test_exportacion_conserva_acentos():
    assert "Montaña" in exportar_json([registro()])
    assert json.loads(exportar_json([registro()]))["version"] == 1
