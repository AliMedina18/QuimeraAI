"""
firestore_client.py -- Cliente de Firestore para Quimera
=========================================================
Guarda y recupera resultados del pipeline en Cloud Firestore.

Autenticacion: Application Default Credentials (ADC).
  - Local: gcloud auth application-default login
  - Cloud Run: Service Account del contenedor

Estructura en Firestore:
  /projects/{projectId}/
    design_brief:     str
    overall_score:    float
    approved:         bool
    iterations:       int
    component_url:    str  (gs:// Cloud Storage)
    tokens_url:       str
    rationale_url:    str
    aesthetic_scores: dict
    created_at:       timestamp

PREREQUISITO (una vez por proyecto GCP):
  gcloud firestore databases create --region=us-central1 --project=quimera-ai-prod
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "quimera-ai-prod")


class FirestoreClient:
    """
    Cliente async para Cloud Firestore.
    Usa google.cloud.firestore.AsyncClient para no bloquear el event loop de FastAPI.
    """

    def __init__(self, project_id: Optional[str] = None) -> None:
        project = project_id or GCP_PROJECT
        try:
            from google.cloud import firestore
            self._db = firestore.AsyncClient(project=project)
            logger.info("FirestoreClient OK. Proyecto: %s", project)
        except Exception as e:
            logger.error("FirestoreClient: no se pudo inicializar: %s", e)
            self._db = None

    async def save_generated_output(self, project_id: str, output: dict) -> None:
        """
        Guarda el output completo de una ejecucion del pipeline.

        Args:
            project_id: ID unico del proyecto (uuid4 generado por el endpoint).
            output: dict con todos los campos del resultado.
        """
        if self._db is None:
            logger.warning("Firestore no disponible. Omitiendo guardado.")
            return
        try:
            # Agregar timestamp del servidor
            output["created_at"] = datetime.now(timezone.utc).isoformat()
            doc_ref = self._db.collection("projects").document(project_id)
            await doc_ref.set(output, merge=True)
            logger.info("Firestore: proyecto %s guardado.", project_id)
        except Exception as e:
            logger.error("Firestore.save_generated_output: %s", e)
            raise

    async def save_aesthetic_scores(self, project_id: str, scores: dict) -> None:
        """
        Guarda los scores de una iteracion de evaluacion.

        Args:
            project_id: ID del proyecto.
            scores: dict con los 8 scores + overall_score.
        """
        if self._db is None:
            logger.warning("Firestore no disponible. Omitiendo guardado.")
            return
        try:
            scores["evaluated_at"] = datetime.now(timezone.utc).isoformat()
            doc_ref = self._db.collection("aesthetic_scores").document(project_id)
            await doc_ref.set(scores, merge=True)
            logger.info("Firestore: scores de %s guardados.", project_id)
        except Exception as e:
            logger.error("Firestore.save_aesthetic_scores: %s", e)
            raise

    async def get_project(self, project_id: str) -> Optional[dict]:
        """
        Recupera un proyecto por su ID.

        Returns:
            dict con los datos del proyecto, o None si no existe.
        """
        if self._db is None:
            return None
        try:
            doc_ref = self._db.collection("projects").document(project_id)
            doc = await doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error("Firestore.get_project: %s", e)
            return None
