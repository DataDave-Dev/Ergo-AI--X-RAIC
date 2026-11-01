"""Anota localmente landmarks de referencia con clics de OpenCV."""

import argparse
import json
from pathlib import Path

import cv2

from ergoai.landmarks import NOMBRES_LANDMARKS

ORDEN = (
    (11, "hombro izquierdo"), (13, "codo izquierdo"), (15, "muñeca izquierda"), (17, "meñique izquierdo"), (19, "índice izquierdo"),
    (23, "cadera izquierda"), (25, "rodilla izquierda"), (27, "tobillo izquierdo"), (29, "talón izquierdo"), (31, "punta pie izquierda"), (7, "oreja izquierda"),
    (12, "hombro derecho"), (14, "codo derecho"), (16, "muñeca derecha"), (18, "meñique derecho"), (20, "índice derecho"),
    (24, "cadera derecha"), (26, "rodilla derecha"), (28, "tobillo derecho"), (30, "talón derecho"), (32, "punta pie derecho"), (8, "oreja derecha"), (0, "nariz"),
)


def anotar(imagen: Path) -> list[dict[str, float | int | str]]:
    """Solicita landmarks en orden fijo; Enter termina y R deshace el último."""

    original = cv2.imread(str(imagen))
    if original is None:
        raise ValueError(f"No se pudo abrir {imagen}")
    puntos: list[tuple[int, int, int]] = []
    ventana = "ErgoAI anotación manual"

    def clic(evento: int, x: int, y: int, _flags: int, _parametro: object) -> None:
        if evento == cv2.EVENT_LBUTTONDOWN and len(puntos) < len(ORDEN):
            puntos.append((ORDEN[len(puntos)][0], x, y))

    cv2.namedWindow(ventana)
    cv2.setMouseCallback(ventana, clic)
    while True:
        lienzo = original.copy()
        for numero, (indice, x, y) in enumerate(puntos, 1):
            cv2.circle(lienzo, (x, y), 4, (0, 255, 0), -1)
            cv2.putText(lienzo, str(numero), (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
        siguiente = ORDEN[len(puntos)][1] if len(puntos) < len(ORDEN) else "completo"
        cv2.putText(lienzo, f"Siguiente: {siguiente}. Click; R deshace; Enter guarda.", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 3)
        cv2.putText(lienzo, f"Siguiente: {siguiente}. Click; R deshace; Enter guarda.", (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)
        cv2.imshow(ventana, lienzo)
        tecla = cv2.waitKey(20) & 0xFF
        if tecla in (13, 10):
            break
        if tecla in (ord("r"), ord("R")) and puntos:
            puntos.pop()
        if tecla == 27:
            cv2.destroyAllWindows()
            raise KeyboardInterrupt("Anotación cancelada")
    cv2.destroyAllWindows()
    return [{"indice": indice, "nombre": NOMBRES_LANDMARKS[indice], "x_px": x, "y_px": y, "z": 0.0, "visibility": 1.0, "presence": 1.0} for indice, x, y in puntos]


def main() -> None:
    parser = argparse.ArgumentParser(description="Anotación manual local de landmarks ErgoAI")
    parser.add_argument("imagen", type=Path)
    parser.add_argument("--vista", required=True, choices=("frente", "costado", "aerea"))
    parser.add_argument("--salida", type=Path, default=None)
    args = parser.parse_args()
    salida = args.salida or args.imagen.parent / "referencia.json"
    datos = json.loads(salida.read_text(encoding="utf-8")) if salida.exists() else {"caso_id": args.imagen.parent.name, "vistas": {}}
    datos.setdefault("vistas", {})[args.vista] = {"nombre": args.vista, "ancho": None, "alto": None, "detectado": True, "personas_detectadas": 1, "landmarks": anotar(args.imagen), "world_landmarks": []}
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Referencia guardada en {salida}")


if __name__ == "__main__":
    main()
