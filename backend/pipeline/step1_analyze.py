"""
step1_analyze.py -- PASO 1: Generar DESIGN.md
==============================================
Genera un archivo DESIGN.md completo (YAML tokens + Markdown prose)
basado en el brief del usuario.

Input:  DesignContext.design_brief
Output: DesignContext.design_markdown (archivo DESIGN.md completo)

INTEGRACIÓN COMPLETA de design.md-main:
- Especificación completa de format & tokens
- PHILOSOPHY.md: Prose-first, specific references, negative constraints
- Ejemplos: Atmospheric Glass, Paws & Paths, Totality Festival
"""

import logging
from models import DesignContext
from services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


# ========================================================================
# SPECIFICATION + PHILOSOPHY (Integración completa de design.md-main)
# ========================================================================

DESIGN_MD_COMPLETE_GUIDE = """
# DESIGN.md Specification + Philosophy (Completa)

## Principio Fundamental

"The quality of a generated design is determined LESS by the precision 
of its values than by how CLEARLY THE INTENT IS DESCRIBED."

DESIGN.md captures how a design looks, feels, and behaves.
THE PROSE IS WHERE THE DESIGN LIVES.
Everything else exists to support it.

## ¿Qué es DESIGN.md?

DESIGN.md es una representación auto-contenida, legible en texto plano, 
de un sistema de diseño. Define la identidad visual de una marca y producto.

Contiene DOS partes:
1. YAML Frontmatter (máquina-legible): Design tokens estructurados
2. Markdown Body (humano-legible): Rationale, guía, filosofía

## YAML Frontmatter Schema

```yaml
---
version: alpha
name: <string>
description: <string>  # optional
colors:
  <token-name>: <Color>  # Hex: #RGB, #RRGGBB, #RRGGBBAA
  # Material Design 3 semantics: surface, on-surface, surface-container-*, error, etc.
typography:
  <token-name>:
    fontFamily: <string>
    fontSize: <Dimension>  # 12px, 16px, 1.5rem
    fontWeight: <number>  # 400, 500, 600, 700, etc.
    lineHeight: <Dimension | number>  # 1.6, 24px, 1.5rem
    letterSpacing: <Dimension>  # -0.02em, 0.05em
    # OPTIONAL: fontFeature, fontVariation
rounded:
  <scale-level>: <Dimension>  # xs, sm, DEFAULT, md, lg, xl, full
spacing:
  <scale-level>: <Dimension | number>  # base: 8px, xs, sm, md, lg, xl
components:
  <component-name>:
    backgroundColor: <Color | token reference {colors.primary}>
    textColor: <Color | token reference>
    typography: <token reference {typography.body-md}>
    rounded: <token reference {rounded.lg}>
    padding: <Dimension | token reference {spacing.md}>
    # Component variants: button-primary, button-primary-hover, button-primary-active, etc.
---
```

## Markdown Sections (en este ORDEN exacto)

1. **## Overview** (aka "Brand & Style")
   - Holistic description: look, feel, personality
   - Brand personality, target audience
   - Emotional response the UI should evoke
   - Specific reference (NOT generic adjectives)
   - Example: "A 1970s graduate lecture handout in the tradition of an old established university"
   - Example: "Glassmorphism aesthetic with ethereal yet functional personality"

2. **## Colors**
   - Color palette strategy
   - Semantic roles (primary, secondary, tertiary, neutral, surface, error, etc.)
   - Descriptive names mapped to token names
   - USAGE of each color (Material Design 3 semantics help)
   - Example: "**Primary (#855300):** Warm earthy brown evoking trust for fintech"

3. **## Typography**
   - Typography strategy: font families, hierarchy
   - Semantic categories: headline, display, body, label, caption
   - When/why each level exists
   - Treatment: weights, sizes, effects (text-shadows, etc.)
   - Example: "**Headlines:** Bold Plus Jakarta Sans for clear hierarchy"

4. **## Layout & Spacing**
   - Layout model: Fluid Grid, Fixed-Max-Width Grid, etc.
   - Spacing scale: base unit, rhythm (usually 8px)
   - Grouping principles: cards, containment, safe areas
   - Negative space philosophy
   - Example: "Fluid Grid mobile, Fixed-Max 1200px desktop, 8px base scale"

5. **## Elevation & Depth**
   - How visual hierarchy is conveyed
   - If elevation: shadows (spread, blur, color), layers
   - If flat: alternative methods (borders, color contrast, scale)
   - If glassmorphism: blur levels, alpha, transparency physics
   - If neumorphism: highlights and shadows technique
   - Example: "Tonal layers (not heavy shadows), backdrop-filter blur"

6. **## Shapes**
   - Shape language philosophy
   - Corner radius scale & rationale
   - Sharp/rounded/organic spectrum choice
   - Why that choice matters for personality
   - Example: "Rounded corners (12px) for friendly, trustworthy feel"

7. **## Components**
   - Style guidance for specific component atoms
   - Buttons: primary, secondary, tertiary variants + states (hover, active, disabled)
   - Cards: profile, featured, list items
   - Inputs: text, error state, focus state
   - Lists: structure, hover effects
   - Navigation: treatment, selected state
   - Use component token names from YAML
   - Variants should match YAML: button-primary, button-primary-hover, etc.

8. **## Do's and Don'ts**
   - 3-5 INTENTIONAL don'ts (what NOT to do)
   - 3-5 positive do's (best practices)
   - These should flow NATURALLY from the brand reference
   - Don't be generic ("don't use Comic Sans")
   - Be specific to THIS design ("don't add gradients to text")

## Filosofía Clave

### 1. PROSE > TOKENS
Tokens son CONTEXT para la prosa, NO rendering instructions.
La prosa es donde VIVE el diseño.

Correcto:
```markdown
## Colors
colors:
  paper: '#F4F0E4'
  ink: '#1E1A14'

A single-ink-plus-accent system.
- **Paper** {colors.paper} is the canvas — warmed xerox stock, never pure white.
- **Ink** {colors.ink} carries all typography and diagrams; never pure black.
```

### 2. SPECIFIC REFERENCE > GENERIC ADJECTIVES
"A 1970s graduate lecture handout in the tradition of an old and established university"
→ evoca un mundo COMPLETO

❌ "Modern, clean, trustworthy, premium"
→ genérico, sin punto de referencia

La especificidad trae implícitamente:
- Márgenes generosos
- Tipografía serif en tamaño lectura
- Ausencia de decoración
- NO glows, NO gradients, NO rounded corners
- Densidad informativa

### 3. NEGATIVE CONSTRAINTS (Lo que dejas fuera define el carácter)
Un buen reference AUTOMÁTICAMENTE define qué NO hacer:
- Si dices "1970s handout" → el modelo sabe que NO tiene blur o gradients
- Si dices "glassmorphism" → el modelo sabe que SÍ tiene transparency y blur
- No necesitas listar todo. Naming the object names the constraints.

Un intentional list de Do's & Don'ts es útil CUANDO la descripción es específica.

## Ejemplos Reales de design.md-main

### Ejemplo 1: Atmospheric Glass
- Glassmorphism aesthetic: "ethereal yet functional"
- Dark theme (Deep Blue #0b1326 background)
- White text with alpha channels (transparency)
- Material Design 3 semantics (surface, on-surface, etc.)
- Typography: Inter (neutral geometric clarity)
- Elevation: blur levels (20px standard, 40px elevated)
- Shapes: organic & approachable (rounded-xl 24px for buttons)
- Components: glass-card-standard, glass-card-elevated, button-primary, input-field
- Do's: Use frosted glass physics, maintain white border, apply subtle shadows
- Don'ts: No solid backgrounds, no heavy shadows, preserve transparency

### Ejemplo 2: Paws & Paths
- "Joyful energy of a walk + reliability of premium service"
- Modern Corporate + friendly, human-centric
- Warm palette: Golden Retriever orange primary (#855300), Sky Walk blue secondary
- Typography: Plus Jakarta Sans (friendly, rounded terminals)
- Layout: Fixed Grid 4-column mobile-first
- Elevation: Ambient Shadows (diffused, soft, mixed with color)
- Shapes: Rounded (12px buttons, 24px cards) for safe & friendly feel
- Components: button-primary, card-profile, card-walk-stat, badge-status
- Do's: Use generous whitespace, subtle lifts on hover, soft shadows
- Don'ts: No heavy borders, no crude grays in shadows, no clutter

### Ejemplo 3: Totality Festival
- Dark theme, high-contrast colors
- Primary: pale yellow (#fff6df), Secondary: cyan (#00daf3)
- Space Grotesk (geometric, futuristic)
- Material Design 3 full semantic palette
- Festival aesthetic: vibrant, energetic

## Material Design 3 Semantic Colors

Cuando aplica (especialmente en Material Design 3):
- primary: Main accent color for interactive elements
- on-primary: Color for elements ON the primary background
- primary-container: Container for primary-related content
- on-primary-container: Text/elements on primary-container
- secondary, tertiary, error: Additional semantic colors
- surface: Main background color
- on-surface: Text/elements on surface
- surface-container-lowest, -low, (base), -high, -highest: Tonal layers
- outline, outline-variant: Borders, dividers
- background: Page background (usually same as surface)
- on-background: Text on background

Material Design 3 permite JERARQUÍA DE TONO sin necesidad de shadows.

## Token References

Dentro de YAML components y prose, usar sintaxis {{path.to.token}}:
- {{colors.primary}} → referencia a colors.primary
- {{typography.body-md}} → referencia a typography.body-md
- {{spacing.md}} → referencia a spacing.md
- {{rounded.lg}} → referencia a rounded.lg

TODO token referenciado DEBE existir en el YAML.
TODO token definido en YAML DEBE ser usado o mencionado en prose.

## Validación

✅ YAML válido (indentación 2-espacios, estructura correcta)
✅ Todas las secciones markdown ##
✅ Referencias {{token}} existen en YAML
✅ Sin adjectives genéricos sin detalles
✅ Prose explica intentión de cada decisión
✅ Do's & Don'ts son específicos a ESTE diseño
✅ Colores en formato #HEX válido
✅ Tipografía: fontFamily, fontSize, fontWeight, lineHeight, letterSpacing
✅ Material Design 3 semantics o naming coherente
✅ Component variants con -hover, -active, -disabled si aplica
"""


SYSTEM_PROMPT = f"""Eres Gemini, experto en architecture de design systems profesionales.

Tu misión CRÍTICA: Generar un DESIGN.md EXCEPCIONAL que implemente 
COMPLETAMENTE la filosofía y especificación de design.md-main.

{DESIGN_MD_COMPLETE_GUIDE}

## Metodología de Generación:

### PASO 1: Extrae Intención del Brief
- ¿Tipo de proyecto? (app, web, dashboard, landing, etc.)
- ¿Industria? (fintech, healthcare, saas, etc.)
- ¿Audiencia objetivo? (edad, seniority, contexto)
- ¿Tono emocional? (profesional vs playful, premium vs accessible, etc.)

### PASO 2: Define UNA Referencia Visual Específica
NO HAGAS: "moderno, limpio, minimalista, profesional"
HAZ: Una referencia CONCRETA que evoque un mundo completo

Ejemplos:
✅ "1970s graduate lecture handout in the tradition of an old university"
✅ "Glassmorphism weather dashboard with ethereal premium feel"
✅ "Pet walking app with friendly corporate warmth and organic shapes"

### PASO 3: Diseña Paleta de Colores
- 5-7 colores principales (primary, secondary, tertiary, surface, error, etc.)
- Material Design 3 semantics donde sea apropiado
- CADA COLOR tiene razón de ser en la prosa
- Verifica WCAG AA (4.5:1 contraste mínimo para texto)

### PASO 4: Selecciona Tipografía
- 1-2 familias (Inter, Plus Jakarta Sans, Public Sans, Space Grotesk, Roboto, etc.)
- 6-8 niveles tipográficos semánticos
- Cada uno: fontFamily, fontSize, fontWeight, lineHeight, letterSpacing
- Explica LA INTENCIÓN de cada nivel

### PASO 5: Define Espaciado & Layout
- Base unit (típicamente 8px)
- Escala: xs, sm, md, lg, xl (y custom si es necesario)
- Modelo de layout (Fluid Grid, Fixed-Max-Width, etc.)
- Filosofía de negative space

### PASO 6: Estrategia de Profundidad
- Glassmorphism: blur levels, alpha, borders, light refraction
- Flat + Tonal: layers sin shadows
- Neumorphism: soft highlights y shadows
- Material Design 3: tonal surface containers
- Define EXACTAMENTE cómo convey jerarquía visual

### PASO 7: Lenguaje de Formas
- Escala de border-radius (sm, DEFAULT, md, lg, xl, full)
- Filosofía: sharp (tech), rounded (friendly), organic (natural)
- Aplica coherentemente a buttons, cards, inputs

### PASO 8: Componentes Específicos
MÍNIMO:
- button-primary, button-primary-hover, button-primary-active
- button-secondary, button-secondary-hover
- card-default
- input-field, input-field-focus, input-field-error
- link, link-hover

ADICIONAL (si aplica):
- badge-*, list-item-*, modal-*, toast-*, etc.

Todas las propiedades usan token references: {{colors.primary}}, {{typography.body-md}}, {{spacing.md}}

### PASO 9: Do's & Don'ts Intencionados
3-5 Don'ts específicos a ESTE diseño (NO genéricos)
3-5 Do's positivos que refuerzan la identidad
Deben FLUIR naturalmente de la referencia específica

## Output Exacto:

SOLO el archivo DESIGN.md completo:
- Primera línea: ---
- YAML válido, bien indentado
- Secciones markdown ## en orden exacto
- Última línea: final de ## Do's & Don'ts
- SIN explicaciones, SIN code blocks, SIN meta-comentarios
- UTF-8 válido
"""


async def analyze_and_design(context: DesignContext) -> DesignContext:
    """
    PASO 1: Generar DESIGN.md EXCEPCIONAL.
    
    Integra COMPLETAMENTE:
    - Especificación formal de DESIGN.md format
    - Filosofía de design.md-main (Prose > Tokens, Specific > Generic)
    - Ejemplos reales (Atmospheric Glass, Paws & Paths, Totality Festival)
    - Material Design 3 semantics
    - Negative constraints pattern

    Args:
        context: DesignContext con design_brief y project_type opcional

    Returns:
        DesignContext actualizado con design_markdown (DESIGN.md completo)
    """
    logger.info("🎨 PASO 1: Generando DESIGN.md excepcional para: %s...", 
                context.design_brief[:80])

    try:
        client = GeminiClient()

        project_type_line = f"\n\nTipo de Proyecto: {context.project_type}" if context.project_type else ""
        
        user_prompt = f"""Tu misión FINAL: Generar un DESIGN.md EXCEPCIONAL y HERMOSO.

BRIEF DEL USUARIO:
---
{context.design_brief}{project_type_line}
---

INSTRUCCIONES CRÍTICAS:

1. REFERENCE ESPECÍFICA (NO ADJECTIVES GENÉRICOS)
   MALO: "Modern and clean design"
   BUENO: "Glassmorphic dark UI evoking ethereal premium experience"
   
   La referencia DEBE:
   - Evocar un mundo visual completo
   - Traer implícitamente qué SÍ y qué NO incluir
   - Justificar cada decisión de color, tipografía, espaciado

2. PROSA ES EL CORAZÓN
   Prosa > Tokens en importancia
   
   Prosa explica:
   - POR QUÉ se eligió cada color (no solo hex)
   - INTENCIÓN de cada nivel tipográfico
   - FILOSOFÍA de espaciado y negativ space
   - EMOCIÓN que genera cada elección

3. COLORES CON RAZÓN
   - 5-7 colores (primary, secondary, tertiary, surface, error, etc.)
   - Cada color: "**Name (#HEX):** Descripción específica + uso"
   - Verifica WCAG AA (4.5:1) para texto
   - Material Design 3 semantics si aplica (surface-container-*, on-surface, etc.)

4. TIPOGRAFÍA ESTRATÉGICA
   - 1-2 familias (específicas: Inter, Plus Jakarta Sans, etc.)
   - 6-8 niveles semánticos (display, headline-lg, headline-md, body-lg, body-md, label-md, label-sm)
   - Cada uno: fontFamily, fontSize, fontWeight, lineHeight, letterSpacing
   - Explica intención de pesos y tamaños

5. ESPACIADO CONSISTENTE
   - Base: 8px (estándar)
   - Escala: xs (4px), sm (8px), md (16px), lg (32px), xl (64px)
   - Modelo: Fluid Grid, Fixed-Max-Width, etc.
   - Filosofía: negative space generosa, breathing room

6. PROFUNDIDAD & ELEVACIÓN
   - Si glassmorphism: blur (20px/40px), alpha (0.1/0.2), borders blancos
   - Si flat: tonal layers (Material Design 3), sin shadows
   - Si neumorphism: soft highlights + shadows
   - Define EXACTAMENTE cómo convey jerarquía

7. FORMAS & BORDER-RADIUS
   - Escala: sm (0.25rem), DEFAULT (0.5rem), md (0.75rem), lg (1rem), xl (1.5rem), full (9999px)
   - Filosofía: ¿sharp para tech? ¿rounded para friendly? ¿organic para natural?

8. COMPONENTES REALES
   - MÍNIMO: button-primary + hover, button-secondary + hover, card, input-field
   - ADICIONAL (si aplica): badge, list-item, modal, toast
   - Propiedades: backgroundColor, textColor, typography, rounded, padding
   - USA token references: {{colors.primary}}, {{typography.body-md}}, {{spacing.md}}
   - Todos los tokens referenciados DEBEN existir en YAML

9. DO'S & DON'TS INTENCIONADOS
   - 3-5 Don'ts específicos a ESTE diseño (NO genéricos como "don't use Comic Sans")
   - 3-5 Do's positivos que refuerzan identidad
   - Fluyen NATURALMENTE de la referencia específica
   
   Ejemplo BUENO (Technical Handout):
   - Don't: "Add a hero moment to the title page. A real handout is first page of content."
   - Do: "Treat as a printed object. The screen is the substrate."
   
   Ejemplo MALO:
   - Don't: "Don't use too many colors"
   - (Vago, no específico)

10. VALIDACIÓN FINAL
    ✅ YAML válido (indentación 2 espacios)
    ✅ Todos los colores #HEX válido
    ✅ Tipografía: fontFamily, fontSize, fontWeight, lineHeight, letterSpacing
    ✅ Material Design 3 semantics (surface-container-*, on-surface, etc.) si aplica
    ✅ Referencias {{token}} existen en YAML
    ✅ Componentes con variantes: -primary, -hover, -active, -disabled si aplica
    ✅ Prosa explica INTENCIÓN, no solo valores
    ✅ Do's & Don'ts específicos a ESTE diseño
    ✅ Markdown válido (headings, listas, texto)
    ✅ No has genéricos: "modern", "clean", "premium" SIN detalles

ENTREGA: SOLO el DESIGN.md desde --- hasta el final.
Nada de explicación, nada de markdown code blocks (```), nada de meta-comentarios.
Hazlo HERMOSO, PROFESIONAL y ESPECÍFICO. Este es el OUTPUT FINAL.
"""

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        design_markdown = await client.generate_text(
            prompt=full_prompt,
            model="pro",
            temperature=0.7,
        )

        context.design_markdown = design_markdown
        logger.info("✅ DESIGN.md generado: %d caracteres, %d líneas",
                   len(design_markdown),
                   design_markdown.count('\n'))

        return context

    except Exception as e:
        logger.error("❌ Error en PASO 1: %s", str(e))
        raise
