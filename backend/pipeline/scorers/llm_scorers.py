"""
llm_scorers.py — Criterios 3-8: Scorers vía Gemini (temperatura=0)
===================================================================
6 scorers que evalúan aspectos de diseño que requieren percepción visual y
juicio contextual. Todos usan Gemini 2.5 Pro con temperatura=0 para máxima
reproducibilidad.

Por qué temperatura=0 para los scorers:
  Los scorers deben ser DETERMINISTAS: dado el mismo diseño, siempre dan
  el mismo resultado. Temperatura=0 elimina la aleatoriedad del LLM.
  Esto garantiza que los tests de regresión sean confiables.

Criterio 3 — Balance compositivo    (Regla de tercios · Golden Ratio)
Criterio 4 — Jerarquía visual       (Escala 1.25x · patrón F/Z)
Criterio 5 — Cumplimiento Gestalt   (Proximidad · Similitud · Continuidad)
Criterio 6 — Calidad espacio negativo (≥30% viewport libre)
Criterio 7 — Consistencia de marca  (Coherencia con brand_context)
Criterio 8 — Accesibilidad general  (No solo color · tamaños mínimos)

Cada scorer retorna (score: float, explanation: str) para que el critique
del loop de corrección pueda decir exactamente qué falló.

Este archivo se implementa completamente en el Día 3.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Template base para todos los scorers LLM
# Cada scorer personaliza el CRITERIO_DESCRIPTION y el JSON esperado
SCORER_SYSTEM_TEMPLATE = """
Eres un auditor de diseño visual. Tu trabajo es evaluar una propuesta de diseño
con MÁXIMA OBJETIVIDAD.

REGLAS OBLIGATORIAS:
1. Asigna una puntuación EXACTA de 0 a 100 (no rangos, no aproximaciones).
2. La puntuación debe ser reproducible: dado el mismo diseño, siempre da la misma nota.
3. Justifica en exactamente 2 líneas qué está bien y qué está mal.
4. Si el score es menor a 85, indica EXACTAMENTE qué valor específico resolvería el problema.

Temperatura: 0 (determinista)

Criterio a evaluar:
{criterio_description}

Diseño propuesto:
{design_summary}

Responde ÚNICAMENTE en este JSON:
{{
  "score": <número 0-100>,
  "justification": "<2 líneas máximo>",
  "fix": "<valor específico que resolvería el problema, o null si score >= 85>"
}}
"""


def _build_design_summary(context) -> str:
    """
    Convierte el DesignContext en un resumen legible para los scorers LLM.
    El LLM necesita el contexto en texto, no en un objeto Python.
    """
    return f"""
Tipo de proyecto: {context.project_type}
Industria: {context.industry}
Audiencia: {context.target_audience}
Personalidad de marca: {', '.join(context.brand_personality)}
Color primario: {context.primary_color}
Color secundario: {context.secondary_color}
Color de acento: {context.accent_color}
Paleta neutral: {', '.join(context.neutral_palette)}
Tipografía títulos: {context.heading_font}
Tipografía cuerpo: {context.body_font}
Layout: {context.layout_type}
Regla de composición: {context.composition_rule}
Tipo de armonía cromática: {context.color_harmony_type}
Rationale: {context.design_rationale}
"""


async def score_composition_balance(context) -> tuple[float, str]:
    """
    Criterio 3: Balance compositivo.

    Evalúa si el peso visual está distribuido equilibradamente según:
    - Regla de los tercios: elementos importantes en intersecciones de la cuadrícula 3×3
    - Golden Ratio (1.618): proporciones entre secciones principales
    - Simetría/asimetría: intencional y coherente con el tipo de layout

    Args:
        context: DesignContext con propuesta de diseño completa.

    Returns:
        (score: float 0-100, explanation: str)

    TODO Día 3: implementar con GeminiClient.generate_json(prompt, temperature=0.0)
    """
    logger.warning("score_composition_balance: stub — implementar en Día 3")
    return (75.0, "Stub — no evaluado aún")


async def score_visual_hierarchy(context) -> tuple[float, str]:
    """
    Criterio 4: Jerarquía visual.

    Evalúa:
    - Escala: el elemento más importante es al menos 1.25× más grande que el secundario
    - Contraste tonal: elementos importantes tienen mayor contraste con el fondo
    - Flujo F o Z: la pantalla sigue los patrones naturales de lectura

    TODO Día 3: implementar.
    """
    logger.warning("score_visual_hierarchy: stub — implementar en Día 3")
    return (75.0, "Stub — no evaluado aún")


async def score_gestalt_compliance(context) -> tuple[float, str]:
    """
    Criterio 5: Cumplimiento Gestalt.

    Leyes evaluadas:
    - Proximidad: elementos relacionados están físicamente cerca
    - Similitud: elementos del mismo tipo tienen el mismo estilo
    - Continuidad: el flujo de lectura sigue una dirección clara
    - Figura/Fondo: clara distinción entre contenido principal y fondo

    TODO Día 3: implementar.
    """
    logger.warning("score_gestalt_compliance: stub — implementar en Día 3")
    return (75.0, "Stub — no evaluado aún")


async def score_whitespace_quality(context) -> tuple[float, str]:
    """
    Criterio 6: Calidad del espacio negativo.

    Regla: al menos el 30% del viewport debe ser espacio negativo intencional.
    Evalúa también márgenes y separación entre secciones.

    TODO Día 3: implementar.
    """
    logger.warning("score_whitespace_quality: stub — implementar en Día 3")
    return (75.0, "Stub — no evaluado aún")


async def score_brand_consistency(context) -> tuple[float, str]:
    """
    Criterio 7: Consistencia de marca.

    Verifica coherencia entre propuesta visual y brand_context:
    - ¿Los colores corresponden a los mencionados por el usuario?
    - ¿La tipografía tiene la personalidad adecuada?
    - ¿El tono visual coincide con brand_personality?

    TODO Día 3: implementar.
    """
    logger.warning("score_brand_consistency: stub — implementar en Día 3")
    return (75.0, "Stub — no evaluado aún")


async def score_accessibility(context) -> tuple[float, str]:
    """
    Criterio 8: Accesibilidad general.

    Más allá del contraste (Criterio 2):
    - No depender solo del color para información (daltonismo)
    - Tamaños de fuente mínimos (≥16px para cuerpo)
    - Áreas de toque suficientes (≥44×44px para interactivos)

    TODO Día 3: implementar.
    """
    logger.warning("score_accessibility: stub — implementar en Día 3")
    return (75.0, "Stub — no evaluado aún")
