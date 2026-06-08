"""
Quimera Backend (Versión Simplificada)
======================================

Pipeline de 2 pasos:
1. Brief → DESIGN.md (Gemini Pro)
2. DESIGN.md → HTML completo (Gemini Flash)

Sin evaluación, sin iteraciones. Solo generación de interfaces.
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
from pipeline.step3_generate import generate_code

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: startup y shutdown del servidor."""
    logger.info("Quimera Backend (Simplificado) arrancando...")
    logger.info("Entorno: %s", os.getenv("ENVIRONMENT", "development"))
    yield
    logger.info("Quimera Backend apagandose...")


app = FastAPI(
    title="Quimera API",
    description="Generador simple de interfaces. Brief → DESIGN.md → HTML",
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
    """Health check para Cloud Run."""
    return HealthResponse(
        status="ok",
        service="quimera-backend",
        version="2.0.0",
    )


@app.get("/gemini-test", response_model=GeminiTestResponse, tags=["Infraestructura"])
async def gemini_test() -> GeminiTestResponse:
    """Prueba de integración con Gemini."""
    try:
        client = GeminiClient()
        start = time.monotonic()
        response = await client.generate_text(
            prompt="Eres Quimera, generador de interfaces. Confirma que estás operativo.",
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


# ============================================================================
# PIPELINE
# ============================================================================

@app.post("/generar-diseno", tags=["Pipeline"])
async def generar_diseno(request: DesignRequest):
    """
    Genera un diseño completo (DESIGN.md + HTML autocontenido).

    Pipeline:
      1. Brief → DESIGN.md (Paso 1, Gemini Pro)
      2. DESIGN.md → HTML completo (Paso 2, Gemini Flash)

    Sin evaluación, sin iteraciones. Una sola pasada.

    Latencia: 25-40 segundos.
    """
    try:
        start = time.monotonic()
        logger.info("Pipeline iniciado para brief: %.50s...", request.design_brief[:50])

        # Paso 1: Generar DESIGN.md
        logger.info("Paso 1: Generando DESIGN.md...")
        context = DesignContext(
            design_brief=request.design_brief,
            project_type=request.project_type,
        )
        context = await analyze_and_design(context)

        if not context.design_markdown:
            raise ValueError("DESIGN.md no fue generado")

        logger.info("Paso 1 completado. DESIGN.md: %d caracteres", len(context.design_markdown))

        # Paso 2: Generar HTML completo
        logger.info("Paso 2: Generando HTML completo...")
        context = await generate_code(context)

        if not context.html_output:
            raise ValueError("HTML no fue generado")

        logger.info("Paso 2 completado. HTML: %d caracteres", len(context.html_output))

        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("Pipeline completado en %dms", elapsed_ms)

        return {
            "status": "ok",
            "elapsed_ms": elapsed_ms,
            "design_markdown": context.design_markdown,
            "html_output": context.html_output,
        }

    except Exception as e:
        logger.error("Error en /generar-diseno: %s", e)
        raise HTTPException(status_code=503, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
