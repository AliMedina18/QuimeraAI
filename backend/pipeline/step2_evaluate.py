"""
step2_evaluate.py — PASO 2: Motor de Evaluación Estética
=========================================================
Responsabilidad: Evaluar la propuesta de diseño del Paso 1 en 8 criterios.
Si el score < 85, generar un diagnóstico y activar el loop de corrección.

Inputs:  context con todos los campos de diseño del Paso 1
Outputs: context con aesthetic_scores, overall_score, approved, critique

Los 8 criterios:
  Algorítmicos (deterministas):
    1. color_harmony    ← score_color_harmony()    en scorers/color_harmony.py
    2. wcag_contrast    ← score_wcag_contrast()    en scorers/wcag_contrast.py

  LLM (temperatura=0, Gemini 2.5 Pro):
    3. composition_balance  ← score_composition_balance()
    4. visual_hierarchy     ← score_visual_hierarchy()
    5. gestalt_compliance   ← score_gestalt_compliance()
    6. whitespace_quality   ← score_whitespace_quality()
    7. brand_consistency    ← score_brand_consistency()
    8. accessibility        ← score_accessibility()

Este archivo se implementa completamente en el Día 3.
"""

import logging
from models import DesignContext, AestheticScores

logger = logging.getLogger(__name__)

# Umbral mínimo para que el diseño sea aprobado
APPROVAL_THRESHOLD = 85.0
MAX_ITERATIONS = 3


async def aesthetic_evaluate(context: DesignContext) -> DesignContext:
    """
    PASO 2: Ejecuta los 8 scorers y decide si el diseño pasa o necesita corrección.

    Flujo:
        1. Ejecutar scorer algorítmico de armonía cromática (OKLCH)
        2. Ejecutar scorer algorítmico de contraste WCAG
        3. Ejecutar 6 scorers LLM con temperatura=0 (en paralelo con asyncio.gather)
        4. Calcular overall_score = promedio de los 8
        5. Si overall_score >= 85: context.approved = True
        6. Si overall_score < 85 y iteration < 3: generar critique específico
        7. Si iteration >= 3: aprobar con advertencia (mejor resultado disponible)

    Args:
        context: DesignContext con propuesta de diseño del Paso 1.

    Returns:
        context con aesthetic_scores, overall_score, approved, critique actualizados.

    TODO Día 3:
        - Importar scorers desde scorers/color_harmony.py, wcag_contrast.py, llm_scorers.py
        - Implementar asyncio.gather para los 6 scorers LLM en paralelo
        - Implementar _generate_critique() que produce diagnóstico específico
        - Registrar cada iteración en Firestore
    """
    logger.info("PASO 2 — Evaluando diseño (iteración %d)", context.iteration)

    # TODO Día 3: Implementar evaluación real
    # from pipeline.scorers.color_harmony import score_color_harmony
    # from pipeline.scorers.wcag_contrast import score_wcag_contrast
    # from pipeline.scorers.llm_scorers import (
    #     score_composition_balance, score_visual_hierarchy,
    #     score_gestalt_compliance, score_whitespace_quality,
    #     score_brand_consistency, score_accessibility
    # )

    logger.warning("PASO 2: stub — implementar en Día 3")
    return context


async def _run_algorithmic_scorers(context: DesignContext) -> dict:
    """
    Ejecuta los 2 scorers algorítmicos (color_harmony, wcag_contrast).
    Son síncronos y muy rápidos, no necesitan async.

    TODO Día 3: implementar.
    """
    # from pipeline.scorers.color_harmony import score_color_harmony
    # from pipeline.scorers.wcag_contrast import score_wcag_contrast

    # palette = [context.primary_color, context.secondary_color, context.accent_color]
    # palette = [c for c in palette if c]  # filtrar None

    # color_harmony_score = score_color_harmony(palette)
    # wcag_score = score_wcag_contrast(context)

    return {}


async def _run_llm_scorers(context: DesignContext) -> dict:
    """
    Ejecuta los 6 scorers LLM en paralelo usando asyncio.gather.
    Todos usan temperatura=0 para máxima reproducibilidad.

    Por qué asyncio.gather aquí:
    Los 6 scorers LLM son independientes entre sí. Si los ejecutamos en secuencia
    tardarían ~30 segundos (6 × 5s). En paralelo tardan ~5-8 segundos.

    TODO Día 3: implementar.
    """
    # import asyncio
    # from pipeline.scorers.llm_scorers import (...)

    # results = await asyncio.gather(
    #     score_composition_balance(context),
    #     score_visual_hierarchy(context),
    #     score_gestalt_compliance(context),
    #     score_whitespace_quality(context),
    #     score_brand_consistency(context),
    #     score_accessibility(context),
    # )
    return {}


def _generate_critique(scores: AestheticScores) -> str:
    """
    Genera un diagnóstico específico para los criterios que fallaron.
    El critique debe incluir:
    - Qué criterio falló y su puntuación actual
    - Por qué falló (explicación del modelo)
    - Qué valor específico lo resolvería

    Ejemplo de critique útil:
    "El contraste entre #3D3D3D y #4A4A4A es 1.2:1.
     WCAG exige mínimo 4.5:1. Solución: cambiar texto a #FFFFFF (contraste 15:1)"

    TODO Día 3: implementar usando las explicaciones de los scorers LLM.
    """
    failing = scores.failing_criteria()
    if not failing:
        return ""

    critique_parts = []
    for criterion in failing:
        score = getattr(scores, criterion)
        critique_parts.append(
            f"- {criterion}: {score:.1f}/100 (mínimo requerido: 85)"
        )

    return "Criterios que requieren corrección:\n" + "\n".join(critique_parts)
