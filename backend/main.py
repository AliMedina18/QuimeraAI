"""
Quimera Backend
===============
Pipeline: Brief -> DESIGN.md -> HTML completo
"""

import asyncio
import os
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from models import HealthResponse, GeminiTestResponse, DesignRequest, DesignContext, SuggestRequest, SuggestResponse
from services.gemini_client import GeminiClient
from services.design_templates import get_templates_manager
from pipeline.step0_template_analysis import analyze_templates
from pipeline.step1_analyze import analyze_and_design
from pipeline.step2_analyze_images import analyze_for_images
from pipeline.step3_generate import generate_code
from pipeline.step_edit import edit_html

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Quimera Backend arrancando...")
    logger.info("Entorno: %s", os.getenv("ENVIRONMENT", "development"))
    yield
    logger.info("Quimera Backend apagandose...")


app = FastAPI(
    title="Quimera API",
    description="Generador de interfaces. Brief -> DESIGN.md -> HTML",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# INFRAESTRUCTURA
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Infraestructura"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="quimera-backend",
        version="2.0.0",
    )


@app.get("/gemini-test", response_model=GeminiTestResponse, tags=["Infraestructura"])
async def gemini_test() -> GeminiTestResponse:
    try:
        client = GeminiClient()
        start = time.monotonic()
        response = await client.generate_text(
            prompt="Eres Quimera, generador de interfaces. Confirma que estas operativo.",
            model="pro",
            temperature=0.3,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("Gemini respondio en %dms", elapsed_ms)
        return GeminiTestResponse(
            status="ok",
            model_used=os.getenv("GEMINI_MODEL_PRO", "gemini-2.5-pro"),
            gemini_response=response.strip(),
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error("Error llamando a Gemini: %s", e)
        raise HTTPException(status_code=503, detail=f"Gemini no disponible: {str(e)}")


@app.get("/templates", tags=["Referencia"])
async def list_templates():
    try:
        manager = get_templates_manager()
        templates = manager.list_available()
        metadata = manager.get_all_metadata()
        return {
            "status": "ok",
            "total": len(templates),
            "available": templates,
            "metadata": metadata,
        }
    except Exception as e:
        logger.error("Error listando templates: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SUGERENCIAS DE BRIEF
# ============================================================================

@app.post("/sugerir", response_model=SuggestResponse, tags=["Sugerencias"])
async def sugerir(request: SuggestRequest) -> SuggestResponse:
    from services.suggestion_engine import analyze_brief
    from models import MissingElement, StyleSuggestion, TemplateSuggestion, ColorPalette
    try:
        result = analyze_brief(request.brief)
        return SuggestResponse(
            industry=result["industry"],
            confidence=result["confidence"],
            missing=[MissingElement(**m) for m in result["missing"]],
            styles=[StyleSuggestion(**s) for s in result["styles"]],
            templates=[TemplateSuggestion(**t) for t in result["templates"]],
            palettes=[ColorPalette(**p) for p in result["palettes"]],
        )
    except Exception as e:
        logger.error("Error en /sugerir: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PIPELINE: GENERACION DESDE CERO
# ============================================================================

@app.post("/generar-diseno", tags=["Pipeline"])
async def generar_diseno(request: DesignRequest):
    """
    Genera un diseno completo (DESIGN.md + HTML).
    Latencia: 30-50 segundos.
    """
    try:
        start = time.monotonic()
        logger.info("Pipeline v3 iniciado: %.50s...", request.design_brief[:50])

        context = DesignContext(
            design_brief=request.design_brief,
            project_type=request.project_type,
            design_reference=request.design_reference,
        )

        logger.info("Paso 0: Analizando templates...")
        context = await analyze_templates(context)

        logger.info("Paso 1: Generando DESIGN.md...")
        context = await analyze_and_design(context)
        if not context.design_markdown:
            raise ValueError("DESIGN.md no fue generado")

        logger.info("Paso 2: Analizando imagenes...")
        context = await analyze_for_images(context)
        image_count = len(context.image_generation_plan.images) if context.image_generation_plan else 0

        logger.info("Paso 3: Generando HTML...")
        context = await generate_code(context)
        if not context.html_output:
            raise ValueError("HTML no fue generado")

        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("Pipeline completado en %dms", elapsed_ms)

        return {
            "status": "ok",
            "elapsed_ms": elapsed_ms,
            "design_markdown": context.design_markdown,
            "html_output": context.html_output,
            "template_analysis": {
                "relevant_templates": context.template_analysis.relevant_templates if context.template_analysis else [],
                "primary_template": context.template_analysis.primary_template if context.template_analysis else None,
                "strategy": context.template_analysis.design_strategy_summary if context.template_analysis else None,
            },
            "images_plan": {
                "total": image_count,
                "estimated_cost": context.image_generation_plan.estimated_cost if context.image_generation_plan else 0.0,
            }
        }

    except Exception as e:
        logger.error("Error en /generar-diseno: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# STUDIO MODE: EDICION QUIRURGICA
# ============================================================================

class EditRequest(BaseModel):
    """Payload para edicion quirurgica de un diseno existente."""
    html_actual: str = Field(..., description="HTML completo del diseno actual")
    instruccion: str = Field(..., min_length=3, description="Que cambiar en el diseno")
    elemento_contexto: Optional[str] = Field(default=None, description="outerHTML del elemento seleccionado")
    design_markdown: Optional[str] = Field(default=None, description="DESIGN.md para contexto")


@app.post("/editar-diseno", tags=["Studio"])
async def editar_diseno(request: EditRequest):
    """
    Edita quirurgicamente un HTML existente generado por Quimera.
    Aplica la instruccion sin regenerar el diseno desde cero.
    Latencia: 5-15 segundos (usa Gemini Flash).
    """
    try:
        start = time.monotonic()
        logger.info(
            "Edicion iniciada. Instruccion: %.60s... | Elemento: %s",
            request.instruccion,
            "si" if request.elemento_contexto else "no",
        )

        html_modificado = await edit_html(
            html_actual=request.html_actual,
            instruccion=request.instruccion,
            elemento_contexto=request.elemento_contexto,
            design_markdown=request.design_markdown,
        )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("Edicion completada en %dms. HTML: %d chars", elapsed_ms, len(html_modificado))

        return {
            "status": "ok",
            "elapsed_ms": elapsed_ms,
            "html_output": html_modificado,
        }

    except Exception as e:
        logger.error("Error en /editar-diseno: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# USUARIOS — REGISTRO Y EMAIL DE BIENVENIDA
# ============================================================================

class RegisterUserRequest(BaseModel):
    name: str  = Field(..., min_length=1, max_length=100, description="Nombre del usuario")
    email: str = Field(..., min_length=5, max_length=200, description="Correo electrónico")


@app.post("/usuarios/registrar", tags=["Usuarios"])
async def registrar_usuario(request: RegisterUserRequest):
    """
    Registra un nuevo usuario y le envía un correo de bienvenida via SendGrid.
    Requiere SENDGRID_API_KEY en el entorno (.env o Secret Manager en Cloud Run).
    """
    import re
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', request.email):
        raise HTTPException(status_code=422, detail="Formato de email inválido")

    from services.email_client import send_welcome_email
    email_sent = await send_welcome_email(name=request.name, to_email=request.email)
    logger.info(
        "Registro: %s <%s> — email_sent=%s",
        request.name, request.email, email_sent,
    )
    return {"status": "ok", "email_sent": email_sent}


# ============================================================================
# BIBLIOTECA DE DISEÑOS
# ============================================================================

_firestore = None
_storage   = None

def _get_firestore():
    global _firestore
    if _firestore is None:
        from services.firestore_client import FirestoreClient
        _firestore = FirestoreClient()
    return _firestore

def _get_storage():
    global _storage
    if _storage is None:
        from services.storage_client import StorageClient
        _storage = StorageClient()
    return _storage


class SaveDesignRequest(BaseModel):
    session_id:      str           = Field(..., min_length=1, description="ID de sesion del usuario (UUID desde localStorage)")
    name:            str           = Field(..., min_length=1, max_length=100, description="Nombre del diseño")
    html_output:     str           = Field(..., min_length=1, description="HTML completo del diseño")
    design_markdown: str           = Field(default="", description="DESIGN.md opcional")
    design_id:       Optional[str] = Field(default=None, description="ID para actualizar un diseño existente")


@app.post("/biblioteca/guardar", tags=["Biblioteca"])
async def guardar_diseno(request: SaveDesignRequest):
    """
    Guarda o actualiza un diseño en la biblioteca del usuario.
    1. Sube HTML y DESIGN.md a Cloud Storage (GCS).
    2. Guarda las rutas GCS en Firestore (evita el límite de 1 MB por documento).
    """
    import uuid as _uuid
    try:
        fs  = _get_firestore()
        gcs = _get_storage()

        # Reutilizar design_id si es actualización, o generar uno nuevo
        did = request.design_id or str(_uuid.uuid4())

        # 1. Subir archivos a GCS en paralelo
        html_gcs_path, markdown_gcs_path = await asyncio.gather(
            gcs.upload_design_html(did, request.html_output),
            gcs.upload_design_markdown(did, request.design_markdown),
            return_exceptions=True,
        )

        # Si GCS falla, hacer fallback a guardado inline en Firestore
        html_gcs_ok     = isinstance(html_gcs_path,     str) and html_gcs_path
        markdown_gcs_ok = isinstance(markdown_gcs_path, str) and markdown_gcs_path

        if not html_gcs_ok:
            logger.warning("GCS upload falló para HTML (design=%s), usando fallback inline.", did)
            html_gcs_path = ""
        if not markdown_gcs_ok:
            logger.warning("GCS upload falló para Markdown (design=%s), usando fallback inline.", did)
            markdown_gcs_path = ""

        # 2. Guardar metadatos en Firestore
        design_id = await fs.save_design(
            session_id=request.session_id,
            name=request.name,
            design_id=did,
            html_gcs_path=html_gcs_path     if html_gcs_ok     else "",
            markdown_gcs_path=markdown_gcs_path if markdown_gcs_ok else "",
            # Fallback inline si GCS no estuvo disponible
            html_output=request.html_output         if not html_gcs_ok     else "",
            design_markdown=request.design_markdown if not markdown_gcs_ok else "",
        )

        logger.info(
            "Biblioteca: diseño %s guardado. GCS: html=%s, md=%s",
            design_id, html_gcs_ok, markdown_gcs_ok,
        )
        return {"status": "ok", "design_id": design_id, "gcs": html_gcs_ok}

    except Exception as e:
        logger.error("Error en /biblioteca/guardar: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/biblioteca", tags=["Biblioteca"])
async def listar_disenos(session_id: str):
    """Lista los diseños guardados de una sesion (solo metadatos, sin HTML)."""
    try:
        fs = _get_firestore()
        designs = await fs.list_designs(session_id)
        return {"status": "ok", "total": len(designs), "designs": designs}
    except Exception as e:
        logger.error("Error en /biblioteca: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/biblioteca/{design_id}", tags=["Biblioteca"])
async def obtener_diseno(design_id: str):
    """
    Obtiene un diseño completo por ID.
    Si el HTML está en GCS, lo descarga y lo incluye en la respuesta.
    Compatibilidad hacia atrás: si el doc tiene html_output inline, lo usa directamente.
    """
    try:
        fs  = _get_firestore()
        gcs = _get_storage()

        design = await fs.get_design(design_id)
        if design is None:
            raise HTTPException(status_code=404, detail="Diseño no encontrado")

        # Descargar HTML desde GCS si aplica
        html_gcs_path     = design.pop("html_gcs_path",     "")
        markdown_gcs_path = design.pop("markdown_gcs_path", "")

        if html_gcs_path:
            try:
                design["html_output"] = await gcs.download_text(html_gcs_path)
            except Exception as gcs_err:
                logger.error("GCS download HTML %s: %s", html_gcs_path, gcs_err)
                design["html_output"] = design.get("html_output", "")

        if markdown_gcs_path:
            try:
                design["design_markdown"] = await gcs.download_text(markdown_gcs_path)
            except Exception as gcs_err:
                logger.error("GCS download Markdown %s: %s", markdown_gcs_path, gcs_err)
                design["design_markdown"] = design.get("design_markdown", "")

        return {"status": "ok", "design": design}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error en /biblioteca/%s: %s", design_id, e)
        raise HTTPException(status_code=503, detail=str(e))


@app.delete("/biblioteca/{design_id}", tags=["Biblioteca"])
async def eliminar_diseno(design_id: str):
    """
    Elimina un diseño de la biblioteca.
    Borra tanto el documento de Firestore como los archivos en GCS.
    """
    try:
        fs  = _get_firestore()
        gcs = _get_storage()

        deleted_doc = await fs.delete_design(design_id)
        if deleted_doc is None:
            raise HTTPException(status_code=404, detail="Diseño no encontrado")

        # Limpiar GCS (fire-and-forget; no bloquear si falla)
        try:
            await gcs.delete_design(design_id)
        except Exception as gcs_err:
            logger.warning("GCS delete design %s: %s", design_id, gcs_err)

        return {"status": "ok", "deleted": design_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error en DELETE /biblioteca/%s: %s", design_id, e)
        raise HTTPException(status_code=503, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
