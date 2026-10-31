"""Razas y terrenos definidos como DATOS.

Para añadir una raza o cambiar un pasivo basta con editar RAZAS:
el motor (motor.py) no necesita tocarse.
"""
from __future__ import annotations

from dataclasses import dataclass

LLANURA, MONTANA, BOSQUE, RIO = "Llanura", "Montaña", "Bosque", "Río"
TERRENOS = (LLANURA, MONTANA, BOSQUE, RIO)


@dataclass(frozen=True)
class Raza:
    id: str
    nombre: str
    descripcion: str = ""
    # Humano / Corrupto: en rondas 3, 6, 9... su dado no se tira y vale 4.
    dado_fijo_cada_3_rondas: bool = False
    bono_atacando: int = 0
    bono_defendiendo: int = 0
    # Bono que se aplica atacando Y defendiendo cuando el terreno es Montaña.
    bono_en_montana: int = 0
    # Pares (terreno, bono) que solo se aplican al DEFENDER.
    bonos_terreno_defensa: tuple[tuple[str, int], ...] = ()
    # Orco: el usuario marca "tercer ataque" a mano (ver docs/ESPECIFICACION.md).
    bono_tercer_ataque: int = 0                  # atacando: +2
    penal_defensa_montana_tras_ataque: int = 0   # defendiendo en Montaña: -1


RAZAS: dict[str, Raza] = {
    r.id: r
    for r in (
        Raza("humano", "Humano", "Rondas 3, 6, 9...: su dado vale 4 fijo.",
             dado_fijo_cada_3_rondas=True),
        Raza("enano", "Enano", "+1 atacando y defendiendo en Montaña.",
             bono_en_montana=1),
        Raza("elfo", "Elfo", "+1 siempre que ataca. +1 defendiendo en Bosque.",
             bono_atacando=1, bonos_terreno_defensa=((BOSQUE, 1),)),
        Raza("corrupto", "Corrupto", "Rondas 3, 6, 9...: su dado vale 4 fijo.",
             dado_fijo_cada_3_rondas=True),
        Raza("orco", "Orco",
             "Tercer ataque: +2 atacando. Tras él: -1 defendiendo en Montaña.",
             bono_tercer_ataque=2, penal_defensa_montana_tras_ataque=-1),
        Raza("elfo_oscuro", "Elfo oscuro", "+1 siempre que defiende.",
             bono_defendiendo=1),
    )
}
