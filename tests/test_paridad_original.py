"""Paridad con el programa C++ original.

`referencia_cpp` es una traducción literal del bucle del C++ (solo con los
pasivos que el original implementaba: Humano y Corrupto en rondas 3, 6, 9...).
Con la misma semilla, el motor nuevo debe dar exactamente el mismo resultado.
"""
import random

import pytest

from turno import RAZAS, Ejercito, Raza, crear_tirador, simular

NEUTRA = Raza("neutra", "Neutra")
RAZAS_ORIGINAL = [RAZAS["humano"], RAZAS["corrupto"], NEUTRA]


def referencia_cpp(fijo1, fijo2, bon1, bon2, ejer1, ejer2, ciudadela, tirar, tope=1000):
    n = min(ejer1, ejer2)
    l = 1
    while n > 0 and l <= tope:
        caso = 0
        if l % 3 == 0 and fijo1:
            caso += 1
        if l % 3 == 0 and fijo2:
            caso += 2
        if caso == 1:
            dado1, dado2 = 4 + bon1, tirar() + bon2
        elif caso == 2:
            dado1, dado2 = tirar() + bon1, 4 + bon2
        elif caso == 3:
            dado1, dado2 = 4 + bon1, 4 + bon2
        else:
            dado1 = tirar() + bon1
            dado2 = tirar() + bon2
        if not ciudadela:
            if dado1 > dado2:
                ejer2 -= 1
            elif dado2 > dado1:
                ejer1 -= 1
        else:
            if dado1 > dado2 and dado1 > 2:
                ejer2 -= 1
            elif dado2 > dado1:
                ejer1 -= 1
        n = min(ejer1, ejer2)
        l += 1
    return ejer1, ejer2, l - 1


@pytest.mark.parametrize("semilla", range(300))
def test_paridad_con_cpp(semilla):
    azar = random.Random(1000 + semilla)
    r1, r2 = azar.choice(RAZAS_ORIGINAL), azar.choice(RAZAS_ORIGINAL)
    b1, b2 = azar.randint(-2, 3), azar.randint(-2, 3)
    t1, t2 = azar.randint(1, 8), azar.randint(1, 8)
    ciudadela = azar.random() < 0.5

    esperado = referencia_cpp(r1.dado_fijo_cada_3_rondas, r2.dado_fijo_cada_3_rondas,
                              b1, b2, t1, t2, ciudadela, crear_tirador(semilla))
    res = simular(Ejercito(r1, t1, b1), Ejercito(r2, t2, b2), ciudadela=ciudadela,
                  tirar=crear_tirador(semilla), max_rondas=1000)
    assert (res.tropas_atacante, res.tropas_defensor, len(res.rondas)) == esperado
