from pathlib import Path

import pytest

from ergoai.config import cargar_configuracion


def test_carga_configuracion_del_proyecto() -> None:
    raiz = Path(__file__).resolve().parents[1]
    configuracion = cargar_configuracion(raiz / "config" / "umbrales.yaml")
    assert configuracion.pose.vis_min == 0.5
    assert configuracion.reba.lado_reportado == "peor"


def test_configuracion_informa_clave_obligatoria_faltante(tmp_path: Path) -> None:
    ruta = tmp_path / "mal.yaml"
    ruta.write_text("pose: {}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Configuración inválida"):
        cargar_configuracion(ruta)
