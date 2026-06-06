"""
step3_generate.py -- PASO 3: Generacion de codigo React
========================================================
Responsabilidad: Con el diseno aprobado, generar:
  1. Componente React funcional + TypeScript + Tailwind CSS
  2. Design tokens como variables CSS
  3. Documento Markdown con el rationale de cada decision

REGLA CRITICA: Este paso NO puede inventar valores.
Solo usa colores, tipografias y espaciados del DesignContext aprobado.

Inputs:  context.approved == True (obligatorio)
         Todos los campos de diseno del DesignContext
Outputs: context.react_component    -- codigo TSX completo
         context.design_tokens_css  -- variables CSS
         context.rationale_document -- markdown con decisiones

Modelo: gemini-2.5-flash (mas rapido y barato que pro, suficiente para generacion)
"""

import asyncio
import logging
import os
import tempfile

from models import DesignContext
from services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Delimitadores para parsear la respuesta de Gemini
# Se usan delimitadores en vez de JSON para evitar escaping de codigo
# ---------------------------------------------------------------------------
_D_REACT = "===REACT_COMPONENT==="
_D_CSS   = "===DESIGN_TOKENS_CSS==="
_D_MD    = "===RATIONALE==="
_D_END   = "===END==="

GENERATE_SYSTEM_PROMPT = """Eres un desarrollador React senior especializado en sistemas de diseno.
Tu tarea es generar un componente React completo a partir de un diseno aprobado.

REGLAS ESTRICTAS:
1. Usa EXACTAMENTE los colores hex del DesignContext. No inventes colores.
   Usa CSS variables: var(--color-primary), var(--color-secondary), etc.
2. Usa EXACTAMENTE las fuentes del DesignContext. No inventes fuentes.
3. Usa Tailwind para layout y espaciado. Usa CSS variables para colores y fuentes.
4. TypeScript: componente funcional con React.FC. Sin props requeridos.
5. Auto-contenido: incluye Google Fonts @import dentro del CSS tokens.
6. Componente completo: navbar + hero + seccion de features + CTA + footer.
7. Responsivo: usa clases Tailwind md: para 2 breakpoints.
8. Accesible: aria-labels en botones y links, roles semanticos.

IMPORTANTE: Responde UNICAMENTE con el siguiente formato exacto, incluyendo los delimitadores:

===REACT_COMPONENT===
[codigo TypeScript React completo aqui]
===DESIGN_TOKENS_CSS===
[variables CSS y Google Fonts import aqui]
===RATIONALE===
[documento Markdown con justificacion de cada decision]
===END===

Sin texto adicional fuera de los delimitadores."""


async def generate_code(context: DesignContext) -> DesignContext:
    """
    PASO 3: Genera el codigo a partir del diseno aprobado.

    Flujo:
        1. Verificar context.approved == True
        2. Construir prompt con todos los valores del DesignContext
        3. Llamar a Gemini Flash (temperatura=0.4, mas creativo que los scorers)
        4. Parsear respuesta con delimitadores
        5. Validar sintaxis JSX con Babel/Node
        6. Si invalido: pedir correccion una vez mas
        7. Si persiste: usar template base fallback
        8. Guardar resultado en context

    Args:
        context: DesignContext con approved=True y todos los campos de diseno.

    Returns:
        context con react_component, design_tokens_css, rationale_document completados.

    Raises:
        ValueError: Si context.approved es False.
    """
    if not context.approved:
        raise ValueError(
            f"El Paso 3 solo se ejecuta con disenos aprobados. "
            f"overall_score actual: {context.overall_score}"
        )

    logger.info("PASO 3 -- Generando codigo (score aprobado: %.1f, iteraciones: %d)",
                context.overall_score or 0, context.iteration)

    client = GeminiClient()
    prompt = _build_generate_prompt(context)

    try:
        raw = await client.generate_with_retry(
            prompt=prompt,
            model="flash",
            temperature=0.4,
            max_retries=3,
        )
        sections = _parse_code_output(raw)
    except Exception as e:
        logger.error("Gemini fallo en Paso 3: %s", e)
        sections = {}

    react_component = sections.get("react_component", "")
    design_tokens_css = sections.get("design_tokens_css", "")
    rationale_document = sections.get("rationale_document", "")

    # Validar sintaxis JSX del componente generado
    if react_component:
        is_valid = await _validate_react_syntax(react_component)
        if not is_valid:
            logger.warning("Sintaxis JSX invalida. Pidiendo correccion a Gemini...")
            fix_prompt = _build_fix_prompt(react_component, context)
            try:
                fixed_raw = await client.generate_with_retry(
                    prompt=fix_prompt,
                    model="flash",
                    temperature=0.2,
                    max_retries=2,
                )
                fixed_sections = _parse_code_output(fixed_raw)
                fixed_component = fixed_sections.get("react_component", "")
                fixed_is_valid = await _validate_react_syntax(fixed_component) if fixed_component else False
                if fixed_is_valid:
                    react_component = fixed_component
                    logger.info("Correccion exitosa: componente reparado")
                else:
                    logger.warning("Correccion fallo. Usando template fallback.")
                    react_component = _get_fallback_component(context)
            except Exception as e:
                logger.error("Error en correccion: %s. Usando fallback.", e)
                react_component = _get_fallback_component(context)
    else:
        logger.warning("Gemini no genero componente. Usando template fallback.")
        react_component = _get_fallback_component(context)

    if not design_tokens_css:
        design_tokens_css = _get_fallback_tokens(context)

    if not rationale_document:
        rationale_document = _get_fallback_rationale(context)

    context.react_component = react_component
    context.design_tokens_css = design_tokens_css
    context.rationale_document = rationale_document

    logger.info("PASO 3 completo. Componente: %d chars | Tokens: %d chars",
                len(react_component), len(design_tokens_css))
    return context


def _build_generate_prompt(context: DesignContext) -> str:
    """Construye el prompt completo con todos los valores del DesignContext aprobado."""
    neutral_str = ", ".join(context.neutral_palette) if context.neutral_palette else "#FFFFFF, #F8FAFC, #64748B, #1E293B"
    personality_str = ", ".join(context.brand_personality) if context.brand_personality else "profesional"

    # Mapear layout_type a descripcion de estructura
    layout_descriptions = {
        "hero_centered":  "hero centrado + grid de features + CTA + footer",
        "sidebar_left":   "sidebar de navegacion izquierdo + contenido principal a la derecha",
        "grid_cards":     "navbar + grid de tarjetas + paginacion + footer",
        "full_width":     "secciones full-width apiladas: hero, features, testimonios, CTA",
        "split_screen":   "pantalla dividida 50/50: lado izquierdo texto, lado derecho visual",
    }
    layout_desc = layout_descriptions.get(context.layout_type or "", "hero + features + CTA")

    return f"""{GENERATE_SYSTEM_PROMPT}

DISENO APROBADO (score: {context.overall_score}/100):

Proyecto: {context.project_type} | Industria: {context.industry}
Audiencia: {context.target_audience}
Personalidad de marca: {personality_str}

COLORES (usa EXACTAMENTE estos valores):
--color-primary:    {context.primary_color}
--color-secondary:  {context.secondary_color}
--color-accent:     {context.accent_color}
--color-neutral-50: {context.neutral_palette[0] if context.neutral_palette else '#FFFFFF'}
--color-neutral-100:{context.neutral_palette[1] if len(context.neutral_palette) > 1 else '#F8FAFC'}
--color-neutral-600:{context.neutral_palette[2] if len(context.neutral_palette) > 2 else '#64748B'}
--color-neutral-900:{context.neutral_palette[3] if len(context.neutral_palette) > 3 else '#1E293B'}

TIPOGRAFIA (usa EXACTAMENTE estas fuentes):
--font-heading: '{context.heading_font}', sans-serif
--font-body:    '{context.body_font}', sans-serif

LAYOUT: {context.layout_type} -- estructura: {layout_desc}
REGLA COMPOSITIVA: {context.composition_rule}
ARMONIA CROMATICA: {context.color_harmony_type}

BRIEF ORIGINAL: {context.design_brief[:300]}

Genera el componente AHORA siguiendo el formato de delimitadores."""


def _build_fix_prompt(invalid_component: str, context: DesignContext) -> str:
    """Prompt para pedir a Gemini que corrija el componente con error de sintaxis."""
    return f"""{GENERATE_SYSTEM_PROMPT}

El siguiente componente React tiene un error de sintaxis. Corrígelo manteniendo exactamente
los mismos colores y fuentes del diseno aprobado:

COLORES:
--color-primary: {context.primary_color}
--color-accent:  {context.accent_color}
--font-heading:  '{context.heading_font}'
--font-body:     '{context.body_font}'

COMPONENTE CON ERROR:
{invalid_component[:3000]}

Genera la version corregida con el formato de delimitadores."""


def _parse_code_output(text: str) -> dict:
    """
    Parsea la respuesta de Gemini extrayendo las 3 secciones por delimitadores.

    Retorna dict con claves: react_component, design_tokens_css, rationale_document.
    Cualquier seccion no encontrada retorna string vacio.
    """
    result = {
        "react_component": "",
        "design_tokens_css": "",
        "rationale_document": "",
    }

    sections = [
        ("react_component",    _D_REACT, _D_CSS),
        ("design_tokens_css",  _D_CSS,   _D_MD),
        ("rationale_document", _D_MD,    _D_END),
    ]

    for key, start_delim, end_delim in sections:
        if start_delim in text and end_delim in text:
            try:
                content = text.split(start_delim, 1)[1].split(end_delim, 1)[0].strip()
                # Gemini a veces envuelve el codigo en fences de markdown (```tsx, ```css).
                # Los eliminamos para que el frontend pueda usar el codigo directamente.
                if content.startswith("```"):
                    lines = content.split("\n")
                    lines = lines[1:]  # eliminar primera linea (```tsx, ```python, etc.)
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]  # eliminar cierre ```
                    content = "\n".join(lines).strip()
                result[key] = content
            except (IndexError, ValueError):
                logger.warning("No se pudo extraer seccion %s del output", key)

    return result


async def _validate_react_syntax(component_code: str) -> bool:
    """
    Valida que el componente React tiene sintaxis TypeScript/JSX valida.
    Usa @babel/parser via Node.js (subprocess).

    Si Node no esta disponible, usa validacion Python basica como fallback.
    Siempre retorna True o False (nunca lanza excepcion).
    """
    # Intento 1: validacion con Babel/Node
    try:
        script_path = os.path.join(os.path.dirname(__file__), "..", "validate_jsx.js")
        script_path = os.path.normpath(script_path)

        if os.path.exists(script_path):
            proc = await asyncio.create_subprocess_exec(
                "node", script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(
                proc.communicate(input=component_code.encode("utf-8")),
                timeout=10.0,
            )
            if proc.returncode != 0:
                logger.warning("Babel encontro error: %s", stderr.decode()[:300])
            return proc.returncode == 0
    except asyncio.TimeoutError:
        logger.warning("Validacion Babel timeout. Usando validacion Python.")
    except FileNotFoundError:
        logger.info("Node.js no disponible. Usando validacion Python.")
    except Exception as e:
        logger.warning("Error en validacion Babel: %s(%s)", type(e).__name__, e)

    # Fallback: validacion Python basica
    return _basic_python_validation(component_code)


def _basic_python_validation(code: str) -> bool:
    """
    Validacion Python basica de un componente React.
    Verifica las senales minimas de un componente valido.
    """
    checks = [
        "export default" in code,
        "return" in code,
        ("React.FC" in code or "(): " in code or "() =>" in code),
        code.count("{") >= code.count("}") - 2,  # braces roughly balanced
    ]
    return all(checks)


def _get_fallback_component(context: DesignContext) -> str:
    """
    Template React funcional minimo que siempre es valido.
    Usa los colores del context directamente como inline styles.
    Activa cuando Gemini genera codigo con errores de sintaxis.
    """
    primary = context.primary_color or "#1E40AF"
    accent   = context.accent_color  or "#F59E0B"
    neutral_bg  = context.neutral_palette[0] if context.neutral_palette else "#FFFFFF"
    neutral_txt = context.neutral_palette[-1] if context.neutral_palette else "#1E293B"
    neutral_sub = context.neutral_palette[2] if len(context.neutral_palette) > 2 else "#64748B"
    font_h = context.heading_font or "Inter"
    font_b = context.body_font    or "Inter"
    project_type = context.project_type or "proyecto"
    industry     = context.industry     or ""

    return f"""import React from 'react';

interface QuimeraDesignProps {{}}

const QuimeraDesign: React.FC<QuimeraDesignProps> = () => {{
  return (
    <div style={{{{ minHeight: '100vh', backgroundColor: '{neutral_bg}', fontFamily: "'{font_b}', sans-serif" }}}}>
      {{/* Navigation */}}
      <nav style={{{{ backgroundColor: '{primary}', padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}}}>
        <span style={{{{ color: 'white', fontFamily: "'{font_h}', sans-serif", fontSize: '1.25rem', fontWeight: '700' }}}}>
          Quimera
        </span>
        <button
          aria-label="Comenzar ahora"
          style={{{{ backgroundColor: '{accent}', color: '{neutral_txt}', padding: '0.5rem 1.25rem', borderRadius: '0.5rem', border: 'none', fontWeight: '600', cursor: 'pointer' }}}}
        >
          Comenzar
        </button>
      </nav>

      {{/* Hero */}}
      <section style={{{{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '5rem 2rem', textAlign: 'center' }}}}>
        <h1 style={{{{ fontFamily: "'{font_h}', sans-serif", fontSize: '3rem', fontWeight: '700', color: '{neutral_txt}', marginBottom: '1.5rem', maxWidth: '700px' }}}}>
          {industry.capitalize() if industry else 'Tu solución digital'} — Diseñado por Quimera AI
        </h1>
        <p style={{{{ fontSize: '1.125rem', color: '{neutral_sub}', marginBottom: '2.5rem', maxWidth: '500px', lineHeight: '1.75' }}}}>
          {context.design_brief[:120] if context.design_brief else 'Descripcion del proyecto.'}
        </p>
        <button
          aria-label="Empezar gratis"
          style={{{{ backgroundColor: '{primary}', color: 'white', padding: '1rem 2.5rem', borderRadius: '0.75rem', border: 'none', fontSize: '1.125rem', fontWeight: '600', cursor: 'pointer' }}}}
        >
          Empezar gratis
        </button>
      </section>

      {{/* Features */}}
      <section style={{{{ padding: '4rem 2rem', maxWidth: '960px', margin: '0 auto' }}}}>
        <div style={{{{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '2rem' }}}}>
          {{['Calidad', 'Velocidad', 'Confianza'].map((feature, i) => (
            <div key={{i}} style={{{{ backgroundColor: 'white', border: `1px solid ${{'{neutral_bg}'}}`, borderRadius: '0.75rem', padding: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}}}>
              <h3 style={{{{ color: '{primary}', fontFamily: "'{font_h}', sans-serif", fontWeight: '600', marginBottom: '0.75rem' }}}}>{{feature}}</h3>
              <p style={{{{ color: '{neutral_sub}', fontSize: '0.9rem', lineHeight: '1.6' }}}}>
                Funcionalidad clave para tu {project_type}.
              </p>
            </div>
          ))}}
        </div>
      </section>
    </div>
  );
}};

export default QuimeraDesign;"""


def _get_fallback_tokens(context: DesignContext) -> str:
    """Genera design tokens CSS desde el context cuando Gemini no los produce."""
    neutral = context.neutral_palette or ["#FFFFFF", "#F8FAFC", "#64748B", "#1E293B"]
    font_h = context.heading_font or "Inter"
    font_b = context.body_font    or "Inter"

    # Extraer familia base para Google Fonts (eliminar weights como "Inter Bold")
    google_h = font_h.split()[0] if font_h else "Inter"
    google_b = font_b.split()[0] if font_b else "Inter"
    fonts_to_import = list(dict.fromkeys([google_h, google_b]))  # dedup preservando orden
    gf_query = "+".join(f.replace(" ", "+") for f in fonts_to_import)

    return f"""@import url('https://fonts.googleapis.com/css2?family={gf_query}:wght@300;400;500;600;700&display=swap');

:root {{
  /* --- Colores de marca --- */
  --color-primary:    {context.primary_color or '#1E40AF'};
  --color-secondary:  {context.secondary_color or '#3B82F6'};
  --color-accent:     {context.accent_color or '#F59E0B'};

  /* --- Paleta neutral --- */
  --color-neutral-50:  {neutral[0] if len(neutral) > 0 else '#FFFFFF'};
  --color-neutral-100: {neutral[1] if len(neutral) > 1 else '#F8FAFC'};
  --color-neutral-600: {neutral[2] if len(neutral) > 2 else '#64748B'};
  --color-neutral-900: {neutral[3] if len(neutral) > 3 else '#1E293B'};

  /* --- Tipografia --- */
  --font-heading: '{font_h}', sans-serif;
  --font-body:    '{font_b}', sans-serif;

  /* --- Espaciado --- */
  --spacing-xs:  4px;
  --spacing-sm:  8px;
  --spacing-md:  16px;
  --spacing-lg:  32px;
  --spacing-xl:  64px;
  --spacing-2xl: 128px;

  /* --- Border radius --- */
  --radius-sm:  4px;
  --radius-md:  8px;
  --radius-lg:  16px;
  --radius-xl:  24px;
  --radius-full: 9999px;

  /* --- Sombras --- */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.06);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05);
}}"""


def _get_fallback_rationale(context: DesignContext) -> str:
    """Genera documento de rationale desde el context."""
    return f"""# Rationale de Diseno — Quimera AI

## Resumen
Diseno generado automaticamente para: **{context.design_brief[:200]}**
Score estetico aprobado: **{context.overall_score}/100** en {context.iteration} iteracion(es).

## Paleta de colores
- **Primario ({context.primary_color})**: Color principal de la marca. Justificacion: {context.design_rationale.get('primary_color', {}).get('razon', 'Elegido por el Motor de Evaluacion Estetica.')}
- **Secundario ({context.secondary_color})**: Complemento del primario. Armonia: {context.color_harmony_type}.
- **Acento ({context.accent_color})**: CTA y elementos de atencion. Contraste alto sobre fondos claros.

## Tipografia
- **Titulos ({context.heading_font})**: {context.design_rationale.get('heading_font', {}).get('razon', 'Seleccionada por legibilidad y caracter de marca.')}
- **Cuerpo ({context.body_font})**: {context.design_rationale.get('body_font', {}).get('razon', 'Optima para lectura en pantalla.')}

## Layout y composicion
- **Layout**: {context.layout_type} — apropiado para {context.project_type} en {context.industry}.
- **Regla compositiva**: {context.composition_rule}.
- **Armonia cromatica**: {context.color_harmony_type} (OKLCH validado).

## Accesibilidad
- Contraste WCAG 2.1 evaluado por el Motor de Evaluacion Estetica.
- Score general: {context.overall_score}/100 (umbral: 85/100).
"""
