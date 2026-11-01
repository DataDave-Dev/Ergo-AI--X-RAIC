"""Modelos de datos de entrada y salida de las fases 0 y 1."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Landmark:
    """Landmark en píxeles y su profundidad/confianza original."""

    indice: int
    nombre: str
    x_px: float
    y_px: float
    z: float
    visibility: float
    presence: float


@dataclass(frozen=True)
class WorldLandmark:
    """Landmark 3D de MediaPipe, expresado en metros."""

    indice: int
    nombre: str
    x: float
    y: float
    z: float
    visibility: float
    presence: float


@dataclass(frozen=True)
class PoseResult:
    """Una persona detectada por cualquier backend intercambiable."""

    landmarks: list[Landmark]
    world_landmarks: list[WorldLandmark]


@dataclass
class VistaPose:
    """Resultado final de una vista de una estación de trabajo."""

    nombre: str
    ancho: int
    alto: int
    detectado: bool
    personas_detectadas: int
    motivo: str | None = None
    persona_indice: int | None = None
    landmarks: list[Landmark] = field(default_factory=list)
    world_landmarks: list[WorldLandmark] = field(default_factory=list)

    def a_diccionario(self, vis_min: float) -> dict[str, Any]:
        """Convierte la vista a un diccionario JSON sin perder la trazabilidad."""

        salida = asdict(self)
        salida["landmarks"] = [
            {**asdict(punto), "utilizable": punto.visibility >= vis_min}
            for punto in self.landmarks
        ]
        return salida
