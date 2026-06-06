"""
llm_scorers.py -- Criterios 3-8: Scorers via Gemini (temperatura=0)
===================================================================
6 scorers que evaluan aspectos de diseno que requieren percepcion visual y
juicio contextual. Todos usan Gemini 2.5 Pro con temperatura=0 para maxima
reproducibilidad.

Por que temperatura=0 para los scorers:
  Los scorers deben ser DETERMINISTAS: dado el mismo diseno, siempre dan
  el mismo resultado. Temperatura=0 elimina la aleatoriedad del LLM.

Criterio 3 -- Balance compositivo    (Regla de tercios, Golden Ratio)
Criterio 4 -- Jerarquia visual       (Escala 1.25x, patron F/Z)
Criterio 5 -- Cumplimiento Gestalt   (Proximidad, Similitud, Continuidad)
Criterio 6 -- Calidad espacio negativo (>=30% viewport libre)
Criterio 7 -- Consistencia de marca  (Coherencia con brand_personality)
Criterio 8 -- Accesibilidad general  (No solo color, tamanos minimos)

Cada scorer retorna (score: float, explanation: str) para que el critique
del loop de correccion pueda decir exactamente que fallo.
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SCORER_BASE = """Eres un auditor de diseno visual experto. Evalua con maxima objetividad.

REGLAS:
1. Score EXACTO de 0 a 100 (entero o un decimal).
2. Reproducible: mismo diseno = mismo score siempre.
3. Justificacion en 2 lineas: que esta bien y que falla.
4. Si score < 85, indica el valor exacto que resolveria el problema.

Diseno a evaluar:
{design_summary}

Criterio: {criterio}

Responde UNICAMENTE con este JSON exacto:
{{"score": <0-100>, "justification": "<2 lineas>", "fix": "<valor especifico o null>"}}"""


def _build_design_summary(context) -> str:
    """Serializa DesignContext a texto para el prompt del scorer."""
    neutrales = ", ".join(context.neutral_palette) if context.neutral_palette else "no definida"
    personalidad = ", ".join(context.brand_personality) if context.brand_personality else "no definida"
    return (
        f"Proyecto: {context.project_type} | Industria: {context.industry}\n"
        f"Audiencia: {context.target_audience}\n"
        f"Personalidad de marca: {personalidad}\n"
        f"Color primario: {context.primary_color} | Secundario: {context.secondary_color} | Acento: {context.accent_color}\n"
        f"Paleta neutral: {neutrales}\n"
        f"Tipografia titulos: {context.heading_font} | Cuerpo: {context.body_font}\n"
        f"Layout: {context.layout_type} | Regla compositiva: {context.composition_rule}\n"
        f"Armonia cromatica: {context.color_harmony_type}\n"
        f"Brief original: {context.design_brief[:200]}"
    )


async def _call_scorer(client, criterio: str, design_summary: str) -> tuple[float, str, Optional[str]]:
    """
    Llama a Gemini con temperatura=0 y parsea la respuesta del scorer.
    Retorna (score, justification, fix).
    """
    prompt = SCORER_BASE.format(
        design_summary=design_summary,
        criterio=criterio,
    )
    try:
        result = await client.generate_json_with_retry(
            prompt=prompt,
            model="pro",
            temperature=0.0,
            max_retries=2,
        )
        score = float(result.get("score", 75.0))
        score = max(0.0, min(100.0, score))
        justification = result.get("justification", "")
        fix = result.get("fix")
        return (score, justification, fix)
    except Exception as e:
        logger.error("Error en scorer LLM: %s", e)
        return (75.0, f"Error al evaluar: {e}", None)


async def score_composition_balance(context, client) -> tuple[float, str]:
    """
    Criterio 3: Balance compositivo.
    Regla de tercios, Golden Ratio (1.618), simetria/asimetria intencional.
    """
    criterio = (
        "BALANCE COMPOSITIVO: Evalua si el peso visual esta distribuido equilibradamente. "
        "Criterios: (1) Regla de los tercios: elementos clave en intersecciones de la cuadricula 3x3. "
        "(2) Golden Ratio: proporciones 1:1.618 entre secciones. "
        "(3) Simetria coherente con el layout elegido. "
        "Layout hero_centered implica simetria vertical. Sidebar implica asimetria intencional. "
        "Score 90-100: perfectamente balanceado. 70-89: balance aceptable con mejoras menores. "
        "50-69: desbalance notable. <50: composicion caotica."
    )
    score, justification, fix = await _call_scorer(client, criterio, _build_design_summary(context))
    if fix:
        justification += f" Fix: {fix}"
    return (score, justification)


async def score_visual_hierarchy(context, client) -> tuple[float, str]:
    """
    Criterio 4: Jerarquia visual.
    Escala minima 1.25x, contraste tonal, patron de lectura F o Z.
    """
    criterio = (
        "JERARQUIA VISUAL: Evalua si el sistema tipografico y de color crea una jerarquia clara. "
        "Criterios: (1) Escala: heading >= 1.25x el tamano del body. "
        "(2) El color de acento guia la atencion al CTA principal. "
        "(3) El layout sigue patron de lectura F (dashboard/listas) o Z (landing/hero). "
        "(4) El contraste entre heading y body es visualmente distinguible. "
        "Score 90-100: jerarquia cristalina. 70-89: jerarquia funcional. <70: confuso."
    )
    score, justification, fix = await _call_scorer(client, criterio, _build_design_summary(context))
    if fix:
        justification += f" Fix: {fix}"
    return (score, justification)


async def score_gestalt_compliance(context, client) -> tuple[float, str]:
    """
    Criterio 5: Cumplimiento de leyes Gestalt.
    Proximidad, Similitud, Continuidad, Figura/Fondo.
    """
    criterio = (
        "LEYES DE GESTALT: Evalua si la propuesta cumple los principios de percepcion visual. "
        "Criterios: (1) Proximidad: elementos relacionados agrupados visualmente. "
        "(2) Similitud: elementos del mismo tipo tienen mismo estilo (color, tamano, fuente). "
        "(3) Continuidad: el flujo de lectura sigue una direccion clara sin interrupciones. "
        "(4) Figura/Fondo: clara distincion entre contenido principal y fondo. "
        "La paleta neutral debe funcionar como fondo sin competir con el contenido. "
        "Score 90-100: gestalt perfecto. 70-89: principios respetados. <70: confusion visual."
    )
    score, justification, fix = await _call_scorer(client, criterio, _build_design_summary(context))
    if fix:
        justification += f" Fix: {fix}"
    return (score, justification)


async def score_whitespace_quality(context, client) -> tuple[float, str]:
    """
    Criterio 6: Calidad del espacio negativo.
    Minimo 30% del viewport libre, margenes coherentes.
    """
    criterio = (
        "ESPACIO NEGATIVO (WHITESPACE): Evalua si el diseno usa el espacio vacio intencionalmente. "
        "Criterios: (1) Al menos 30% del viewport debe ser espacio negativo. "
        "(2) Margenes consistentes entre secciones. "
        "(3) El layout elegido es compatible con buen uso de whitespace "
        "(hero_centered y full_width favorecen whitespace generoso). "
        "(4) La paleta neutral apoya visualmente el espacio vacio. "
        "Score 90-100: whitespace elegante y funcional. 70-89: adecuado. <70: diseno abarrotado."
    )
    score, justification, fix = await _call_scorer(client, criterio, _build_design_summary(context))
    if fix:
        justification += f" Fix: {fix}"
    return (score, justification)


async def score_brand_consistency(context, client) -> tuple[float, str]:
    """
    Criterio 7: Consistencia de marca.
    Coherencia entre propuesta visual y brand_personality del brief.
    """
    criterio = (
        "CONSISTENCIA DE MARCA: Evalua si la propuesta visual es coherente con la identidad de marca. "
        "Criterios: (1) Los colores reflejan la personalidad de marca declarada. "
        "(2) La tipografia tiene el caracter correcto para la industria y audiencia. "
        "(3) El layout y composicion son apropiados para el tipo de proyecto. "
        "(4) El tono visual coincide con las expectativas de la audiencia objetivo. "
        "Ejemplo: fintech para jovenes debe ser moderno y confiable, no conservador. "
        "Score 90-100: coherencia total. 70-89: mayormente coherente. <70: desconexion marca/visual."
    )
    score, justification, fix = await _call_scorer(client, criterio, _build_design_summary(context))
    if fix:
        justification += f" Fix: {fix}"
    return (score, justification)


async def score_accessibility(context, client) -> tuple[float, str]:
    """
    Criterio 8: Accesibilidad general.
    Mas alla del contraste: no depender solo del color, tamanos minimos.
    """
    criterio = (
        "ACCESIBILIDAD GENERAL: Evalua si el diseno es inclusivo mas alla del contraste WCAG. "
        "Criterios: (1) No se depende unicamente del color para transmitir informacion critica "
        "(considerar daltonismo: rojo/verde problematicos sin patron adicional). "
        "(2) Tamano de fuente body >= 16px equivalente (fuentes legibles en pantalla). "
        "(3) La paleta de colores es distinguible para los tipos comunes de daltonismo. "
        "(4) El layout tiene suficiente espaciado para areas de toque (>=44x44px movil). "
        "Score 90-100: completamente accesible. 70-89: accesible con mejoras menores. <70: barreras de acceso."
    )
    score, justification, fix = await _call_scorer(client, criterio, _build_design_summary(context))
    if fix:
        justification += f" Fix: {fix}"
    return (score, justification)
