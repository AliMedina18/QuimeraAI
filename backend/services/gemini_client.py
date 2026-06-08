"""
gemini_client.py -- Wrapper del SDK de Google GenAI (google-genai)
===================================================================
Centraliza toda la comunicacion con Gemini.
El resto del pipeline solo llama a este cliente.

SDK: google-genai (el nuevo, reemplaza al deprecado google-generativeai)
Instalacion: pip install google-genai

Autenticacion:
  Vertex AI (por defecto): usa Application Default Credentials (ADC) de gcloud.
    - Local: correr 'gcloud auth application-default login'
    - Cloud Run: credenciales automaticas del Service Account
  AI Studio (fallback): agrega USE_VERTEX_AI=false en .env y pon GOOGLE_API_KEY

Modelos:
  gemini-2.5-pro   -> Paso 1 (analisis) + Paso 2 (scorers LLM, temperatura=0)
  gemini-2.5-flash -> Paso 3 (generacion de codigo, mas rapido y barato)
"""

import os
import json
import asyncio
import logging
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:
    pass  # .env no requerido en entornos con variables ya seteadas
logger = logging.getLogger(__name__)

MODEL_PRO = os.getenv("GEMINI_MODEL_PRO", "gemini-2.5-pro")
MODEL_FLASH = os.getenv("GEMINI_MODEL_FLASH", "gemini-2.5-flash")
GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "quimera-ai-prod")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")


class GeminiClient:
    """
    Cliente para Gemini usando el SDK google-genai.
    Usa Vertex AI por defecto (credenciales ADC de gcloud).
    Fallback a API key de AI Studio si USE_VERTEX_AI=false en .env.
    """

    def __init__(self) -> None:
        use_vertex = os.getenv("USE_VERTEX_AI", "true").lower() != "false"

        if use_vertex:
            self._client = genai.Client(
                vertexai=True,
                project=GCP_PROJECT,
                location=GCP_LOCATION,
            )
            logger.info("GeminiClient OK (Vertex AI). Proyecto: %s | Pro: %s | Flash: %s",
                        GCP_PROJECT, MODEL_PRO, MODEL_FLASH)
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "GOOGLE_API_KEY no esta configurada.\n"
                    "  Agrega GOOGLE_API_KEY en backend/.env\n"
                    "  O usa Vertex AI (por defecto): corre 'gcloud auth application-default login'"
                )
            self._client = genai.Client(api_key=api_key)
            logger.info("GeminiClient OK (AI Studio). Pro: %s | Flash: %s", MODEL_PRO, MODEL_FLASH)

    def _model_name(self, model: str) -> str:
        return MODEL_FLASH if model == "flash" else MODEL_PRO

    async def generate_text(
        self,
        prompt: str,
        model: str = "pro",
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
    ) -> str:
        """
        Genera texto a partir de un prompt.

        Args:
            model: 'pro' (gemini-2.5-pro) o 'flash' (gemini-2.5-flash)
            temperature: 0.0 = determinista, 1.0 = creativo
                         Los scorers del Paso 2 usan 0.0 para reproducibilidad
        """
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        # asyncio.to_thread: ejecuta la llamada sincrona en un thread del pool.
        # Sin esto bloquea el event loop de FastAPI durante 5-30 segundos.
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._model_name(model),
            contents=prompt,
            config=config,
        )
        return response.text

    async def generate_json(
        self,
        prompt: str,
        model: str = "pro",
        temperature: float = 0.7,
    ) -> dict:
        """
        Genera una respuesta JSON estructurada.
        Limpia automaticamente los bloques de codigo que Gemini a veces anade.
        """
        full_prompt = (
            f"{prompt}\n\n"
            "IMPORTANTE: Responde UNICAMENTE con JSON valido. "
            "Sin texto adicional. Sin bloques ```json. Sin markdown."
        )
        text = await self.generate_text(full_prompt, model=model, temperature=temperature)
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Gemini devolvio JSON invalido: %s\nRespuesta: %s", e, text[:500])
            raise

    async def generate_with_retry(
        self,
        prompt: str,
        model: str = "pro",
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> str:
        """Genera texto con retry exponencial (1s -> 2s -> 4s)."""
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                return await self.generate_text(prompt, model=model, temperature=temperature)
            except Exception as e:
                last_error = e
                wait_time = 2 ** attempt
                logger.warning("Intento %d/%d fallo: %s. Esperando %ds...",
                               attempt + 1, max_retries, e, wait_time)
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
        raise RuntimeError(f"Gemini fallo tras {max_retries} intentos. Ultimo: {last_error}")

    async def generate_json_with_retry(
        self,
        prompt: str,
        model: str = "pro",
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> dict:
        """Genera JSON con retry exponencial."""
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                return await self.generate_json(prompt, model=model, temperature=temperature)
            except Exception as e:
                last_error = e
                wait_time = 2 ** attempt
                logger.warning("JSON intento %d/%d fallo: %s. Esperando %ds...",
                               attempt + 1, max_retries, e, wait_time)
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
        raise RuntimeError(f"generate_json fallo tras {max_retries} intentos. Ultimo: {last_error}")
