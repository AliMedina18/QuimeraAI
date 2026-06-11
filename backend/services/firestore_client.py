"""
firestore_client.py -- Cliente de Firestore para Quimera
=========================================================
Guarda y recupera resultados del pipeline y la biblioteca de diseños.

Autenticacion: Application Default Credentials (ADC).
  - Local: gcloud auth application-default login
  - Cloud Run: Service Account del contenedor

Estructura en Firestore:
  /projects/{projectId}/          <- pipeline outputs (legacy)
  /designs/{designId}/            <- biblioteca de diseños guardados
    session_id:      str
    name:            str
    html_output:     str
    design_markdown: str
    created_at:      str (ISO 8601)
    updated_at:      str (ISO 8601)

PREREQUISITO (una vez por proyecto GCP):
  gcloud firestore databases create --region=us-central1 --project=quimera-ai-prod
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "quimera-ai-prod")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FirestoreClient:
    """
    Cliente async para Cloud Firestore.
    Usa google.cloud.firestore.AsyncClient para no bloquear el event loop de FastAPI.
    Si Firestore no esta disponible, los metodos fallan silenciosamente (log warning).
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

    # ------------------------------------------------------------------ #
    #  Pipeline outputs (legacy)                                          #
    # ------------------------------------------------------------------ #

    async def save_generated_output(self, project_id: str, output: dict) -> None:
        """Guarda el output completo de una ejecucion del pipeline."""
        if self._db is None:
            logger.warning("Firestore no disponible. Omitiendo guardado.")
            return
        try:
            output["created_at"] = _now_iso()
            doc_ref = self._db.collection("projects").document(project_id)
            await doc_ref.set(output, merge=True)
            logger.info("Firestore: proyecto %s guardado.", project_id)
        except Exception as e:
            logger.error("Firestore.save_generated_output: %s", e)
            raise

    # ------------------------------------------------------------------ #
    #  Biblioteca de diseños                                              #
    # ------------------------------------------------------------------ #

    async def save_design(
        self,
        session_id: str,
        name: str,
        html_gcs_path: str = "",
        markdown_gcs_path: str = "",
        design_id: Optional[str] = None,
        # Fallback: si no hay GCS, guardar inline (solo para compatibilidad)
        html_output: str = "",
        design_markdown: str = "",
    ) -> str:
        """
        Guarda un diseño en la coleccion /designs/.
        Preferencia: rutas GCS (html_gcs_path, markdown_gcs_path).
        Fallback: html_output / design_markdown inline (documentos viejos).
        Retorna el design_id (nuevo o el recibido si es actualizacion).
        """
        if self._db is None:
            logger.warning("Firestore no disponible. Usando ID generado sin persistir.")
            return design_id or str(uuid.uuid4())

        did = design_id or str(uuid.uuid4())
        now = _now_iso()
        data: dict = {
            "session_id":          session_id,
            "name":                name,
            "html_gcs_path":       html_gcs_path,
            "markdown_gcs_path":   markdown_gcs_path,
            "updated_at":          now,
        }
        # Guardar inline solo si no tenemos rutas GCS (fallback)
        if not html_gcs_path and html_output:
            data["html_output"] = html_output
        if not markdown_gcs_path and design_markdown:
            data["design_markdown"] = design_markdown

        # Solo setear created_at al crear, no al actualizar
        if design_id is None:
            data["created_at"] = now

        try:
            doc_ref = self._db.collection("designs").document(did)
            await doc_ref.set(data, merge=True)
            logger.info(
                "Firestore: diseño %s guardado (session=%s, gcs=%s).",
                did, session_id, bool(html_gcs_path),
            )
            return did
        except Exception as e:
            logger.error("Firestore.save_design: %s", e)
            raise

    async def list_designs(self, session_id: str) -> list[dict]:
        """
        Lista los diseños de una session ordenados por created_at desc.
        No incluye html_output para reducir trafico.
        Nota: el orden se hace en Python para evitar requerir índice compuesto en Firestore.
        """
        if self._db is None:
            logger.warning("Firestore no disponible. Retornando lista vacía.")
            return []
        try:
            # Solo where, sin order_by → no requiere índice compuesto
            query = (
                self._db.collection("designs")
                .where("session_id", "==", session_id)
                .limit(50)
            )
            docs = query.stream()
            results = []
            async for doc in docs:
                d = doc.to_dict()
                results.append({
                    "id":           doc.id,
                    "name":         d.get("name", "Sin nombre"),
                    "created_at":   d.get("created_at", ""),
                    "updated_at":   d.get("updated_at", ""),
                    "has_markdown": bool(d.get("design_markdown")),
                })
            # Ordenar por created_at desc en Python (trivial para ≤50 docs)
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return results
        except Exception as e:
            logger.error("Firestore.list_designs: %s", e)
            raise

    async def get_design(self, design_id: str) -> Optional[dict]:
        """
        Obtiene los metadatos completos de un diseño.
        Incluye html_gcs_path y markdown_gcs_path para que el caller descargue de GCS.
        También retorna html_output inline si existe (docs viejos, sin GCS).
        """
        if self._db is None:
            return None
        try:
            doc_ref = self._db.collection("designs").document(design_id)
            doc = await doc_ref.get()
            if not doc.exists:
                return None
            d = doc.to_dict()
            d["id"] = doc.id
            return d
        except Exception as e:
            logger.error("Firestore.get_design: %s", e)
            raise

    async def delete_design(self, design_id: str) -> Optional[dict]:
        """
        Elimina un diseño de Firestore.
        Retorna el dict del diseño eliminado (para que el caller pueda limpiar GCS),
        o None si no existía.
        """
        if self._db is None:
            return None
        try:
            doc_ref = self._db.collection("designs").document(design_id)
            doc = await doc_ref.get()
            if not doc.exists:
                return None
            d = doc.to_dict()
            d["id"] = design_id
            await doc_ref.delete()
            logger.info("Firestore: diseño %s eliminado.", design_id)
            return d
        except Exception as e:
            logger.error("Firestore.delete_design: %s", e)
            raise
