"""Tests deterministas del motor, con dados inyectados."""
import itertools

import pytest

from turno import (ATACANTE, DEFENSOR, BOSQUE, LLANURA, MONTANA, RAZAS, RIO,
                   Ejercito, Raza, bonos_pasivos, simular)

NEUTRA = Raza("neutra", "Neutra")


class Secuencia:
    """Dado guionizado: devuelve los valores en orden y falla si se piden de más."""

    def __init__(self, *valores):
        self._it = iter(valores)
        self.pedidos = 0

    def __call__(self):
        self.pedidos += 1
        try:
            return next(self._it)
        except StopIteration:
            raise AssertionError("El motor pidió más tiradas de las previstas")


def ej(raza=NEUTRA, tropas=1, bon=0, **kw):
    return Ejercito(raza, tropas, bon, **kw)


# ---------- Reglas básicas ----------

def test_gana_atacante_y_defensor_pierde_una_tropa():
    r = simular(ej(tropas=2), ej(tropas=2), tirar=Secuencia(4, 2, 4, 1))
    assert r.rondas[0].resultado == "atacante"
    assert r.rondas[0].tropas_defensor == 1
    assert r.ganador == ATACANTE and r.tropas_defensor == 0


def test_gana_defensor():
    r = simular(ej(), ej(), tirar=Secuencia(1, 3))
    assert r.ganador == DEFENSOR and r.tropas_atacante == 0


def test_empate_no_quita_tropas_pero_cuenta_ronda():
    r = simular(ej(), ej(), tirar=Secuencia(2, 2, 3, 1))
    assert r.rondas[0].resultado == "empate"
    assert (r.rondas[0].tropas_atacante, r.rondas[0].tropas_defensor) == (1, 1)
    assert len(r.rondas) == 2 and r.ganador == ATACANTE


def test_bonificador_negativo_puede_perder_con_dado_alto():
    r = simular(ej(bon=-3), ej(), tirar=Secuencia(4, 2))
    assert r.rondas[0].total_ataque == 1
    assert r.ganador == DEFENSOR


def test_bonificador_positivo_decide():
    r = simular(ej(bon=2), ej(), tirar=Secuencia(1, 2))
    assert r.rondas[0].total_ataque == 3 and r.ganador == ATACANTE


# ---------- Fin de combate y casos límite ----------

def test_tropas_cero_no_hay_rondas():
    r = simular(ej(tropas=0), ej(tropas=3), tirar=Secuencia())
    assert r.rondas == [] and r.ganador == DEFENSOR
    r = simular(ej(tropas=0), ej(tropas=0), tirar=Secuencia())
    assert r.ganador is None


def test_tropas_negativas_lanzan_error():
    with pytest.raises(ValueError):
        simular(ej(tropas=-1), ej())


def test_no_modifica_los_ejercitos_de_entrada():
    a, d = ej(tropas=3), ej(tropas=3)
    simular(a, d)
    assert (a.tropas, d.tropas) == (3, 3)


def test_combate_infinito_se_interrumpe():
    ciclo = itertools.cycle([2, 1])  # atacante siempre gana con 2: sin efecto en ciudadela
    r = simular(ej(tropas=5), ej(tropas=5), ciudadela=True,
                tirar=lambda: next(ciclo), max_rondas=50)
    assert r.interrumpida and r.ganador is None and len(r.rondas) == 50


# ---------- Pasivo Humano / Corrupto ----------

def test_humano_atacante_dado_fijo_en_ronda_3_sin_consumir_tirada():
    tirar = Secuencia(1, 1, 2, 2, 1)  # r1: 2 tiradas, r2: 2, r3: solo el defensor
    r = simular(ej(RAZAS["humano"]), ej(), tirar=tirar)
    assert (r.rondas[2].dado_ataque, r.rondas[2].dado_defensa) == (4, 1)
    assert tirar.pedidos == 5 and r.ganador == ATACANTE


def test_ambos_con_pasivo_sacan_4_sin_tirar():
    tirar = Secuencia(1, 1, 1, 1, 4, 1)  # r1 2, r2 2, r3 0, r4 2
    r = simular(ej(RAZAS["humano"]), ej(RAZAS["corrupto"]), tirar=tirar)
    assert (r.rondas[2].dado_ataque, r.rondas[2].dado_defensa) == (4, 4)
    assert r.rondas[2].resultado == "empate"
    assert tirar.pedidos == 6


def test_corrupto_defensor_fijo_en_rondas_3_y_6_pero_no_en_otras():
    tirar = Secuencia(1, 1, 2, 2, 1, 1, 1, 2, 2, 1)
    r = simular(ej(tropas=3), ej(RAZAS["corrupto"], tropas=3), tirar=tirar, max_rondas=6)
    fijas = [x.numero for x in r.rondas if x.dado_defensa == 4]
    assert fijas == [3, 6]
    assert r.rondas[3].dado_defensa == 1  # ronda 4: tirada normal


def test_otras_razas_no_tienen_dado_fijo():
    for rid in ("enano", "elfo", "orco", "elfo_oscuro"):
        assert not RAZAS[rid].dado_fijo_cada_3_rondas


# ---------- Ciudadela ----------

def test_ciudadela_atacante_gana_con_total_2_no_hace_dano():
    r = simular(ej(), ej(), ciudadela=True, tirar=Secuencia(2, 1), max_rondas=1)
    assert r.rondas[0].resultado == "sin_efecto"
    assert (r.tropas_atacante, r.tropas_defensor) == (1, 1)


def test_ciudadela_atacante_gana_con_total_3_hace_dano():
    r = simular(ej(), ej(), ciudadela=True, tirar=Secuencia(3, 1))
    assert r.ganador == ATACANTE


def test_ciudadela_cuenta_el_total_con_bonificador_no_solo_el_dado():
    r = simular(ej(bon=2), ej(), ciudadela=True, tirar=Secuencia(1, 1))
    assert r.rondas[0].total_ataque == 3 and r.ganador == ATACANTE


def test_ciudadela_el_defensor_gana_con_normalidad():
    r = simular(ej(), ej(), ciudadela=True, tirar=Secuencia(1, 4))
    assert r.ganador == DEFENSOR


def test_sin_ciudadela_total_2_si_hace_dano():
    r = simular(ej(), ej(), ciudadela=False, tirar=Secuencia(2, 1))
    assert r.ganador == ATACANTE


# ---------- Pasivos por raza (tabla) ----------

def total(e, rol, terreno):
    return sum(b for _, b in bonos_pasivos(e, rol, terreno))


@pytest.mark.parametrize("raza,rol,terreno,esperado", [
    ("elfo", ATACANTE, LLANURA, 1),
    ("elfo", ATACANTE, BOSQUE, 1),
    ("elfo", DEFENSOR, LLANURA, 0),
    ("elfo", DEFENSOR, BOSQUE, 1),
    ("elfo", DEFENSOR, RIO, 0),
    ("elfo_oscuro", DEFENSOR, LLANURA, 1),
    ("elfo_oscuro", DEFENSOR, MONTANA, 1),
    ("elfo_oscuro", ATACANTE, LLANURA, 0),
    ("enano", ATACANTE, MONTANA, 1),
    ("enano", DEFENSOR, MONTANA, 1),
    ("enano", ATACANTE, LLANURA, 0),
    ("enano", DEFENSOR, RIO, 0),
    ("humano", ATACANTE, MONTANA, 0),
    ("corrupto", DEFENSOR, BOSQUE, 0),
    ("orco", ATACANTE, MONTANA, 0),
    ("orco", DEFENSOR, MONTANA, 0),
])
def test_pasivos_de_raza(raza, rol, terreno, esperado):
    assert total(ej(RAZAS[raza]), rol, terreno) == esperado


@pytest.mark.parametrize("rol,terreno,esperado", [
    (ATACANTE, LLANURA, 2),
    (ATACANTE, MONTANA, 2),
    (DEFENSOR, MONTANA, -1),
    (DEFENSOR, LLANURA, 0),
    (DEFENSOR, RIO, 0),
])
def test_orco_tercer_ataque(rol, terreno, esperado):
    assert total(ej(RAZAS["orco"], tercer_ataque_orco=True), rol, terreno) == esperado


def test_pasivo_se_aplica_en_la_simulacion_y_se_suma_al_bonificador():
    r = simular(ej(RAZAS["elfo"], bon=1), ej(), tirar=Secuencia(1, 3), max_rondas=1)
    assert r.rondas[0].total_ataque == 3  # 1 + 1 (manual) + 1 (elfo)
    assert r.rondas[0].resultado == "empate"
    assert r.bono_total_atacante == 2


def test_enano_defendiendo_en_montana_gana_empates_de_dado():
    r = simular(ej(), ej(RAZAS["enano"]), terreno=MONTANA, tirar=Secuencia(3, 3))
    assert r.ganador == DEFENSOR
