from math import cos, radians, sin

import pytest

from ergoai.geometria import angulo_entre, normalizar_angulo, theta_abajo, theta_arriba


@pytest.mark.parametrize(
    ("sentido", "vector", "esperado"),
    [
        (1, (sin(radians(30)), -cos(radians(30))), 30.0),
        (-1, (-sin(radians(30)), -cos(radians(30))), 30.0),
        (1, (-sin(radians(30)), -cos(radians(30))), -30.0),
    ],
)
def test_signo_de_tronco_es_independiente_del_lado(sentido: int, vector: tuple[float, float], esperado: float) -> None:
    assert theta_arriba(vector, sentido) == pytest.approx(esperado)


def test_brazo_colgando_horizontal_y_atras() -> None:
    tronco = (0.0, -1.0)
    referencia = theta_abajo((-tronco[0], -tronco[1]), 1)
    assert theta_abajo((0.0, 1.0), 1) - referencia == pytest.approx(0.0)
    assert theta_abajo((1.0, 0.0), 1) - referencia == pytest.approx(90.0)
    atras = (-sin(radians(30)), cos(radians(30)))
    assert theta_abajo(atras, 1) - referencia == pytest.approx(-30.0)


def test_angulos_y_normalizacion() -> None:
    assert angulo_entre((1, 0), (0, 1)) == pytest.approx(90.0)
    assert angulo_entre((0, 0), (0, 1)) is None
    assert normalizar_angulo(190) == pytest.approx(-170)


def test_los_pixeles_preservan_la_geometria_de_una_imagen_ancha() -> None:
    """La misma recta en normalizados se distorsiona si no se lleva a píxeles."""

    ancho, alto = 1920, 1080
    vector_px = (300.0, -300.0)
    vector_normalizado = (vector_px[0] / ancho, vector_px[1] / alto)
    assert theta_arriba(vector_px, 1) == pytest.approx(45.0)
    assert theta_arriba(vector_normalizado, 1) != pytest.approx(45.0)
