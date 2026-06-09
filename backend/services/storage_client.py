"""
storage_client.py -- Cliente de Cloud Storage para Quimera
===========================================================
Sube los archivos generados (React, CSS, Markdown) a un bucket de GCS.

Autenticacion: Application Default Credentials (ADC).
  - Local: gcloud auth application-default login
  - Cloud Run: Service Account del contenedor

Bucket: quimera-ai-prod-outputs
Estructura:
  projects/{projectId}/index.html       -- sitio HTML generado (Step 3)
  projects/{projectId}/design.md        -- DESIGN.md generado (Step 1)

PREREQUISITO (una vez por proyecto GCP):
  gsutil mb -p quimera-ai-prod -l us-central1 gs://quimera-ai-prod-outputs

NOTA: el SDK de google-cloud-storage es sincrono.
Todas las llamadas se envuelven en asyncio.to_thread() para no bloquear FastAPI.
"""

import asyncio
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "quimera-ai-prod")
BUCKET_NAME = os.getenv("GCS_BUCKET", "quimera-ai-prod-outputs")


class StorageClient:
    """
    Cliente para subir archivos generados a Cloud Storage.
    El SDK de GCS es sincrono: usa asyncio.to_thread() para no bloquear el event loop.
    """

    def __init__(self, project_id: Optional[str] = None) -> None:
        project = project_id or GCP_PROJECT
        try:
            from google.cloud import storage
            self._client = storage.Client(project=project)
            self._bucket = self._client.bucket(BUCKET_NAME)
            logger.info("StorageClient OK. Bucket: gs://%s", BUCKET_NAME)
        except Exception as e:
            logger.error("StorageClient: no se pudo inicializar: %s", e)
            self._client = None
            self._bucket = None

    def _upload_blob_sync(self, blob_path: str, content: str, content_type: str) -> str:
        """
        Sube un blob a GCS (sincrono, se llama desde asyncio.to_thread).

        Returns:
            URL publica gs:// del archivo subido.
        """
        if self._bucket is None:
            raise RuntimeError("StorageClient no inicializado correctamente.")
        blob = self._bucket.blob(blob_path)
        blob.upload_from_string(content.encode("utf-8"), content_type=content_type)
        return f"gs://{BUCKET_NAME}/{blob_path}"

    async def upload_component(self, project_id: str, content: str) -> str:
        """
        Sube el componente React TypeScript.

        Returns:
            URL gs:// del componente.
        """
        if not content:
            return f"gs://{BUCKET_NAME}/projects/{project_id}/componente.tsx"
        try:
            path = f"projects/{project_id}/componente.tsx"
            url = await asyncio.to_thread(
                self._upload_blob_sync, path, content, "text/plain; charset=utf-8"
            )
            logger.info("Storage: componente subido a %s", url)
            return url
        except Exception as e:
            logger.error("Storage.upload_component: %s", e)
            return f"gs://{BUCKET_NAME}/projects/{project_id}/componente.tsx"

    async def upload_tokens(self, project_id: str, content: str) -> str:
        """
        Sube los design tokens CSS.

        Returns:
            URL gs:// de los tokens.
        """
        if not content:
            return f"gs://{BUCKET_NAME}/projects/{project_id}/tokens.css"
        try:
            path = f"projects/{project_id}/tokens.css"
            url = await asyncio.to_thread(
                self._upload_blob_sync, path, content, "text/css; charset=utf-8"
            )
            logger.info("Storage: tokens subidos a %s", url)
            return url
        except Exception as e:
            logger.error("Storage.upload_tokens: %s", e)
            return f"gs://{BUCKET_NAME}/projects/{project_id}/tokens.css"

    async def upload_rationale(self, project_id: str, content: str) -> str:
        """
        Sube el documento de rationale en Markdown.

        Returns:
            URL gs:// del rationale.
        """
        if not content:
            return f"gs://{BUCKET_NAME}/projects/{project_id}/rationale.md"
        try:
            path = f"projects/{project_id}/rationale.md"
            url = await asyncio.to_thread(
                self._upload_blob_sync, path, content, "text/markdown; charset=utf-8"
            )
            logger.info("Storage: rationale subido a %s", url)
            return url
        except Exception as e:
            logger.error("Storage.upload_rationale: %s", e)
            return f"gs://{BUCKET_NAME}/projects/{project_id}/rationale.md"
