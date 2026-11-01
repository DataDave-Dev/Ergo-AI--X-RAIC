"""Índices de BlazePose y nombres comprensibles en español."""

NOMBRES_LANDMARKS: dict[int, str] = {
    0: "nariz", 1: "ojo_interno_izquierdo", 2: "ojo_izquierdo",
    3: "ojo_externo_izquierdo", 4: "ojo_interno_derecho", 5: "ojo_derecho",
    6: "ojo_externo_derecho", 7: "oreja_izquierda", 8: "oreja_derecha",
    9: "boca_izquierda", 10: "boca_derecha", 11: "hombro_izquierdo",
    12: "hombro_derecho", 13: "codo_izquierdo", 14: "codo_derecho",
    15: "muneca_izquierda", 16: "muneca_derecha", 17: "menique_izquierdo",
    18: "menique_derecho", 19: "indice_izquierdo", 20: "indice_derecho",
    21: "pulgar_izquierdo", 22: "pulgar_derecho", 23: "cadera_izquierda",
    24: "cadera_derecha", 25: "rodilla_izquierda", 26: "rodilla_derecha",
    27: "tobillo_izquierdo", 28: "tobillo_derecho", 29: "talon_izquierdo",
    30: "talon_derecho", 31: "punta_pie_izquierdo", 32: "punta_pie_derecho",
}

INDICES_CARA = frozenset(range(0, 11))

# Conexiones del esqueleto que no revelan ni dibujan puntos faciales.
CONEXIONES_CUERPO = (
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (11, 23),
    (12, 24), (23, 24), (23, 25), (25, 27), (27, 29),
    (29, 31), (24, 26), (26, 28), (28, 30), (30, 32),
)
