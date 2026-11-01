"""Carga local y segura de fotografías."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


@dataclass(frozen=True)
class ImagenRGB:
    """Imagen corregida por EXIF lista para MediaPipe y OpenCV."""

    pixeles: np.ndarray
    ancho: int
    alto: int


def cargar_imagen(ruta: str | Path) -> ImagenRGB:
    """Corrige EXIF, convierte a RGB y devuelve píxeles uint8."""

    with Image.open(ruta) as original:
        rgb = ImageOps.exif_transpose(original).convert("RGB")
        pixeles = np.asarray(rgb, dtype=np.uint8).copy()
    alto, ancho = pixeles.shape[:2]
    return ImagenRGB(pixeles=pixeles, ancho=ancho, alto=alto)
