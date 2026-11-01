"""Operaciones geométricas puras para coordenadas de imagen y mundo."""

from __future__ import annotations

from math import acos, atan2, cos, degrees, hypot, radians, sin
from typing import Sequence, TypeAlias

Vector2: TypeAlias = tuple[float, float]
Vector3: TypeAlias = tuple[float, float, float]


def restar(a: Vector2, b: Vector2) -> Vector2:
    """Calcula el vector que va de `b` a `a`."""

    return a[0] - b[0], a[1] - b[1]


def punto_medio(*puntos: Vector2) -> Vector2 | None:
    """Devuelve el punto medio; sin puntos no inventa una coordenada."""

    if not puntos:
        return None
    return (
        sum(punto[0] for punto in puntos) / len(puntos),
        sum(punto[1] for punto in puntos) / len(puntos),
    )


def norma(vector: Sequence[float]) -> float:
    """Calcula la longitud euclidiana de un vector de dimensión arbitraria."""

    return hypot(*vector)


def unitario(vector: Vector2) -> Vector2 | None:
    """Normaliza un vector 2D o devuelve `None` si no tiene dirección."""

    longitud = norma(vector)
    if longitud == 0:
        return None
    return vector[0] / longitud, vector[1] / longitud


def angulo_entre(u: Sequence[float], v: Sequence[float]) -> float | None:
    """Ángulo menor entre dos vectores, en el intervalo inclusivo [0, 180]."""

    longitud = norma(u) * norma(v)
    if longitud == 0:
        return None
    coseno = sum(a * b for a, b in zip(u, v, strict=True)) / longitud
    return degrees(acos(max(-1.0, min(1.0, coseno))))


def normalizar_angulo(angulo: float) -> float:
    """Normaliza un ángulo al intervalo (-180, 180]."""

    resultado = (angulo + 180.0) % 360.0 - 180.0
    return 180.0 if resultado == -180.0 else resultado


def theta_arriba(vector: Vector2, sentido: int) -> float | None:
    """Ángulo firmado respecto a la vertical hacia arriba de la imagen."""

    if norma(vector) == 0 or sentido not in (-1, 1):
        return None
    return degrees(atan2(sentido * vector[0], -vector[1]))


def theta_abajo(vector: Vector2, sentido: int) -> float | None:
    """Ángulo firmado respecto a la vertical hacia abajo de la imagen."""

    if norma(vector) == 0 or sentido not in (-1, 1):
        return None
    return degrees(atan2(sentido * vector[0], vector[1]))


def rotar(punto: Vector2, centro: Vector2, grados: float) -> Vector2:
    """Rota un punto alrededor de `centro` en el sistema de píxeles."""

    angulo = radians(grados)
    x, y = punto[0] - centro[0], punto[1] - centro[1]
    return (
        centro[0] + x * cos(angulo) - y * sin(angulo),
        centro[1] + x * sin(angulo) + y * cos(angulo),
    )


def rotacion_para_vertical(referencia: tuple[Vector2, Vector2]) -> float:
    """Devuelve los grados necesarios para alinear una recta con la vertical."""

    (x1, y1), (x2, y2) = referencia
    return -degrees(atan2(y2 - y1, x2 - x1)) - 90.0
