"""
step3_generate.py — PASO 3: Generación de código
=================================================
Responsabilidad: Con el diseño aprobado, generar:
  1. Componente React funcional + TypeScript + Tailwind CSS
  2. Design tokens como variables CSS
  3. Documento Markdown con el rationale de cada decisión

REGLA CRÍTICA: Este paso NO puede inventar valores.
Solo puede usar colores, tipografías y espaciados que estén en el DesignContext aprobado.
Si el prompt intenta introducir un valor nuevo, se rechaza.

Inputs:  context.approved == True (obligatorio)
         Todos los campos de diseño del DesignContext
Outputs: context.react_component
         context.design_tokens_css
         context.rationale_document

Este archivo se implementa completamente en el Día 4.
"""

import logging
from models import DesignContext, GeneratedOutput

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt del Paso 3 — Ver Sección 7.3 del plan maestro
# ---------------------------------------------------------------------------
GENERATE_SYSTEM_PROMPT = """
Genera un componente React funcional usando EXACTAMENTE los valores aprobados
en el DesignContext.

REGLAS ESTRICTAS:
1. No puedes introducir valores de color que no estén en el DesignContext.
2. No puedes introducir tipografías que no estén en heading_font o body_font.
3. No puedes introducir espaciados arbitrarios: usa solo las clases de Tailwind.
4. TypeScript strict mode. Sin CSS personalizado inline.
5. El componente debe ser self-contained y renderizable en un iframe sandbox.

Genera tres outputs separados en este JSON:
{
  "react_component": "// código TypeScript completo",
  "design_tokens_css": "/* variables CSS */",
  "rationale_document": "# Markdown con decisiones"
}
"""


async def generate_code(context: DesignContext) -> DesignContext:
    """
    PASO 3: Genera el código a partir del diseño aprobado.

    Precondición: context.approved == True
    Si se llama con approved == False, lanza un ValueError.

    Args:
        context: DesignContext con approved=True y todos los campos de diseño.

    Returns:
        context con react_component, design_tokens_css, rationale_document completados.

    TODO Día 4:
        1. Verificar que context.approved == True
        2. Construir el prompt con todos los valores del DesignContext
        3. Llamar a GeminiClient.generate_json_with_retry(prompt, model="flash", temperature=0.4)
        4. Extraer react_component, design_tokens_css, rationale_document del JSON
        5. Validar sintaxis del React generado (llamar a Node con @babel/parser)
        6. Si sintaxis inválida: pedir corrección automática una vez más
        7. Si persiste: usar template base fallback
        8. Guardar en Firestore + Cloud Storage
    """
    if not context.approved:
        raise ValueError(
            "El Paso 3 solo se ejecuta con diseños aprobados (context.approved == True). "
            f"Overall score actual: {context.overall_score}"
        )

    logger.info("PASO 3 — Generando código para diseño aprobado (score: %s)", context.overall_score)

    # TODO Día 4: Implementar generación real
    # client = GeminiClient()
    # prompt = _build_generate_prompt(context)
    # output = await client.generate_json_with_retry(prompt, model="flash", temperature=0.4)
    # context = _apply_output_to_context(context, output)

    logger.warning("PASO 3: stub — implementar en Día 4")
    return context


def _build_generate_prompt(context: DesignContext) -> str:
    """
    Construye el prompt para la generación de código.
    Incluye todos los valores aprobados del DesignContext explícitamente.

    TODO Día 4: implementar.
    """
    return f"""
{GENERATE_SYSTEM_PROMPT}

DesignContext aprobado:
- project_type: {context.project_type}
- industry: {context.industry}
- target_audience: {context.target_audience}
- brand_personality: {', '.join(context.brand_personality)}
- primary_color: {context.primary_color}
- secondary_color: {context.secondary_color}
- accent_color: {context.accent_color}
- neutral_palette: {context.neutral_palette}
- heading_font: {context.heading_font}
- body_font: {context.body_font}
- layout_type: {context.layout_type}
- composition_rule: {context.composition_rule}
- color_harmony_type: {context.color_harmony_type}
- overall_score: {context.overall_score}/100

Brief original: {context.design_brief}
"""


async def _validate_react_syntax(component_code: str) -> bool:
    """
    Valida que el componente React generado tiene sintaxis TypeScript válida.
    Usa @babel/parser desde Node.js (llamada de subproceso).

    TODO Día 4: implementar usando asyncio.create_subprocess_exec
    """
    # import asyncio
    # proc = await asyncio.create_subprocess_exec(
    #     "node", "-e",
    #     f"require('@babel/parser').parse(`{component_code}`, {{sourceType:'module', plugins:['typescript','jsx']}})",
    #     stdout=asyncio.subprocess.PIPE,
    #     stderr=asyncio.subprocess.PIPE,
    # )
    # _, stderr = await proc.communicate()
    # return proc.returncode == 0
    return True  # placeholder
