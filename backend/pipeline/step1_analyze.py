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
"""

import logging
from models import DesignContext
from services.gemini_client import GeminiClient
from pipeline.scorers.color_harmony import generate_harmonic_palette

logger = logging.getLogger(__name__)

ANALYZE_SYSTEM_PROMPT = """Eres un disenador visual senior con dominio de:
- Teoria del color (OKLCH, armonias cromaticas: complementaria, analoga, triadica, monocromatica)
- Composicion (Golden Ratio, Regla de los tercios)
- Psicologia de la Gestalt
- Psicologia del color por industria

REGLA OBLIGATORIA: Cada valor propuesto (color, tipografia, layout) DEBE incluir:
  - "valor": el valor concreto
  - "principio": el principio de diseno que lo justifica
  - "razon": por que aplica a este proyecto especifico

Responde UNICAMENTE con JSON valido, sin texto adicional, sin markdown.

Estructura exacta requerida:
{
  "project_type": "landing_page | dashboard | app",
  "industry": "fintech | healthtech | e-commerce | saas | educacion | otro",
  "target_audience": "descripcion concisa de la audiencia objetivo",
  "brand_personality": ["adjetivo1", "adjetivo2", "adjetivo3"],
  "primary_color": {
    "valor": "#HEXCODE",
    "principio": "nombre del principio de diseno",
    "razon": "por que este color para este proyecto"
  },
  "secondary_color": {
    "valor": "#HEXCODE",
    "principio": "nombre del principio de diseno",
    "razon": "por que este color para este proyecto"
  },
  "accent_color": {
    "valor": "#HEXCODE",
    "principio": "nombre del principio de diseno",
    "razon": "por que este color para este proyecto"
  },
  "neutral_palette": ["#hex1", "#hex2", "#hex3", "#hex4"],
  "heading_font": {
    "valor": "nombre de la fuente",
    "principio": "nombre del principio tipografico",
    "razon": "por que esta fuente para este proyecto"
  },
  "body_font": {
    "valor": "nombre de la fuente",
    "principio": "nombre del principio tipografico",
    "razon": "por que esta fuente para este proyecto"
  },
  "layout_type": "hero_centered | sidebar_left | grid_cards | full_width | split_screen",
  "composition_rule": "rule_of_thirds | golden_ratio",
  "color_harmony_type": "complementario | analogo | triadico | monocromatico"
}"""


async def analyze_and_design(context: DesignContext) -> DesignContext:
    """
    PASO 1: Analiza el brief y propone un diseno justificado.

    Si es una iteracion de correccion (context.iteration > 0), el critique
    del paso anterior se incluye en el prompt para guiar las correcciones.

    Args:
        context: DesignContext con design_brief obligatorio.

    Returns:
        DesignContext enriquecido con propuesta de diseno completa.
    """
    logger.info("PASO 1 -- Analizando brief (iteracion %d): %.50s...",
                context.iteration, context.design_brief)

    client = GeminiClient()
    prompt = _build_analyze_prompt(context)

    proposal = await client.generate_json_with_retry(
        prompt=prompt,
        model="pro",
        temperature=0.7,
        max_retries=3,
    )

    context = _apply_proposal_to_context(context, proposal)

    # Refinar paleta con armonias OKLCH reales
    if context.primary_color and context.color_harmony_type:
        try:
            harmonic = generate_harmonic_palette(
                context.primary_color,
                context.color_harmony_type,
            )
            # Siempre usar los valores OKLCH para secondary, accent y neutral.
            # Gemini elige el primary_color y el tipo de armonia;
            # los colores derivados se calculan matematicamente para garantizar
            # que score_color_harmony los detecte correctamente en PASO 2.
            # Si Gemini propone secondary/accent propios, suelen no cumplir
            # las relaciones angulares OKLCH reales y el scorer penaliza.
            context.secondary_color = harmonic["secondary"]
            context.accent_color = harmonic["accent"]
            context.neutral_palette = harmonic["neutral_palette"]
            logger.info("Paleta armonica generada con OKLCH para %s",
                        context.color_harmony_type)
        except Exception as e:
            logger.warning("No se pudo generar paleta armonica: %s", e)

    logger.info("PASO 1 completo. Proyecto: %s | Industria: %s | Color primario: %s",
                context.project_type, context.industry, context.primary_color)
    return context


def _build_analyze_prompt(context: DesignContext) -> str:
    """Construye el prompt para el Paso 1."""
    prompt = f"{ANALYZE_SYSTEM_PROMPT}\n\nBrief del usuario:\n{context.design_brief}"

    if context.critique and context.iteration > 0:
        prompt += (
            f"\n\nCORRECCION REQUERIDA (iteracion {context.iteration}):\n"
            f"{context.critique}\n\n"
            "El diseno anterior no supero la evaluacion estetica (score < 85). "
            "Aplica exactamente las correcciones indicadas y propone nuevos valores "
            "que resuelvan los criterios que fallaron."
        )
    return prompt


def _apply_proposal_to_context(context: DesignContext, proposal: dict) -> DesignContext:
    """
    Aplica el JSON de respuesta de Gemini al DesignContext.
    Extrae el campo 'valor' de los campos con principio/razon.
    Guarda el razonamiento completo en design_rationale.
    """
    context.project_type = proposal.get("project_type", "")
    context.industry = proposal.get("industry", "")
    context.target_audience = proposal.get("target_audience", "")
    context.brand_personality = proposal.get("brand_personality", [])

    # Campos con estructura {valor, principio, razon}
    for field in ["primary_color", "secondary_color", "accent_color",
                  "heading_font", "body_font"]:
        field_data = proposal.get(field, {})
        if isinstance(field_data, dict):
            setattr(context, field, field_data.get("valor"))
            context.design_rationale[field] = field_data
        elif isinstance(field_data, str):
            # Gemini a veces devuelve el valor directamente
            setattr(context, field, field_data)

    # Paleta neutral (lista de hex)
    context.neutral_palette = proposal.get("neutral_palette", [])

    # Campos simples
    context.layout_type = proposal.get("layout_type", "")
    context.composition_rule = proposal.get("composition_rule", "rule_of_thirds")
    context.color_harmony_type = proposal.get("color_harmony_type", "complementario")

    return context
