from pathlib import Path

import pytest

from ergoai.config import Configuracion, cargar_configuracion


@pytest.fixture
def configuracion() -> Configuracion:
    return cargar_configuracion(Path(__file__).resolve().parents[1] / "config" / "umbrales.yaml")
