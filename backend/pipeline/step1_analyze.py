"""
step1_analyze.py -- PASO 1: Analizar el brief y proponer un diseno
==================================================================
Inputs:  context.design_brief (obligatorio)
         context.critique     (si es una iteracion de correccion)
Outputs: context con campos de diseno completados:
           project_type, industry, target_audience, brand_personality,
           primary_color, secondary_color, accent_color, neutral_palette,
           heading_font, body_font, layout_type, composition_rule,
           color_harmony_type, design_rationale

Implementacion completa: Dia 2.
"""

import logging
from models import DesignContext
from services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

ANALYZE_SYSTEM_PROMPT = """
Eres un disenador visual senior con dominio de:
- Teoria del color (Itten, OKLCH, harmonias cromaticas)
- Composicion (Golden Ratio, Regla de los tercios)
- Psicologia de la Gestalt
- Psicologia del color por industria

REGLA OBLIGATORIA: Antes de proponer cualquier valor (color, tipografia, layout),
debes indicar el principio de diseno que lo justifica.

Formato de respuesta: JSON con esta estructura exacta:
{
  "project_type": "landing_page | dashboard | app",
  "industry": "string",
  "target_audience": "string",
  "brand_personality": ["adjetivo1", "adjetivo2", "adjetivo3"],
  "primary_color": {"valor": "#hex", "principio": "string", "razon": "string"},
  "secondary_color": {"valor": "#hex", "principio": "string", "razon": "string"},
  "accent_color": {"valor": "#hex", "principio": "string", "razon": "string"},
  "neutral_palette": ["#hex1", "#hex2", "#hex3", "#hex4"],
  "heading_font": {"valor": "string", "principio": "string", "razon": "string"},
  "body_font": {"valor": "string", "principio": "string", "razon": "string"},
  "layout_type": "string",
  "composition_rule": "rule_of_thirds | golden_ratio",
  "color_harmony_type": "complementario | analogo | triadico | monocromatico"
}
"""


async def analyze_and_design(context: DesignContext) -> DesignContext:
    """
    PASO 1: Analiza el brief y propone un diseno justificado.

    Si es una iteracion de correccion (context.iteration > 0), el critique
    del paso anterior se incluye en el prompt para guiar las correcciones.

    TODO Dia 2:
        1. Construir el prompt con design_brief + critique (si aplica)
        2. Llamar a GeminiClient.generate_json_with_retry(prompt, model="pro", temperature=0.7)
        3. Parsear la respuesta JSON a los campos de DesignContext
        4. Llamar a generate_harmonic_palette() de color_harmony.py
        5. Loggear la propuesta para debugging
    """
    logger.info("PASO 1 -- Analizando brief (iteracion %d): %s...",
                context.iteration, context.design_brief[:50])
    # TODO Dia 2: implementar llamado real a Gemini
    # client = GeminiClient()
    # prompt = _build_analyze_prompt(context)
    # proposal = await client.generate_json_with_retry(prompt, model="pro", temperature=0.7)
    # context = _apply_proposal_to_context(context, proposal)
    logger.warning("PASO 1: stub -- implementar en Dia 2")
    return context


def _build_analyze_prompt(context: DesignContext) -> str:
    """Construye el prompt para el Paso 1. TODO Dia 2."""
    prompt = f"{ANALYZE_SYSTEM_PROMPT}\n\nBrief del usuario:\n{context.design_brief}"
    if context.critique and context.iteration > 0:
        prompt += (
            f"\n\nCORRECCION REQUERIDA (iteracion {context.iteration}):\n"
            f"{context.critique}\n\n"
            "El diseno anterior no supero la evaluacion estetica. "
            "Aplica exactamente las correcciones indicadas."
        )
    return prompt


def _apply_proposal_to_context(context: DesignContext, proposal: dict) -> DesignContext:
    """Aplica el JSON de respuesta de Gemini al DesignContext. TODO Dia 2."""
    # context.project_type = proposal.get("project_type", "")
    # context.primary_color = proposal.get("primary_color", {}).get("valor")
    # context.design_rationale["primary_color"] = proposal.get("primary_color", {})
    return context
