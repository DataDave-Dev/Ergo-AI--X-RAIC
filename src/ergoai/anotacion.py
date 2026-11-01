"""Anotación OpenCV de detecciones de la Fase 1."""

from pathlib import Path

import cv2
import numpy as np

from .landmarks import CONEXIONES_CUERPO, INDICES_CARA
from .modelos import Landmark


def dibujar_esqueleto(image_rgb: np.ndarray, landmarks: list[Landmark], vis_min: float) -> np.ndarray:
    """Dibuja únicamente el cuerpo; los landmarks faciales nunca se representan."""

    imagen = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    puntos = {punto.indice: punto for punto in landmarks if punto.visibility >= vis_min}
    for inicio, fin in CONEXIONES_CUERPO:
        if inicio in puntos and fin in puntos:
            a, b = puntos[inicio], puntos[fin]
            cv2.line(imagen, (round(a.x_px), round(a.y_px)), (round(b.x_px), round(b.y_px)), (0, 220, 0), 2)
    for indice, punto in puntos.items():
        if indice not in INDICES_CARA:
            cv2.circle(imagen, (round(punto.x_px), round(punto.y_px)), 3, (255, 170, 0), -1)
    return imagen


def guardar_esqueleto(ruta: str | Path, image_rgb: np.ndarray, landmarks: list[Landmark], vis_min: float) -> None:
    """Guarda la anotación como PNG, creando sus carpetas si hacen falta."""

    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(destino), dibujar_esqueleto(image_rgb, landmarks, vis_min)):
        raise OSError(f"No se pudo guardar la imagen anotada: {destino}")


def guardar_angulos(
    ruta: str | Path, image_rgb: np.ndarray, landmarks: list[Landmark], vis_min: float,
    etiquetas: list[str],
) -> None:
    """Guarda el esqueleto y las medidas de una vista sin dibujar la cara."""

    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    imagen = dibujar_esqueleto(image_rgb, landmarks, vis_min)
    for renglon, etiqueta in enumerate(etiquetas):
        cv2.putText(imagen, etiqueta, (12, 28 + 24 * renglon), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 3, cv2.LINE_AA)
        cv2.putText(imagen, etiqueta, (12, 28 + 24 * renglon), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    if not cv2.imwrite(str(destino), imagen):
        raise OSError(f"No se pudo guardar la imagen anotada: {destino}")
