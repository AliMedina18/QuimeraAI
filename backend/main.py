import os
import json
import uuid
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from models import HealthResponse, GeminiTestResponse, DesignRequest, DesignContext
from services.gemini_client import GeminiClient
from services.firestore_client import FirestoreClient
from services.storage_client import StorageClient
from pipeline.step1_analyze import analyze_and_design
from pipeline.step2_evaluate import aesthetic_evaluate
from pipeline.step3_generate import generate_code

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

MAX_ITER = 3


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: startup y shutdown del servidor."""
    logger.info("Quimera Backend arrancando...")
    logger.info("Entorno: %s", os.getenv("ENVIRONMENT", "development"))
    logger.info("Proyecto GCP: %s", os.getenv("GCP_PROJECT_ID", "no configurado"))
    yield
    logger.info("Quimera Backend apagandose...")


app = FastAPI(
    title="Quimera API",
    description="Agente de IA para diseno visual -- evalua antes de generar",
    version="1.0.0",
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


# ---------------------------------------------------------------------------
# INFRAESTRUCTURA
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Infraestructura"])
async def health() -> HealthResponse:
    """
    Health check para Cloud Run.
    Cloud Run llama a este endpoint cada 30s.
    Si devuelve 2xx: servicio sano. Si falla 3 veces: Cloud Run reinicia el contenedor.
    """
    return HealthResponse(
        status="ok",
        service="quimera-backend",
        version="1.0.0",
    )


@app.get("/gemini-test", response_model=GeminiTestResponse, tags=["Infraestructura"])
async def gemini_test() -> GeminiTestResponse:
    """
    Prueba de integracion con Gemini. Verifica:
    1. GOOGLE_API_KEY esta configurada
    2. El SDK puede hacer una llamada exitosa
    3. La respuesta llega completa
    """
    try:
        client = GeminiClient()
        start = time.monotonic()
        response = await client.generate_text(
            prompt="Eres el backend del proyecto Quimera, un agente de IA para diseno visual. Responde en una oracion confirmando que estas operativo.",
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


# ---------------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------------

@app.post("/analyze", tags=["Pipeline"])
async def analyze(request: DesignRequest):
    """
    PASO 1 -- Analiza el brief y propone un diseno justificado.

    Recibe un brief en texto libre y retorna una propuesta de diseno completa:
    colores (con principio y razon), tipografia, layout, tipo de armonia cromatica.

    Latencia esperada: 5-10 segundos (llamada a Gemini 2.5 Pro).
    """
    try:
        start = time.monotonic()
        context = DesignContext(
            design_brief=request.design_brief,
            project_type=request.project_type or "",
        )
        context = await analyze_and_design(context)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("PASO 1 completado en %dms", elapsed_ms)
        return {
            "status": "ok",
            "elapsed_ms": elapsed_ms,
            "project_type": context.project_type,
            "industry": context.industry,
            "target_audience": context.target_audience,
            "brand_personality": context.brand_personality,
            "primary_color": context.primary_color,
            "secondary_color": context.secondary_color,
            "accent_color": context.accent_color,
            "neutral_palette": context.neutral_palette,
            "heading_font": context.heading_font,
            "body_font": context.body_font,
            "layout_type": context.layout_type,
            "composition_rule": context.composition_rule,
            "color_harmony_type": context.color_harmony_type,
            "design_rationale": context.design_rationale,
        }
    except Exception as e:
        logger.error("Error en /analyze: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/evaluate", tags=["Pipeline"])
async def evaluate(request: DesignRequest):
    """
    PASO 1+2 con loop de correccion automatico.

    Flujo completo:
      1. Paso 1: analyze_and_design() -> propuesta de diseno
      2. Paso 2: aesthetic_evaluate() -> 8 scores
      3. Si overall_score < 85 e iteration < 3: volver al Paso 1 con critique
      4. Repetir hasta aprobar o agotar iteraciones

    Latencia esperada: 30-60s (puede hacer hasta 3 ciclos de Paso1+Paso2).
    """
    try:
        start = time.monotonic()
        context = DesignContext(
            design_brief=request.design_brief,
            project_type=request.project_type or "",
        )

        while True:
            context = await analyze_and_design(context)
            context = await aesthetic_evaluate(context)

            logger.info(
                "Iteracion %d: overall_score=%.1f approved=%s",
                context.iteration, context.overall_score or 0, context.approved
            )

            if context.approved or context.iteration >= MAX_ITER:
                break

        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("Pipeline Paso1+2 completado en %dms tras %d iteracion(es)",
                    elapsed_ms, context.iteration)
        return {
            "status": "ok",
            "elapsed_ms": elapsed_ms,
            "overall_score": context.overall_score,
            "approved": context.approved,
            "iterations_used": context.iteration,
            "aesthetic_scores": context.aesthetic_scores,
            "critique": context.critique,
            "design_proposal": {
                "primary_color": context.primary_color,
                "secondary_color": context.secondary_color,
                "accent_color": context.accent_color,
                "heading_font": context.heading_font,
                "body_font": context.body_font,
                "layout_type": context.layout_type,
                "color_harmony_type": context.color_harmony_type,
            },
        }
    except Exception as e:
        logger.error("Error en /evaluate: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/generar-diseno", tags=["Pipeline"])
async def generar_diseno(request: DesignRequest):
    """
    PIPELINE COMPLETO con SSE streaming.

    Flujo:
      Paso 1: analyze_and_design()          -> propuesta de diseno
      Paso 2: aesthetic_evaluate()           -> 8 scores (loop hasta >= 85 o 3 iteraciones)
      Paso 3: generate_code()                -> React + CSS tokens + rationale
      Guardar: Firestore + Cloud Storage     -> URLs de los archivos

    Cada transicion emite un evento SSE:
      {"paso": "analisis",   "status": "iniciando"|"completado", ...}
      {"paso": "evaluacion", "status": "aprobado"|"corrigiendo", "overall_score": ..., ...}
      {"paso": "generacion", "status": "iniciando"|"completado"}
      {"paso": "guardando",  "status": "iniciando"}
      {"paso": "completado", "project_id": ..., "react_component": ..., ...}
      {"error": "mensaje"}    -- si hay un error fatal

    Probar con curl (Swagger UI no renderiza SSE):
      curl -X POST http://localhost:8000/generar-diseno
           -H "Content-Type: application/json"
           -d '{"design_brief": "Landing para fintech..."}'
           --no-buffer

    Latencia esperada: 45-90 segundos.
    """
    async def event_stream():
        def sse(data: dict) -> str:
            return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        project_id = str(uuid.uuid4())[:12]
        start = time.monotonic()

        try:
            context = DesignContext(
                design_brief=request.design_brief,
                project_type=request.project_type or "",
            )

            yield sse({
                "paso": "inicio",
                "project_id": project_id,
                "status": "Pipeline Quimera iniciado",
            })

            # --- Loop Paso 1 + Paso 2 ---
            while True:
                yield sse({
                    "paso": "analisis",
                    "iteration": context.iteration + 1,
                    "status": "Analizando brief y proponiendo diseno...",
                })
                context = await analyze_and_design(context)
                yield sse({
                    "paso": "analisis",
                    "status": "completado",
                    "primary_color": context.primary_color,
                    "secondary_color": context.secondary_color,
                    "accent_color": context.accent_color,
                    "layout_type": context.layout_type,
                    "color_harmony_type": context.color_harmony_type,
                    "heading_font": context.heading_font,
                })

                yield sse({
                    "paso": "evaluacion",
                    "iteration": context.iteration + 1,
                    "status": "Evaluando 8 criterios esteticos...",
                })
                context = await aesthetic_evaluate(context)
                yield sse({
                    "paso": "evaluacion",
                    "status": "aprobado" if context.approved else "corrigiendo",
                    "overall_score": context.overall_score,
                    "approved": context.approved,
                    "iteration": context.iteration,
                    "aesthetic_scores": context.aesthetic_scores,
                })

                if context.approved or context.iteration >= MAX_ITER:
                    break

                yield sse({
                    "paso": "correccion",
                    "status": f"Score {context.overall_score:.1f} < 85. Aplicando correcciones...",
                    "critique_preview": (context.critique or "")[:200],
                })

            # --- Paso 3: Generacion ---
            yield sse({
                "paso": "generacion",
                "status": "Generando componente React + design tokens...",
            })
            context = await generate_code(context)
            yield sse({
                "paso": "generacion",
                "status": "completado",
                "component_size": len(context.react_component or ""),
                "tokens_size": len(context.design_tokens_css or ""),
            })

            # --- Guardar en Firestore + Storage ---
            yield sse({"paso": "guardando", "status": "Guardando en Cloud Storage y Firestore..."})

            component_url = f"gs://quimera-ai-prod-outputs/projects/{project_id}/componente.tsx"
            tokens_url    = f"gs://quimera-ai-prod-outputs/projects/{project_id}/tokens.css"
            rationale_url = f"gs://quimera-ai-prod-outputs/projects/{project_id}/rationale.md"

            try:
                storage = StorageClient()
                component_url = await storage.upload_component(project_id, context.react_component or "")
                tokens_url    = await storage.upload_tokens(project_id, context.design_tokens_css or "")
                rationale_url = await storage.upload_rationale(project_id, context.rationale_document or "")
            except Exception as e:
                logger.warning("Storage fallo (no critico): %s", e)

            try:
                firestore_client = FirestoreClient()
                await firestore_client.save_generated_output(project_id, {
                    "project_id": project_id,
                    "design_brief": context.design_brief,
                    "overall_score": context.overall_score,
                    "approved": context.approved,
                    "iterations": context.iteration,
                    "aesthetic_scores": context.aesthetic_scores,
                    "component_url": component_url,
                    "tokens_url": tokens_url,
                    "rationale_url": rationale_url,
                    "primary_color": context.primary_color,
                    "layout_type": context.layout_type,
                })
            except Exception as e:
                logger.warning("Firestore fallo (no critico): %s", e)

            elapsed_ms = int((time.monotonic() - start) * 1000)
            logger.info("Pipeline completo en %dms. project_id=%s score=%.1f",
                        elapsed_ms, project_id, context.overall_score or 0)

            yield sse({
                "paso": "completado",
                "project_id": project_id,
                "elapsed_ms": elapsed_ms,
                "overall_score": context.overall_score,
                "approved": context.approved,
                "iterations": context.iteration,
                "design_proposal": {
                    "primary_color": context.primary_color,
                    "secondary_color": context.secondary_color,
                    "accent_color": context.accent_color,
                    "heading_font": context.heading_font,
                    "body_font": context.body_font,
                    "layout_type": context.layout_type,
                    "color_harmony_type": context.color_harmony_type,
                },
                "component_url": component_url,
                "tokens_url": tokens_url,
                "rationale_url": rationale_url,
                "react_component": context.react_component or "",
                "design_tokens_css": context.design_tokens_css or "",
                "rationale_document": context.rationale_document or "",
            })

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            logger.error("Error fatal en /generar-diseno [%dms]: %s", elapsed_ms, e)
            yield sse({"error": str(e), "elapsed_ms": elapsed_ms})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

