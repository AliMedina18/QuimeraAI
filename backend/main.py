"""
main.py -- Punto de entrada FastAPI de Quimera
==============================================
Endpoints del Dia 1:
  GET  /health       -> Health check. Cloud Run lo llama cada 30s.
  GET  /gemini-test  -> Confirma que Gemini responde correctamente.

Endpoints del Dia 2:
  POST /analyze      -> Paso 1 del pipeline: analiza brief y propone diseno.

Endpoints que se implementan en dias siguientes:
  POST /evaluate       -> Dia 3: Motor de Evaluacion Estetica
  POST /generar-diseno -> Dia 4: pipeline completo con SSE streaming
"""

import os
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import HealthResponse, GeminiTestResponse, DesignRequest, DesignContext
from services.gemini_client import GeminiClient
from pipeline.step1_analyze import analyze_and_design

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


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
    """PASO 2 -- Motor de Evaluacion Estetica. Implementar en Dia 3."""
    raise HTTPException(status_code=501, detail="En construccion -- Dia 3")


@app.post("/generar-diseno", tags=["Pipeline"])
async def generar_diseno(request: DesignRequest):
    """Pipeline completo con SSE streaming. Implementar en Dia 4."""
    raise HTTPException(status_code=501, detail="En construccion -- Dia 4")
