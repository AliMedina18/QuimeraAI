"""
conftest.py — Configuración global de pytest para Quimera
=========================================================

Contiene:
- Hook para convertir errores de red transitorios en SKIP
  en tests @pytest.mark.slow (que llaman a Gemini API).

Errores de red que se convierten en SKIP:
  - httpx.RemoteProtocolError  (servidor desconectó sin responder)
  - httpx.ConnectError         (no se pudo conectar)
  - httpx.TimeoutException     (timeout)
  - httpx.ReadTimeout          (timeout de lectura)

Esto evita que un corte momentáneo de red o una caída transitoria
de la API de Gemini marque el test como FAILED en lugar de SKIPPED.
"""

import pytest
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno desde backend/.env ANTES de cualquier import de módulos
_backend_env = Path(__file__).parent.parent / "backend" / ".env"
if _backend_env.exists():
    load_dotenv(_backend_env)


# Errores de red que indican problema de infraestructura, no de código
_NETWORK_EXCEPTIONS: tuple[type[Exception], ...] = ()

try:
    import httpx
    _NETWORK_EXCEPTIONS += (
        httpx.RemoteProtocolError,
        httpx.ConnectError,
        httpx.TimeoutException,
        httpx.ReadTimeout,
        httpx.ConnectTimeout,
        httpx.NetworkError,
    )
except ImportError:
    pass  # httpx no instalado — no se aplica el hook


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item):
    """
    Hook que intercepta la ejecución de cada test.

    Si el test tiene @pytest.mark.slow Y falla con un error de red,
    lo convierte en SKIP en lugar de FAILED.
    """
    outcome = yield

    if not _NETWORK_EXCEPTIONS:
        return  # httpx no disponible, nada que hacer

    if outcome.excinfo is None:
        return  # Test pasó, nada que hacer

    exc_type, exc_value, _ = outcome.excinfo

    # Solo actuar en tests @pytest.mark.slow
    if not item.get_closest_marker("slow"):
        return

    # Si es un error de red, convertir en skip
    if issubclass(exc_type, _NETWORK_EXCEPTIONS):
        pytest.skip(
            f"Error de red transitorio en llamada a Gemini API — "
            f"{exc_type.__name__}: {exc_value}"
        )
