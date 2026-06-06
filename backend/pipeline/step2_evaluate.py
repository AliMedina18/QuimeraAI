"""
step2_evaluate.py -- PASO 2: Motor de Evaluacion Estetica
=========================================================
Responsabilidad: Evaluar la propuesta de diseno del Paso 1 en 8 criterios.
Si el score < 85, generar un diagnostico y activar el loop de correccion.

Inputs:  context con todos los campos de diseno del Paso 1
Outputs: context con aesthetic_scores, overall_score, approved, critique

Los 8 criterios:
  Algoritmicos (deterministas):
    1. color_harmony    <- score_color_harmony()    en scorers/color_harmony.py
    2. wcag_contrast    <- score_wcag_contrast()    en scorers/wcag_contrast.py

  LLM (temperatura=0, Gemini 2.5 Pro):
    3. composition_balance  <- score_composition_balance()
    4. visual_hierarchy     <- score_visual_hierarchy()
    5. gestalt_compliance   <- score_gestalt_compliance()
    6. whitespace_quality   <- score_whitespace_quality()
    7. brand_consistency    <- score_brand_consistency()
    8. accessibility        <- score_accessibility()
"""

import asyncio
import logging
from models import DesignContext, AestheticScores
from services.gemini_client import GeminiClient
from pipeline.scorers.color_harmony import score_color_harmony
from pipeline.scorers.wcag_contrast import score_wcag_contrast
from pipeline.scorers.llm_scorers import (
    score_composition_balance,
    score_visual_hierarchy,
    score_gestalt_compliance,
    score_whitespace_quality,
    score_brand_consistency,
    score_accessibility,
)

logger = logging.getLogger(__name__)

APPROVAL_THRESHOLD = 85.0
MAX_ITERATIONS = 3


async def aesthetic_evaluate(context: DesignContext) -> DesignContext:
    """
    PASO 2: Ejecuta los 8 scorers y decide si el diseno pasa o necesita correccion.

    Flujo:
        1. Scorers algoritmicos: color_harmony y wcag_contrast (sincrono, rapido)
        2. Scorers LLM: 6 scorers en paralelo con asyncio.gather (temperatura=0)
        3. overall_score = promedio de los 8
        4. Si overall_score >= 85: context.approved = True
        5. Si overall_score < 85 e iteration < 3: generar critique especifico
        6. Si iteration >= 3: aprobar con el mejor resultado disponible

    Args:
        context: DesignContext con propuesta de diseno del Paso 1.

    Returns:
        context con aesthetic_scores, overall_score, approved, critique actualizados.
    """
    logger.info("PASO 2 -- Evaluando diseno (iteracion %d)", context.iteration)

    # --- Scorers algoritmicos (deterministas, rapidos) ---
    algo_scores = _run_algorithmic_scorers(context)

    # --- Scorers LLM (en paralelo para minimizar latencia) ---
    client = GeminiClient()
    llm_scores, llm_explanations = await _run_llm_scorers(context, client)

    # --- Construir AestheticScores ---
    scores = AestheticScores(
        color_harmony=algo_scores["color_harmony"],
        wcag_contrast=algo_scores["wcag_contrast"],
        composition_balance=llm_scores["composition_balance"],
        visual_hierarchy=llm_scores["visual_hierarchy"],
        gestalt_compliance=llm_scores["gestalt_compliance"],
        whitespace_quality=llm_scores["whitespace_quality"],
        brand_consistency=llm_scores["brand_consistency"],
        accessibility=llm_scores["accessibility"],
        iteration=context.iteration + 1,
    )

    overall = scores.overall_score
    logger.info(
        "PASO 2 completo. Overall: %.1f | Aprobado: %s | Criterios fallidos: %s",
        overall, scores.passed, scores.failing_criteria()
    )

    # --- Actualizar context ---
    context.aesthetic_scores = scores.to_dict()
    context.overall_score = overall
    context.iteration += 1

    if scores.passed:
        context.approved = True
        context.critique = None
        logger.info("Diseno APROBADO con score %.1f", overall)
    elif context.iteration >= MAX_ITERATIONS:
        context.approved = True  # Aprobar tras max iteraciones con lo mejor disponible
        context.critique = None
        logger.warning(
            "Maximo de iteraciones alcanzado (%d). Aprobando con score %.1f",
            MAX_ITERATIONS, overall
        )
    else:
        context.approved = False
        context.critique = _generate_critique(scores, llm_explanations)
        logger.info("Diseno RECHAZADO. Generando critique para iteracion %d",
                    context.iteration + 1)

    return context


def _run_algorithmic_scorers(context: DesignContext) -> dict:
    """
    Ejecuta los 2 scorers algoritmicos: color_harmony y wcag_contrast.
    Son sincronos y rapidos (no necesitan llamadas externas).
    """
    palette = [
        c for c in [
            context.primary_color,
            context.secondary_color,
            context.accent_color,
        ] if c
    ]

    color_harmony = score_color_harmony(palette)
    wcag = score_wcag_contrast(context)

    logger.info("Scorers algoritmicos: color_harmony=%.1f wcag_contrast=%.1f",
                color_harmony, wcag)
    return {
        "color_harmony": color_harmony,
        "wcag_contrast": wcag,
    }


async def _run_llm_scorers(context: DesignContext, client: GeminiClient) -> tuple[dict, dict]:
    """
    Ejecuta los 6 scorers LLM en paralelo con asyncio.gather.

    Por que asyncio.gather:
    Cada scorer llama a Gemini (~5-8s). En secuencia serian ~40s.
    En paralelo tardan ~8-10s (el tiempo del scorer mas lento).

    Retorna (scores_dict, explanations_dict).
    """
    results = await asyncio.gather(
        score_composition_balance(context, client),
        score_visual_hierarchy(context, client),
        score_gestalt_compliance(context, client),
        score_whitespace_quality(context, client),
        score_brand_consistency(context, client),
        score_accessibility(context, client),
        return_exceptions=True,
    )

    names = [
        "composition_balance",
        "visual_hierarchy",
        "gestalt_compliance",
        "whitespace_quality",
        "brand_consistency",
        "accessibility",
    ]

    scores = {}
    explanations = {}

    for name, result in zip(names, results):
        if isinstance(result, Exception):
            logger.error("Scorer %s fallo: %s", name, result)
            scores[name] = 75.0  # fallback neutral
            explanations[name] = f"Error: {result}"
        else:
            score, explanation = result
            scores[name] = score
            explanations[name] = explanation
            logger.info("Scorer %s: %.1f", name, score)

    return scores, explanations


def _generate_critique(scores: AestheticScores, explanations: dict) -> str:
    """
    Genera un diagnostico especifico para los criterios que fallaron.
    Incluye: que criterio fallo, su score, y que valor lo resolveria.

    El critique es el input del Paso 1 en la siguiente iteracion.
    Gemini lo lee y corrige especificamente los puntos debiles.
    """
    failing = scores.failing_criteria()
    if not failing:
        return ""

    lines = [
        f"Score global: {scores.overall_score:.1f}/100 (umbral: 85.0)",
        f"Iteracion: {scores.iteration}",
        "",
        "Criterios que requieren correccion:",
    ]

    for criterion in failing:
        score = getattr(scores, criterion)
        explanation = explanations.get(criterion, "Sin explicacion disponible")
        lines.append(f"- {criterion}: {score:.1f}/100 -- {explanation}")

    lines += [
        "",
        "Instruccion para la siguiente iteracion:",
        "Revisa y corrige ESPECIFICAMENTE los criterios listados arriba.",
        "Mantén los criterios que ya pasaron (score >= 85).",
    ]

    return "\n".join(lines)
