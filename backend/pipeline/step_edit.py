"""
step_edit.py - Edición quirúrgica de HTML existente
=====================================================

Recibe un HTML generado por Quimera y aplica una instrucción de edición
sin regenerar el diseño desde cero. Usa Gemini Flash para velocidad.

Flujo:
  html_actual + instruccion [+ elemento_contexto] → HTML modificado
"""

import logging
from services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


EDIT_SYSTEM_PROMPT = """Eres un experto en HTML/CSS/JS. Tu única tarea es editar código HTML existente
siguiendo instrucciones precisas del usuario.

REGLAS CRÍTICAS:
1. Devuelve SOLO el HTML completo y modificado — sin explicaciones, sin markdown, sin código de bloque.
2. Mantén TODA la estructura, estilos, scripts y contenido que no se menciona en la instrucción.
3. Aplica únicamente los cambios solicitados. No "mejores" ni alteres nada más.
4. Conserva todos los atributos, clases, IDs y estilos inline existentes.
5. El HTML de salida debe ser completamente autocontenido (sin dependencias externas rotas).
6. Si se indica un elemento específico a editar, modifica SOLO ese elemento y su contenido inmediato.
"""


def _build_edit_prompt(
    html_actual: str,
    instruccion: str,
    elemento_contexto: str | None,
    design_markdown: str | None,
) -> str:
    parts = []

    if design_markdown:
        parts.append(f"## Contexto del diseño (DESIGN.md)\n{design_markdown[:2000]}\n")

    if elemento_contexto:
        parts.append(
            f"## Elemento seleccionado por el usuario\n"
            f"El usuario ha seleccionado este elemento específico del diseño:\n"
            f"```html\n{elemento_contexto[:1000]}\n```\n"
            f"Aplica la instrucción SOLO a este elemento (o a elementos equivalentes en el HTML).\n"
        )

    parts.append(f"## Instrucción del usuario\n{instruccion}\n")
    parts.append(f"## HTML actual\n{html_actual}")

    return "\n".join(parts)


async def edit_html(
    html_actual: str,
    instruccion: str,
    elemento_contexto: str | None = None,
    design_markdown: str | None = None,
) -> str:
    """
    Edita quirúrgicamente el HTML según la instrucción dada.

    Args:
        html_actual: HTML completo generado por Quimera
        instruccion: Qué cambiar (ej: "cambia el botón a rojo", "añade un footer")
        elemento_contexto: outerHTML del elemento seleccionado en el preview (opcional)
        design_markdown: DESIGN.md de referencia para contexto (opcional)

    Returns:
        HTML completo modificado
    """
    client = GeminiClient()

    prompt = _build_edit_prompt(html_actual, instruccion, elemento_contexto, design_markdown)

    logger.info(
        "Editando HTML. Instrucción: %.80s... | Elemento: %s",
        instruccion,
        "sí" if elemento_contexto else "no",
    )

    full_prompt = EDIT_SYSTEM_PROMPT + "\n\n" + prompt

    html_result = await client.generate_text(
        prompt=full_prompt,
        model="flash",
        temperature=0.2,
    )

    # Limpiar por si Gemini envuelve en markdown
    html_clean = html_result.strip()
    if html_clean.startswith("```html"):
        html_clean = html_clean[7:]
    if html_clean.startswith("```"):
        html_clean = html_clean[3:]
    if html_clean.endswith("```"):
        html_clean = html_clean[:-3]

    return html_clean.strip()
