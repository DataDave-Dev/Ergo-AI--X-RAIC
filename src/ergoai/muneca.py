"""Medición experimental de muñeca con HandLandmarker, aislada de REBA."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .geometria import Vector2, angulo_entre, punto_medio, restar


@dataclass(frozen=True)
class MedicionMunecaMano:
    """Resultado experimental; requiere validación de Fase 4 antes de adoptarse."""

    valor_deg: float | None
    confianza: float | None
    metodo: str = "HandLandmarker: eje metacarpianos"
    advertencia: str = "experimental: comparar contra referencia manual antes de adoptar"


def medir_muneca_con_mano(antebrazo: Vector2, landmarks_mano: list[Vector2], confianza: float | None = None) -> MedicionMunecaMano:
    """Mide el ángulo entre antebrazo y eje de metacarpianos de una mano detectada."""

    # HandLandmarker: 0 muñeca; 5 MCP índice; 17 MCP meñique.
    if len(landmarks_mano) <= 17:
        return MedicionMunecaMano(None, confianza)
    muneca, eje = landmarks_mano[0], punto_medio(landmarks_mano[5], landmarks_mano[17])
    if eje is None:
        return MedicionMunecaMano(None, confianza)
    valor = angulo_entre(antebrazo, restar(eje, muneca))
    return MedicionMunecaMano(valor, confianza)


class HandLandmarkerBackend:
    """Detector local de manos MediaPipe Tasks para recortes RGB de muñeca."""

    def __init__(self, modelo: str | Path) -> None:
        self.modelo = Path(modelo)

    def detectar(self, recorte_rgb: np.ndarray) -> list[list[Vector2]]:
        """Detecta manos en un recorte; no transmite imágenes fuera del equipo."""

        if not self.modelo.is_file():
            raise FileNotFoundError(f"No existe el modelo de manos: {self.modelo}")
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision
        except ImportError as exc:
            raise RuntimeError("MediaPipe no está instalado.") from exc
        opciones = vision.HandLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(self.modelo)),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=2,
        )
        alto, ancho = recorte_rgb.shape[:2]
        with vision.HandLandmarker.create_from_options(opciones) as detector:
            resultado = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=recorte_rgb))
        return [[(punto.x * ancho, punto.y * alto) for punto in mano] for mano in resultado.hand_landmarks]
