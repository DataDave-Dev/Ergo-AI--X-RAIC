"""Descarga localmente el modelo pesado de MediaPipe requerido por ErgoAI."""

from pathlib import Path
from urllib.request import urlretrieve

URL_MODELO = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"
)


def main() -> None:
    """Descarga el modelo a models/ sin enviar ninguna imagen."""

    raiz = Path(__file__).resolve().parents[1]
    destino = raiz / "models" / "pose_landmarker_heavy.task"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0:
        print(f"El modelo ya existe: {destino}")
        return
    print(f"Descargando modelo a {destino}...")
    urlretrieve(URL_MODELO, destino)
    print("Modelo descargado correctamente.")


if __name__ == "__main__":
    main()
