"""EAWS simplificado e independiente del cálculo REBA."""

from dataclasses import asdict, dataclass
from typing import Any

from .config import EawsConfig


@dataclass(frozen=True)
class ResultadoEaws:
    duracion_min_turno: float
    postura: int
    fuerza: int
    frecuencia: int
    total: int
    nivel: str

    def a_diccionario(self) -> dict[str, Any]:
        return asdict(self)


def calcular_eaws(
    tiempo_ciclo_s: float, frecuencia_por_ciclo: float, carga_kg: float, flexion_tronco: float,
    torsion_tronco: float, sobre_hombro: bool, bajo_rodilla: bool, horas_turno: float,
    tiempo_movimiento_s: float, config: EawsConfig,
) -> ResultadoEaws:
    """Aplica literalmente la fórmula EAWS simplificada del documento Jabil."""

    if tiempo_ciclo_s <= 0 or horas_turno < 0 or tiempo_movimiento_s < 0:
        raise ValueError("EAWS: tiempo de ciclo debe ser positivo; duraciones no negativas.")
    duracion = (tiempo_movimiento_s * frecuencia_por_ciclo * (3600 / tiempo_ciclo_s) * horas_turno) / 60
    postura = (1 if flexion_tronco < config.tronco.leve else 3 if flexion_tronco < config.tronco.moderado else 6)
    postura += 0 if torsion_tronco < config.torsion_deg else 2
    postura += 2 * int(sobre_hombro) + 2 * int(bajo_rodilla)
    fuerza = 1 if carga_kg < config.carga_kg.baja else 3 if carga_kg < config.carga_kg.alta else 6
    acciones = (duracion * 60 / tiempo_ciclo_s) * frecuencia_por_ciclo
    frecuencia = 1 if acciones < config.acciones.baja else 3 if acciones < config.acciones.alta else 6
    total = postura + fuerza + frecuencia
    nivel = "Bajo" if total <= 5 else "Medio" if total <= 10 else "Alto"
    return ResultadoEaws(duracion, postura, fuerza, frecuencia, total, nivel)
