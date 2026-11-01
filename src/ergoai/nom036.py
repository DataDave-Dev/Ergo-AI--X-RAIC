"""Sugerencias visuales NOM-036-1; no son una evaluación normativa final."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SugerenciaNom:
    categoria: str
    puntaje_visual: int
    nivel: str
    sugerencia: str = "confirmar por el especialista"

    def a_diccionario(self) -> dict[str, Any]:
        return asdict(self)


def _nivel(puntaje: int) -> str:
    return "verde" if puntaje == 0 else "naranja" if puntaje <= 3 else "rojo"


def levantamiento_distancia(brazos_alejados: bool, torso_inclinado: bool) -> SugerenciaNom:
    """Sugiere riesgo visual por distancia horizontal manos–espalda baja."""

    puntaje = 6 if brazos_alejados and torso_inclinado else 3 if brazos_alejados or torso_inclinado else 0
    return SugerenciaNom("levantamiento_distancia_horizontal", puntaje, _nivel(puntaje))


def region_vertical_manos(bajo_rodilla: bool, nivel_piso: bool, sobre_codo: bool, nivel_cabeza: bool) -> SugerenciaNom:
    """Sugiere riesgo visual por región vertical de las manos."""

    puntaje = 3 if nivel_piso or nivel_cabeza else 1 if bajo_rodilla or sobre_codo else 0
    return SugerenciaNom("levantamiento_region_vertical_manos", puntaje, _nivel(puntaje))


def torsion_lateral(torsion: bool, lateral: bool) -> SugerenciaNom:
    """Sugiere riesgo por torsión y/o flexión lateral."""

    puntaje = 2 if torsion and lateral else 1 if torsion or lateral else 0
    return SugerenciaNom("torsion_flexion_lateral", puntaje, _nivel(puntaje))


def transporte_asimetrico(mano_lado: bool, sobre_hombro: bool, asimetrico_frontal: bool) -> SugerenciaNom:
    """Sugiere riesgo por asimetría en el transporte."""

    puntaje = 3 if sobre_hombro else 2 if mano_lado else 1 if asimetrico_frontal else 0
    return SugerenciaNom("transporte_carga_asimetrica", puntaje, _nivel(puntaje))


def empuje_arrastre(severo: bool, inclinado_o_torcido: bool) -> SugerenciaNom:
    """Sugiere riesgo postural durante empuje o arrastre."""

    puntaje = 6 if severo else 3 if inclinado_o_torcido else 0
    return SugerenciaNom("empuje_arrastre_postura", puntaje, _nivel(puntaje))
