"""Motor de combate de Turno. Python puro: sin Streamlit, sin E/S.

El dado es inyectable (`tirar`) para poder testear de forma determinista.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from .razas import LLANURA, MONTANA, Raza

ATACANTE, DEFENSOR = "atacante", "defensor"
DADO_FIJO = 4          # valor del dado de Humano/Corrupto cada 3 rondas
MIN_CIUDADELA = 3      # total mínimo del atacante para dañar en ciudadela
MAX_RONDAS = 1000      # seguridad frente a combates que nunca terminan

Tirador = Callable[[], int]


def crear_tirador(semilla: int | None = None) -> Tirador:
    """Devuelve una función que tira un d4 (1-4). Con semilla es reproducible."""
    rng = random.Random(semilla)
    return lambda: rng.randint(1, 4)


@dataclass
class Ejercito:
    raza: Raza
    tropas: int
    bonificador: int = 0               # cartas u otros efectos manuales
    tercer_ataque_orco: bool = False   # atacante: +2 / defensor: -1 en montaña


@dataclass
class Ronda:
    numero: int
    dado_ataque: int
    dado_defensa: int
    total_ataque: int
    total_defensa: int
    resultado: str          # "atacante" | "defensor" | "empate" | "sin_efecto"
    tropas_atacante: int
    tropas_defensor: int
    notas: list[str] = field(default_factory=list)


@dataclass
class Resultado:
    ganador: str | None     # ATACANTE, DEFENSOR o None (sin ganador)
    rondas: list[Ronda]
    tropas_atacante: int
    tropas_defensor: int
    bono_total_atacante: int
    bono_total_defensor: int
    pasivos_atacante: list[tuple[str, int]]
    pasivos_defensor: list[tuple[str, int]]
    interrumpida: bool = False


def bonos_pasivos(ej: Ejercito, rol: str, terreno: str = LLANURA) -> list[tuple[str, int]]:
    """Bonos automáticos de la raza según rol y terreno (sin el bonificador manual)."""
    r, bonos = ej.raza, []
    if rol == ATACANTE and r.bono_atacando:
        bonos.append((f"{r.nombre} atacando", r.bono_atacando))
    if rol == DEFENSOR and r.bono_defendiendo:
        bonos.append((f"{r.nombre} defendiendo", r.bono_defendiendo))
    if terreno == MONTANA and r.bono_en_montana:
        bonos.append((f"{r.nombre} en {terreno}", r.bono_en_montana))
    if rol == DEFENSOR:
        for t, b in r.bonos_terreno_defensa:
            if t == terreno:
                bonos.append((f"{r.nombre} defendiendo en {terreno}", b))
    if ej.tercer_ataque_orco:
        if rol == ATACANTE and r.bono_tercer_ataque:
            bonos.append((f"{r.nombre}: ataque potenciado", r.bono_tercer_ataque))
        if rol == DEFENSOR and terreno == MONTANA and r.penal_defensa_montana_tras_ataque:
            bonos.append((f"{r.nombre}: defensa debilitada en {terreno}",
                          r.penal_defensa_montana_tras_ataque))
    return bonos


def simular(
    atacante: Ejercito,
    defensor: Ejercito,
    terreno: str = LLANURA,
    ciudadela: bool = False,
    tirar: Tirador | None = None,
    max_rondas: int = MAX_RONDAS,
) -> Resultado:
    """Simula el combate completo. No modifica los ejércitos recibidos."""
    for e in (atacante, defensor):
        if e.tropas < 0:
            raise ValueError("Las tropas no pueden ser negativas")
    tirar = tirar or crear_tirador()

    pa = bonos_pasivos(atacante, ATACANTE, terreno)
    pd = bonos_pasivos(defensor, DEFENSOR, terreno)
    ba = atacante.bonificador + sum(b for _, b in pa)
    bd = defensor.bonificador + sum(b for _, b in pd)

    ta, td = atacante.tropas, defensor.tropas
    rondas: list[Ronda] = []
    n = 1
    while ta > 0 and td > 0 and n <= max_rondas:
        notas: list[str] = []
        fijo_a = n % 3 == 0 and atacante.raza.dado_fijo_cada_3_rondas
        fijo_d = n % 3 == 0 and defensor.raza.dado_fijo_cada_3_rondas
        # Orden de tirada igual al código original: primero atacante, luego defensor.
        da = DADO_FIJO if fijo_a else tirar()
        dd = DADO_FIJO if fijo_d else tirar()
        if fijo_a:
            notas.append(f"Dado fijo del atacante ({atacante.raza.nombre})")
        if fijo_d:
            notas.append(f"Dado fijo del defensor ({defensor.raza.nombre})")

        tot_a, tot_d = da + ba, dd + bd
        if tot_a > tot_d:
            if ciudadela and tot_a < MIN_CIUDADELA:
                resultado = "sin_efecto"
                notas.append(f"Ciudadela: el atacante necesita {MIN_CIUDADELA} o más")
            else:
                td -= 1
                resultado = "atacante"
        elif tot_d > tot_a:
            ta -= 1
            resultado = "defensor"
        else:
            resultado = "empate"

        rondas.append(Ronda(n, da, dd, tot_a, tot_d, resultado, ta, td, notas))
        n += 1

    if ta > 0 and td == 0:
        ganador = ATACANTE
    elif td > 0 and ta == 0:
        ganador = DEFENSOR
    else:
        ganador = None
    return Resultado(ganador, rondas, ta, td, ba, bd, pa, pd,
                     interrumpida=(ta > 0 and td > 0))
