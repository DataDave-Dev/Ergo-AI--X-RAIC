"""Genera CSV y resumen de precisión para casos de validación locales."""

import argparse
import csv
import json
from pathlib import Path

from ergoai.config import cargar_configuracion
from ergoai.precision import angulos_desde_landmarks_referencia, comparar_angulos, resumir_precision


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara resultados ErgoAI contra referencia manual")
    parser.add_argument("--validacion", type=Path, default=Path("data/validacion"))
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--csv", type=Path, default=Path("out/precision.csv"))
    args = parser.parse_args()
    raiz = Path(__file__).resolve().parents[1]
    configuracion = cargar_configuracion(raiz / "config" / "umbrales.yaml")
    filas, casos = [], []
    for referencia_ruta in sorted(args.validacion.glob("*/referencia.json")):
        caso_id = referencia_ruta.parent.name
        resultado_ruta = args.out / caso_id / "resultado.json"
        if not resultado_ruta.exists():
            print(f"{caso_id}: falta {resultado_ruta}; se omite.")
            continue
        referencia, automatico = json.loads(referencia_ruta.read_text(encoding="utf-8")), json.loads(resultado_ruta.read_text(encoding="utf-8"))
        if "angulos" not in referencia:
            contexto_ruta = referencia_ruta.parent / "contexto.json"
            contexto = json.loads(contexto_ruta.read_text(encoding="utf-8")) if contexto_ruta.exists() else {"caso_id": caso_id}
            referencia = angulos_desde_landmarks_referencia(referencia, contexto, configuracion)
        filas.extend(comparar_angulos(caso_id, automatico.get("angulos", []), referencia["angulos"]))
        casos.append((automatico, referencia))
    resumen = resumir_precision(filas, casos)
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(("caso_id", "medida", "lado", "error_absoluto_deg", "misma_banda_reba", "vista", "banderas"))
        for fila in resumen["fallos"]:
            escritor.writerow((fila.caso_id, fila.medida, fila.lado, fila.error_absoluto_deg, fila.misma_banda_reba, fila.vista, fila.banderas))
    print(json.dumps({clave: valor for clave, valor in resumen.items() if clave != "fallos"}, ensure_ascii=False, indent=2))
    print(f"CSV: {args.csv}")


if __name__ == "__main__":
    main()
