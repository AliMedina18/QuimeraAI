"""
storage_client.py -- Cliente de Cloud Storage para Quimera
===========================================================
Sube y descarga los archivos de diseño (HTML, Markdown) al bucket de GCS.

Autenticacion: Application Default Credentials (ADC).
  - Local: gcloud auth application-default login
  - Cloud Run: Service Account del contenedor

Bucket: quimera-ai-prod-outputs
Estructura de rutas:
  designs/{designId}/index.html    -- HTML generado
  designs/{designId}/design.md     -- DESIGN.md generado

PREREQUISITO (ya creado):
  gs://quimera-ai-prod-outputs  (us-central1, Standard)

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
    Cliente para subir y descargar archivos de diseño a Cloud Storage.
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

    # ------------------------------------------------------------------ #
    #  Internos                                                            #
    # ------------------------------------------------------------------ #

    def _upload_sync(self, blob_path: str, content: str, content_type: str) -> str:
        """Sube texto a GCS (síncrono). Retorna gs:// path."""
        if self._bucket is None:
            raise RuntimeError("StorageClient no inicializado.")
        blob = self._bucket.blob(blob_path)
        blob.upload_from_string(content.encode("utf-8"), content_type=content_type)
        return f"gs://{BUCKET_NAME}/{blob_path}"

    def _download_sync(self, blob_path: str) -> str:
        """Descarga texto de GCS (síncrono). Retorna el contenido como str."""
        if self._bucket is None:
            raise RuntimeError("StorageClient no inicializado.")
        blob = self._bucket.blob(blob_path)
        return blob.download_as_text(encoding="utf-8")

    def _delete_sync(self, blob_path: str) -> None:
        """Elimina un blob de GCS (síncrono). No falla si no existe."""
        if self._bucket is None:
            return
        try:
            blob = self._bucket.blob(blob_path)
            blob.delete()
        except Exception:
            pass  # No importa si ya no existía

    # ------------------------------------------------------------------ #
    #  API pública — diseños                                               #
    # ------------------------------------------------------------------ #

    async def upload_design_html(self, design_id: str, html: str) -> str:
        """
        Sube el HTML de un diseño a GCS.
        Retorna el gs:// path.
        """
        if not html:
            return ""
        blob_path = f"designs/{design_id}/index.html"
        try:
            gcs_path = await asyncio.to_thread(
                self._upload_sync, blob_path, html, "text/html; charset=utf-8"
            )
            logger.info("Storage: HTML subido → %s (%d chars)", gcs_path, len(html))
            return gcs_path
        except Exception as e:
            logger.error("Storage.upload_design_html: %s", e)
            raise

    async def upload_design_markdown(self, design_id: str, markdown: str) -> str:
        """
        Sube el DESIGN.md de un diseño a GCS.
        Retorna el gs:// path.
        """
        if not markdown:
            return ""
        blob_path = f"designs/{design_id}/design.md"
        try:
            gcs_path = await asyncio.to_thread(
                self._upload_sync, blob_path, markdown, "text/markdown; charset=utf-8"
            )
            logger.info("Storage: Markdown subido → %s", gcs_path)
            return gcs_path
        except Exception as e:
            logger.error("Storage.upload_design_markdown: %s", e)
            raise

    async def download_text(self, gcs_path: str) -> str:
        """
        Descarga contenido de texto desde un gs:// path.
        Ejemplo: gs://quimera-ai-prod-outputs/designs/abc/index.html
        """
        if not gcs_path or not gcs_path.startswith("gs://"):
            return ""
        # Extraer el blob_path quitando el prefijo gs://<bucket>/
        prefix = f"gs://{BUCKET_NAME}/"
        blob_path = gcs_path[len(prefix):]
        try:
            content = await asyncio.to_thread(self._download_sync, blob_path)
            logger.info("Storage: descargado %s (%d chars)", gcs_path, len(content))
            return content
        except Exception as e:
            logger.error("Storage.download_text %s: %s", gcs_path, e)
            raise

    async def delete_design(self, design_id: str) -> None:
        """
        Elimina los archivos de un diseño de GCS (HTML + markdown).
        Se llama cuando el usuario elimina un diseño de la biblioteca.
        """
        for blob_path in [
            f"designs/{design_id}/index.html",
            f"designs/{design_id}/design.md",
        ]:
            await asyncio.to_thread(self._delete_sync, blob_path)
        logger.info("Storage: archivos del diseño %s eliminados.", design_id)
