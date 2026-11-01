import json
from pathlib import Path

from PIL import Image

from ergoai.cli import ejecutar_evaluar
from ergoai.modelos import Landmark, PoseResult


def _landmarks_sinteticos() -> list[Landmark]:
    """Cuerpo completo artificial para probar el pipeline sin MediaPipe."""

    coordenadas = {indice: (20.0 + indice * 3, 30.0 + indice * 4) for indice in range(33)}
    coordenadas.update({
        0: (100, 55), 7: (96, 70), 8: (104, 70),
        11: (100, 100), 12: (110, 100), 13: (130, 152), 14: (140, 152),
        15: (150, 206), 16: (160, 206), 17: (145, 216), 18: (155, 216),
        19: (155, 216), 20: (165, 216), 23: (50, 186.6), 24: (60, 186.6),
        25: (55, 250), 26: (65, 250), 27: (60, 310), 28: (70, 310),
        29: (40, 310), 30: (50, 310), 31: (60, 310), 32: (70, 310),
    })
    return [Landmark(indice, str(indice), *coordenadas[indice], 0.0, 0.95, 0.95) for indice in range(33)]


def test_pipeline_sintetico_sin_mediapipe_produce_reba_esperado(tmp_path: Path) -> None:
    raiz = tmp_path / "proyecto"
    (raiz / "config").mkdir(parents=True)
    (raiz / "config" / "umbrales.yaml").write_text(
        (Path(__file__).resolve().parents[1] / "config" / "umbrales.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    caso = tmp_path / "caso"
    caso.mkdir()
    for vista in ("frente", "costado", "aerea"):
        Image.new("RGB", (300, 400)).save(caso / f"{vista}.png")
    overrides = {"tronco_flexion": 30, "cuello_flexion": 25, "tronco_torsion": 0, "tronco_inclinacion_lateral": 0, "cuello_inclinacion_rotacion": 0, "apoyo_piernas_unilateral": 1}
    for lado in ("L", "R"):
        overrides.update({f"rodilla_flexion_{lado}": 0, f"brazo_flexion_{lado}": 60, f"codo_flexion_{lado}": 50, f"muneca_flexion_extension_{lado}": 20, f"brazo_abduccion_{lado}": 0})
    contexto = {
        "caso_id": "sintetico", "orientacion_costado": "derecha", "postura": "de_pie",
        "carga_kg": 8, "agarre": "regular", "actividad": {"estatica_mas_1min": True},
        "hombro_elevado": {"izquierdo": False, "derecho": False},
        "brazo_apoyado": {"izquierdo": False, "derecho": False},
        "muneca_desviada_o_torcida": {"izquierdo": False, "derecho": False}, "overrides": overrides,
    }
    (caso / "contexto.json").write_text(json.dumps(contexto), encoding="utf-8")

    class BackendSintetico:
        def detect(self, image):
            return [PoseResult(_landmarks_sinteticos(), [])]

    salida = ejecutar_evaluar(caso, raiz, BackendSintetico())
    resultado = json.loads(salida.read_text(encoding="utf-8"))
    assert resultado["reba"]["final"]["reportado"] == 9, resultado["reba"]
    assert resultado["reba"]["nivel_riesgo"] == "Alto"
    assert resultado["reba"]["nivel_accion"] == 3
