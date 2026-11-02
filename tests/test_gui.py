from pathlib import Path

import pytest

pytest.importorskip("tkinter")

from ergoai import gui  # noqa: E402


class _Boton:
    def __init__(self) -> None:
        self.estado = "disabled"

    def configure(self, state: str) -> None:
        self.estado = state


class _Ventana:
    """Encola callbacks como Tk: se ejecutan después de salir del `except`."""

    def __init__(self) -> None:
        self.pendientes: list = []

    def after(self, _retardo: int, funcion) -> None:
        self.pendientes.append(funcion)


class _Variable:
    def __init__(self) -> None:
        self.valor = ""

    def set(self, valor: str) -> None:
        self.valor = valor


def test_error_en_segundo_plano_se_muestra_y_rehabilita_boton(monkeypatch, tmp_path: Path) -> None:
    app = object.__new__(gui.AplicacionErgoAI)
    app.raiz, app.ventana, app.boton_evaluar, app.estado = tmp_path, _Ventana(), _Boton(), _Variable()
    errores: list[tuple[str, str]] = []

    def fallar(caso, raiz):
        raise FileNotFoundError("Ejecuta scripts/descargar_modelo.py")

    monkeypatch.setattr(gui, "ejecutar_evaluar", fallar)
    monkeypatch.setattr(gui.messagebox, "showerror", lambda titulo, mensaje: errores.append((titulo, mensaje)))

    app._evaluar_en_segundo_plano(tmp_path)
    for funcion in app.ventana.pendientes:
        funcion()

    assert errores == [("Error durante el análisis", "Ejecuta scripts/descargar_modelo.py")]
    assert app.boton_evaluar.estado == "normal"
    assert app.estado.valor == "La evaluación no pudo completarse."
