from ergoai.precision import comparar_angulos, resumir_precision


def test_metricas_de_precision_y_bandas() -> None:
    automaticos = [
        {"medida": "tronco_flexion", "lado": None, "valor_deg": 30, "banda_reba": 3, "vista": "costado", "banderas": []},
        {"medida": "codo_flexion", "lado": "R", "valor_deg": 75, "banda_reba": 1, "vista": "costado", "banderas": ["baja_visibilidad"]},
    ]
    referencias = [
        {"medida": "tronco_flexion", "lado": None, "valor_deg": 25, "banda_reba": 3},
        {"medida": "codo_flexion", "lado": "R", "valor_deg": 65, "banda_reba": 2},
    ]
    filas = comparar_angulos("caso01", automaticos, referencias)
    resumen = resumir_precision(filas, [
        ({"reba": {"final": {"reportado": 9}, "nivel_riesgo": "Alto"}}, {"reba": {"final": {"reportado": 9}, "nivel_riesgo": "Alto"}})
    ])
    assert [fila.error_absoluto_deg for fila in filas] == [5, 10]
    assert resumen["porcentaje_misma_banda_reba"] == 50
    assert resumen["porcentaje_mismo_reba_y_nivel"] == 100
    assert resumen["error_por_segmento"]["codo_flexion"]["maximo"] == 10
