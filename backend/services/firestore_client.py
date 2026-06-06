"""
firestore_client.py -- Cliente de Firestore para Quimera
=========================================================
Operaciones de lectura/escritura del pipeline.

Se implementa en el Dia 4 cuando se conecta el pipeline end-to-end.

Estructura de datos en Firestore (ver Seccion 6.2 del plan maestro):
  /users/{userId}/projects/{projectId}/
    brand_context/
    design_specs/
    aesthetic_scores/{evaluationId}
    generated_outputs/{outputId}
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FirestoreClient:
    """Cliente para operaciones de Firestore."""

    def __init__(self, project_id: Optional[str] = None) -> None:
        # TODO Dia 4: inicializar google.cloud.firestore.AsyncClient
        # import google.cloud.firestore as firestore
        # self._db = firestore.AsyncClient(project=project_id)
        logger.warning("FirestoreClient: stub -- implementar en Dia 4")

    async def save_project(self, user_id: str, project_id: str, data: dict) -> None:
        """Guarda o actualiza un proyecto en Firestore. TODO Dia 4."""
        logger.warning("save_project: stub")

    async def save_aesthetic_scores(self, project_id: str, scores: dict) -> None:
        """Guarda los scores de una iteracion. TODO Dia 4."""
        logger.warning("save_aesthetic_scores: stub")

    async def save_generated_output(self, project_id: str, output: dict) -> None:
        """Guarda el output generado (React, tokens, rationale). TODO Dia 4."""
        logger.warning("save_generated_output: stub")
