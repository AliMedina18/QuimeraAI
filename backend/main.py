"""
main.py -- Punto de entrada FastAPI de Quimera
==============================================
Endpoints del Dia 1:
  GET  /health       -> Health check. Cloud Run lo llama cada 30s.
  GET  /gemini-test  -> Confirma que Gemini responde correctamente.

Endpoints que se implementan en dias siguientes:
  POST /analyze        -> Dia 2: Paso 1 del pipeline
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

from models import HealthResponse, GeminiTestResponse, DesignRequest
from services.gemini_client import GeminiClient

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
    """PASO 1 -- Analiza el brief y propone diseno. Implementar en Dia 2."""
    raise HTTPException(status_code=501, detail="En construccion -- Dia 2")


@app.post("/evaluate", tags=["Pipeline"])
async def evaluate(request: DesignRequest):
    """PASO 2 -- Motor de Evaluacion Estetica. Implementar en Dia 3."""
    raise HTTPException(status_code=501, detail="En construccion -- Dia 3")


@app.post("/generar-diseno", tags=["Pipeline"])
async def generar_diseno(request: DesignRequest):
    """Pipeline completo con SSE streaming. Implementar en Dia 4."""
    raise HTTPException(status_code=501, detail="En construccion -- Dia 4")
