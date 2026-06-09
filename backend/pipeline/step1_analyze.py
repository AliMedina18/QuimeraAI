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
from services.design_templates import get_templates_manager

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


DESIGN_MD_REAL_EXAMPLES = """
## EJEMPLO REAL 1: Airbnb (Marketplace Premium)

---
version: alpha
name: Airbnb-design-analysis
description: A warm, generous consumer marketplace anchored on a clean white canvas and Airbnb Rausch (#ff385c), the single brand voltage that carries every primary CTA, search-button orb, and rating dot. Type runs Airbnb Cereal VF at modest weights — display sits at 22–28px in weight 500/600 rather than the heavy 700+ that fintech and enterprise systems use; the brand trusts photography and generous whitespace over typographic muscle. Pill-shaped search bars (`{rounded.full}`), softly rounded property cards (`{rounded.lg}` ~14px), and 32px button radii read as friendly and human.

colors:
  primary: "#ff385c"
  primary-active: "#e00b41"
  primary-disabled: "#ffd1da"
  ink: "#222222"
  body: "#3f3f3f"
  muted: "#6a6a6a"
  canvas: "#ffffff"
  surface-soft: "#f7f7f7"
  surface-strong: "#f2f2f2"
  on-primary: "#ffffff"

typography:
  display-xl:
    fontFamily: "'Airbnb Cereal VF', Circular, sans-serif"
    fontSize: 28px
    fontWeight: 700
    lineHeight: 1.43
    letterSpacing: 0
  display-lg:
    fontFamily: "'Airbnb Cereal VF', Circular, sans-serif"
    fontSize: 22px
    fontWeight: 500
    lineHeight: 1.18
  body-md:
    fontFamily: "'Airbnb Cereal VF', Circular, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: "'Airbnb Cereal VF', Circular, sans-serif"
    fontSize: 14px
    fontWeight: 500

rounded:
  xs: 4px
  sm: 8px
  md: 14px
  lg: 20px
  full: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 12px
  base: 16px
  lg: 24px
  xl: 32px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button-md}"
    rounded: "{rounded.sm}"
    padding: 14px 24px
    height: 48px
  button-primary-active:
    backgroundColor: "{colors.primary-active}"
    textColor: "{colors.on-primary}"
  card-property:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: 12px
---

## EJEMPLO REAL 2: Figma (Editorial + Pastel)

---
version: alpha
name: Figma-design-analysis
description: "A confident black-and-white editorial frame interrupted by oversized, hand-cut pastel color blocks. The marketing canvas is rigorously monochrome — figmaSans variable type, pure white surfaces, pure black ink, pill-shaped CTAs — while each story section drops the page into a saturated lime, lavender, cream, mint, or pink panel that reads like a sticky note placed on a clean desk. Technical AND joyful."

colors:
  primary: "#000000"
  on-primary: "#ffffff"
  ink: "#000000"
  canvas: "#ffffff"
  block-lime: "#dceeb1"
  block-lilac: "#c5b0f4"
  block-cream: "#f4ecd6"
  block-pink: "#efd4d4"
  block-mint: "#c8e6cd"
  accent-magenta: "#ff3d8b"
  semantic-success: "#1ea64a"

typography:
  display-xl:
    fontFamily: figmaSans
    fontSize: 86px
    fontWeight: 340
    lineHeight: 1.00
    letterSpacing: -1.72px
  headline:
    fontFamily: figmaSans
    fontSize: 26px
    fontWeight: 540
    lineHeight: 1.35
  body:
    fontFamily: figmaSans
    fontSize: 18px
    fontWeight: 320
    lineHeight: 1.45
  caption:
    fontFamily: figmaMono
    fontSize: 12px
    fontWeight: 400

rounded:
  sm: 6px
  md: 8px
  lg: 24px
  pill: 50px

spacing:
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.pill}"
    padding: 10px 20px
  button-magenta-promo:
    backgroundColor: "{colors.accent-magenta}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.pill}"
---

## EJEMPLO REAL 3: Stripe (Fintech Premium)

---
version: alpha
name: Stripe-design-analysis
description: A financial-infrastructure brand built on a deep navy ink, an electric indigo primary, and recurring atmospheric gradient meshes. The system pairs Sohne at thin (300) weights with negative letter-spacing for editorial-density display headlines, and uses tabular-figure body type where money and numerics matter. Buttons are tight-radius pills, cards live on near-white surfaces, and the dashboard flips to a familiar dark-app shell.

colors:
  primary: "#533afd"
  primary-deep: "#4434d4"
  primary-press: "#2e2b8c"
  primary-soft: "#665efd"
  ink: "#0d253d"
  ink-secondary: "#273951"
  ink-mute: "#64748d"
  on-primary: "#ffffff"
  canvas: "#ffffff"
  canvas-soft: "#f6f9fc"
  ruby: "#ea2261"

typography:
  display-xxl:
    fontFamily: "sohne-var, 'SF Pro Display', sans-serif"
    fontSize: 56px
    fontWeight: 300
    lineHeight: 1.03
    letterSpacing: -1.4px
  display-lg:
    fontFamily: "sohne-var, 'SF Pro Display', sans-serif"
    fontSize: 32px
    fontWeight: 300
    lineHeight: 1.1
  heading-lg:
    fontFamily: "sohne-var, 'SF Pro Display', sans-serif"
    fontSize: 22px
    fontWeight: 300
  body-lg:
    fontFamily: "sohne-var, 'SF Pro Display', sans-serif"
    fontSize: 16px
    fontWeight: 300
    lineHeight: 1.4
  caption:
    fontFamily: "sohne-var, 'SF Pro Display', sans-serif"
    fontSize: 13px
    fontWeight: 400

rounded:
  xs: 4px
  sm: 6px
  md: 8px
  lg: 12px
  pill: 9999px

spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px

components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.pill}"
  button-primary-hover:
    backgroundColor: "{colors.primary-deep}"
    textColor: "{colors.on-primary}"
---
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

## EJEMPLOS REALES DE DESIGN.MD EXCELENTES

Estos son 3 ejemplos reales de empresas premium. ESTUDIA su estructura YAML, 
la variedad de colores, los niveles tipográficos, cómo definen componentes:

{DESIGN_MD_REAL_EXAMPLES}

**Puntos clave de estos ejemplos:**
1. Airbnb: Paleta cálida de 10+ colores, tipografía friendly, shapes redondeadas
2. Figma: Blanco + negro + pastel blocks vibrantes, jerarquía tipográfica clara
3. Stripe: Navy + Indigo eléctrico, thin weights, paleta sofisticada, financial feel

CUANDO GENERES, PRODUCE UN DESIGN.MD CON LA MISMA CALIDAD Y DETALLE.
No hagas paletas de 2-3 colores. Haz paletas de 8-12 con roles semánticos claros.
No hagas 2-3 niveles tipográficos. Haz 6-8 con intención clara en cada uno.

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
    PASO 1: Generar DESIGN.md EXCEPCIONAL (MEJORADO v3).
    
    NUEVO:
    - Utiliza template_analysis del Step 0 (patrones de composición, tipografía, colores)
    - Inyecta patrones inteligentes extraídos de templates reales
    - Usa Color Science para validar contraste WCAG
    - Recomienda tipografía sistemática basada en industria

    Args:
        context: DesignContext con design_brief, template_analysis, etc.

    Returns:
        DesignContext actualizado con design_markdown (DESIGN.md completo)
    """
    logger.info("🎨 PASO 1 v3: Generando DESIGN.md mejorado para: %s...", 
                context.design_brief[:80])

    try:
        client = GeminiClient()
        templates_manager = get_templates_manager()
        
        from services.typography_analyzer import get_typography_analyzer
        from services.color_science import get_color_science
        
        typo_analyzer = get_typography_analyzer()
        color_science = get_color_science()

        project_type_line = f"\n\nTipo de Proyecto: {context.project_type}" if context.project_type else ""
        
        # NUEVA FEATURE: Inyectar análisis de templates inteligente
        template_patterns_context = ""
        if context.template_analysis and context.template_analysis.patterns:
            analysis = context.template_analysis
            logger.info("✓ Usando patrones de %d templates", len(analysis.patterns))
            
            # Extraer y formatear patrones
            pattern_summaries = []
            for template_name, pattern in analysis.patterns.items():
                pattern_summaries.append(f"""
### {template_name}
- **Composición:** {pattern.composition}
- **Tipografía:** {', '.join(list(pattern.typography.values())[:2])} (+ más niveles)
- **Colores:** {pattern.colors_strategy}
- **Paleta Sample:** {', '.join([f'{k}={v}' for k,v in list(pattern.colors_sample.items())[:3]])}
- **Responsive:** {pattern.responsive_strategy}
- **Elevación:** {pattern.elevation_strategy}
- **Border Radius:** {pattern.corner_radius_philosophy}
""")
            
            template_patterns_context = f"""
## ANÁLISIS INTELIGENTE DE TEMPLATES RELEVANTES

Se han identificado y analizado {len(analysis.patterns)} templates relevantes
para tu industria ({analysis.industry or 'general'}).

**Estrategia:** {analysis.design_strategy_summary}

Estos templates sirven como REFERENCIA DE COMPOSICIÓN, TIPOGRAFÍA Y COLORES:

{''.join(pattern_summaries)}

**INSTRUCCIÓN CRÍTICA:** Usa estos patrones como inspiración para estructura y coherencia.
No copies directamente, pero SI adopta su filosofía de:
- Jerarquía visual clara
- Tipografía sistemática
- Paleta armónica
- Responsive design profesional
""" 
        
        # NUEVA FEATURE: Recomendación tipográfica
        typo_rec = typo_analyzer.recommend_pairing(
            industry=context.template_analysis.industry if context.template_analysis else None
        )
        
        typo_context = f"""
## RECOMENDACIÓN TIPOGRÁFICA SISTEMÁTICA

Basándose en la industria, se recomienda el pairing: **{typo_rec['pairing']}**
({typo_rec['description']})

Jerarquía sugerida:
- **Headline:** {typo_rec['headline']['font']} {typo_rec['headline']['size']}px w{typo_rec['headline']['weight']}
- **Display:** {typo_rec['display']['font']} {typo_rec['display']['size']}px w{typo_rec['display']['weight']}
- **Body:** {typo_rec['body']['font']} {typo_rec['body']['size']}px w{typo_rec['body']['weight']}
- **Caption:** {typo_rec['caption']['font']} {typo_rec['caption']['size']}px w{typo_rec['caption']['weight']}
"""
        
        # Si el usuario especificó una referencia, inyectar ese DESIGN.md real
        reference_context = ""
        if context.design_reference:
            template = templates_manager.get_template(context.design_reference)
            if template:
                logger.info("✓ Template de referencia inyectado: %s", context.design_reference)
                reference_context = f"""
## TEMPLATE DE REFERENCIA ESPECÍFICA

El usuario ha solicitado que generes algo INSPIRADO en este DESIGN.md real:

{template}

---

INSTRUCCIÓN CRÍTICA: Usa este template como REFERENCIA DE ESTRUCTURA Y CALIDAD.
No copies directamente. Toma los principios de:
- Variedad de colores (≥5 colores con roles semánticos)
- Niveles tipográficos variados (≥6 niveles)
- Componentes bien definidos con variantes
- Prosa que explica INTENCIÓN, no solo valores
"""
        
        user_prompt = f"""Tu misión FINAL: Generar un DESIGN.md EXCEPCIONAL, HERMOSO, y FUNDAMENTADO.

BRIEF DEL USUARIO:
---
{context.design_brief}{project_type_line}
---

{template_patterns_context}

{typo_context}

{reference_context}

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

3. PALETA DE COLORES PREMIUM Y COHERENTE — ESTO ES CRÍTICO
   
   MÍNIMO 5-8 colores con roles semánticos:
   - primary: Color hero del diseño
   - secondary: Complemento armónico
   - tertiary: Acentos y detalles
   - surface/canvas: Fondos neutros
   - error: Estados de error
   - Additional: Según tema (success, warning, info, etc.)
   
   NO hagas: "usar azul porque es corporativo"
   HAZ: Análisis profundo del tema + psicología del color
   
   a) ANALIZA el tema/brief:
      - ¿Industria? (restaurante, fintech, SaaS, lifestyle, etc.)
      - ¿Emoción deseada? (lujo, confianza, energía, serenidad, etc.)
      - ¿Inspiraciones visuales reales? (natural, industrial, retro, moderno, etc.)
      - ¿Audiencia? (profesionales, jóvenes, premium, accesible, etc.)
   
   b) ELIGE primario + secundario + acentos:
      - Primary: El color HERO que domina (debe comunicar la esencia)
      - Secondary: Complemento armónico (contrasta pero combina)
      - Tertiary: Acentos y detalles (añade profundidad)
      - Surface/Background: Lo neutro que deja que los colores brillen
      - Error: Rojo significativo, NO genérico
   
   c) FILOSOFÍA DE PALETA:
      - Monocromática + acentos: elegante, minimalista
      - Análoga: armoniosa, natural
      - Complementaria: energética, premium
      - Tonal: sofisticado, moderno
   
   d) VERIFICA:
      - WCAG AA contrast 4.5:1 mínimo para texto
      - Harmonía OKLCH (no solo HEX visualmente agradable)
      - Coherencia cultural (ej: gris en Japón ≠ gris en tech)
      - Premium vs accesible balance
   
   e) EJEMPLOS DE PALETAS HERMOSAS POR TEMA:
      
      Restaurante Premium/Sushi:
      - Primary: #1a1a1a (negro carbón) o #8B2E2E (rojo profundo)
      - Secondary: #D4AF37 (oro sutil) o #F5E6D3 (marfil cálido)
      - Tertiary: #2C3E50 (azul profundo) o #C41E3A (rojo japonés)
      - Surface: #FAFAFA (blanco roto) o #1F1F1F (negro soft)
      
      SaaS Fintech/Moderno:
      - Primary: #0066FF (azul confianza) o #00D9FF (cyan energético)
      - Secondary: #6C5CE7 (púrpura premium) o #FF6B6B (rojo vivo)
      - Surface: #F7F9FC (azul muy pálido) o #FFFFFF (blanco puro)
      
      Lifestyle/Wellness:
      - Primary: #2D5016 (verde natural) o #D4A574 (tierra cálida)
      - Secondary: #E8D4C4 (nude suave) o #8B6F47 (marrón noble)
      - Tertiary: #6FA876 (verde claro) o #FFB347 (naranja cálido)
      
      Tech/Startup:
      - Primary: #FF0080 (magenta) o #00B4D8 (azul vibrante)
      - Secondary: #7C3AED (púrpura) o #EC4899 (rosa)
      - Surface: #0F172A (navy muy oscuro) o #FFFFFF (blanco absoluto)
   
   f) ESCRIBE LA PROSA CON RAZÓN:
      "**Primary (#8B2E2E):** Rojo profundo japonés, evoca tradición, lujo, frescura del sushi. 
       Suficientemente oscuro para mantener legibilidad (WCAG AA verified)."
       
      "**Secondary (#D4AF37):** Oro sutil, detalles nobles sin ser ostentoso. 
       En restaurante premium señala calidad, detalles finos, experiencia exclusiva."
   
   RECUERDA: La paleta define la EMOCIÓN del diseño. 
   Colores genéricos = diseño genérico.
   Colores pensados = identidad visual memorable.

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

⚠️ ADVERTENCIA FINAL SOBRE COLORES:
Los colores son lo más importante. NO uses paletas genéricas. 
Cada color debe tener RAZÓN DE SER específica al tema.
Una paleta mediocre = diseño mediocre.
Una paleta excelente = diseño memorable.

Hazlo HERMOSO, PROFESIONAL, ESPECÍFICO y con COLORES EXCEPCIONALES.
Este es el OUTPUT FINAL.
"""

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        # use_search=True: Gemini busca en Google para encontrar referencias
        # reales de diseño, sitios de competencia, tendencias visuales del sector.
        design_markdown = await client.generate_text(
            prompt=full_prompt,
            model="pro",
            temperature=0.85,
            use_search=True,
        )

        context.design_markdown = design_markdown
        logger.info("✅ DESIGN.md generado: %d caracteres, %d líneas",
                   len(design_markdown),
                   design_markdown.count('\n'))

        return context

    except Exception as e:
        logger.error("\u274c Error en PASO 1: %s", str(e))
        raise
