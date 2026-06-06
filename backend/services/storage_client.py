"""
storage_client.py -- Cliente de Cloud Storage para Quimera
===========================================================
Sube los archivos generados a Cloud Storage.

Se implementa en el Dia 4.

Buckets (ver Seccion 6.3 del plan maestro):
  gs://quimera-outputs/projects/{projectId}/
    componente.tsx
    tokens.css
    rationale.md
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StorageClient:
    """Cliente para subir archivos generados a Cloud Storage."""

    def __init__(self, project_id: Optional[str] = None) -> None:
        # TODO Dia 4: inicializar google.cloud.storage.Client
        logger.warning("StorageClient: stub -- implementar en Dia 4")

    async def upload_component(self, project_id: str, content: str) -> str:
        """Sube el componente React y devuelve la URL. TODO Dia 4."""
        logger.warning("upload_component: stub")
        return f"gs://quimera-outputs/projects/{project_id}/componente.tsx"

    async def upload_tokens(self, project_id: str, content: str) -> str:
        """Sube los design tokens CSS. TODO Dia 4."""
        logger.warning("upload_tokens: stub")
        return f"gs://quimera-outputs/projects/{project_id}/tokens.css"

    async def upload_rationale(self, project_id: str, content: str) -> str:
        """Sube el documento de rationale. TODO Dia 4."""
        logger.warning("upload_rationale: stub")
        return f"gs://quimera-outputs/projects/{project_id}/rationale.md"
