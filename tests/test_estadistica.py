"""Tests estadísticos con semilla fija (reproducibles)."""
from collections import Counter

from turno import RAZAS, Ejercito, Raza, crear_tirador, simular

NEUTRA = Raza("neutra", "Neutra")


def tasa_victoria_atacante(atq, dfn, n=2000, **kw):
    tirar = crear_tirador(42)
    return sum(simular(atq, dfn, tirar=tirar, **kw).ganador == "atacante"
               for _ in range(n)) / n


def test_d4_uniforme():
    tirar = crear_tirador(7)
    n = 40_000
    cuenta = Counter(tirar() for _ in range(n))
    assert set(cuenta) == {1, 2, 3, 4}
    for cara in range(1, 5):
        assert abs(cuenta[cara] / n - 0.25) < 0.01


def test_tirador_con_misma_semilla_es_reproducible():
    a, b = crear_tirador(5), crear_tirador(5)
    assert [a() for _ in range(50)] == [b() for _ in range(50)]


def test_combate_simetrico_es_justo():
    tasa = tasa_victoria_atacante(Ejercito(NEUTRA, 5), Ejercito(NEUTRA, 5))
    assert 0.45 < tasa < 0.55


def test_mas_tropas_gana_mas_a_menudo():
    assert tasa_victoria_atacante(Ejercito(NEUTRA, 8), Ejercito(NEUTRA, 5)) > 0.75


def test_bono_de_elfo_atacante_mejora_su_tasa():
    base = tasa_victoria_atacante(Ejercito(NEUTRA, 5), Ejercito(NEUTRA, 5))
    elfo = tasa_victoria_atacante(Ejercito(RAZAS["elfo"], 5), Ejercito(NEUTRA, 5))
    assert elfo > base + 0.10


def test_ciudadela_perjudica_al_atacante():
    llano = tasa_victoria_atacante(Ejercito(NEUTRA, 5), Ejercito(NEUTRA, 5))
    ciud = tasa_victoria_atacante(Ejercito(NEUTRA, 5), Ejercito(NEUTRA, 5), ciudadela=True)
    assert ciud < llano
