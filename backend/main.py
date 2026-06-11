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

from models import HealthResponse, GeminiTestResponse, DesignRequest, DesignContext, SuggestRequest, SuggestResponse
from services.gemini_client import GeminiClient
from services.design_templates import get_templates_manager
from pipeline.step0_template_analysis import analyze_templates
from pipeline.step1_analyze import analyze_and_design
from pipeline.step2_analyze_images import analyze_for_images
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


@app.get("/templates", tags=["Referencia"])
async def list_templates():
    """Retorna la lista de templates de diseño disponibles para usar como referencia."""
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
# SUGERENCIAS DE BRIEF (ligero, sin Gemini, <50ms)
# ============================================================================

@app.post("/sugerir", response_model=SuggestResponse, tags=["Sugerencias"])
async def sugerir(request: SuggestRequest) -> SuggestResponse:
    """
    Analiza el brief y devuelve sugerencias en tiempo real.

    Sin llamadas a Gemini — responde en <50ms.
    El frontend llama a este endpoint con debounce mientras el usuario escribe.

    Retorna:
      - industry:   industria detectada
      - missing:    elementos que faltan en el brief (chips clicables)
      - styles:     estilos de diseño recomendados (chips clicables)
      - templates:  templates de la biblioteca que encajan (chips clicables)
      - palettes:   paletas de color por industria (chips clicables)
    """
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
# PIPELINE
# ============================================================================

@app.post("/generar-diseno", tags=["Pipeline"])
async def generar_diseno(request: DesignRequest):
    """
    Genera un diseño completo (DESIGN.md + HTML + Imágenes).

    Pipeline de 4 pasos:
      0. Analizar templates relevantes (patrones, composición, tipografía)
      1. Generar DESIGN.md (mejorado con patrones de templates)
      2. Analizar para generación de imágenes (dónde generar, qué generar)
      3. Generar HTML completo + inyectar imágenes

    Latencia: 30-50 segundos (con generación de imágenes: 60-120s).
    """
    try:
        start = time.monotonic()
        logger.info("Pipeline v3 iniciado para brief: %.50s...", request.design_brief[:50])

        # Crear contexto
        context = DesignContext(
            design_brief=request.design_brief,
            project_type=request.project_type,
            design_reference=request.design_reference,
        )

        # PASO 0: Analizar templates
        logger.info("Paso 0: Analizando templates relevantes...")
        context = await analyze_templates(context)
        logger.info("✓ Paso 0 completado. Templates: %s", 
                   context.template_analysis.relevant_templates if context.template_analysis else "None")

        # PASO 1: Generar DESIGN.md (mejorado)
        logger.info("Paso 1: Generando DESIGN.md mejorado...")
        context = await analyze_and_design(context)

        if not context.design_markdown:
            raise ValueError("DESIGN.md no fue generado")

        logger.info("✓ Paso 1 completado. DESIGN.md: %d caracteres", len(context.design_markdown))

        # PASO 2: Analizar para imágenes
        logger.info("Paso 2: Analizando qué imágenes generar...")
        context = await analyze_for_images(context)
        image_count = len(context.image_generation_plan.images) if context.image_generation_plan else 0
        logger.info("✓ Paso 2 completado. Imágenes a generar: %d", image_count)

        # PASO 3: Generar HTML + imágenes
        logger.info("Paso 3: Generando HTML + inyectando imágenes...")
        context = await generate_code(context)

        if not context.html_output:
            raise ValueError("HTML no fue generado")

        logger.info("✓ Paso 3 completado. HTML: %d caracteres", len(context.html_output))

        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info("✅ Pipeline v3 completado en %dms", elapsed_ms)

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
