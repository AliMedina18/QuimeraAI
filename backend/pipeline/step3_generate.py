"""
step3_generate.py -- PASO 2: Generar HTML completo desde DESIGN.md
==================================================================

Lee el DESIGN.md generado en Paso 1 e implementa un archivo HTML
autocontenido que demuestra profesionalmente TODO el sistema de diseño.

Enfoque HTML (como Google Stitch):
  - HTML + CSS inline + JavaScript vanilla
  - Tailwind CDN para utilities de layout
  - Google Fonts para tipografía exacta
  - Sin React, sin transpilación, sin dependencias externas complejas
  - El iframe solo necesita srcDoc={html} — funciona instantáneo

Input:  DesignContext.design_markdown (DESIGN.md completo)
Output: DesignContext.html_output (HTML autocontenido y funcional)

Gemini Flash: Generación rápida, código limpio, implementación fiel
"""

import logging
import re
from models import DesignContext
from services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Eres un experto en HTML, CSS y diseño visual. Tu tarea es generar un archivo HTML COMPLETO y AUTOCONTENIDO que implemente fielmente un sistema de diseño descrito en un DESIGN.md.

## Reglas absolutas del output

1. **SOLO HTML** — Devuelve ÚNICAMENTE el código HTML, sin explicaciones, sin bloques de código markdown (no uses ``` antes ni después), sin comentarios fuera del HTML.
2. **Empieza con** `<!DOCTYPE html>` — primera línea del output.
3. **Termina con** `</html>` — última línea del output.
4. **Autocontenido** — todo CSS y JS va inline en el mismo archivo. No hay imports externos de JS frameworks (React, Vue, etc.).

## Estructura del HTML

```
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Nombre del proyecto]</title>

  <!-- Google Fonts: usa exactamente las fuentes del DESIGN.md -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">

  <!-- Tailwind CDN: solo para utilities de layout (grid, flex, responsive) -->
  <script src="https://cdn.tailwindcss.com"></script>

  <style>
    /* CSS Variables desde el DESIGN.md */
    :root {
      --color-primary: #...;
      --color-secondary: #...;
      /* Todos los tokens del YAML */
    }

    /* Reset y base */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: var(--font-body); color: var(--color-text); background: var(--color-background); }

    /* Estilos de componentes — implementar CADA componente del DESIGN.md */
    .btn-primary { ... }
    .btn-secondary { ... }
    .card { ... }
    /* etc. */
  </style>
</head>
<body>
  <!-- Navbar -->
  <nav>...</nav>

  <!-- Hero -->
  <section class="hero">...</section>

  <!-- Features (3-4 cards mostrando la paleta) -->
  <section class="features">...</section>

  <!-- Components Showcase -->
  <section class="showcase">
    <!-- Buttons, Cards, Inputs, Typography, Colors -->
  </section>

  <!-- CTA -->
  <section class="cta">...</section>

  <!-- Footer -->
  <footer>...</footer>

  <script>
    /* JS vanilla MÍNIMO: solo para interacciones reales (hover states, toggle, etc.) */
    /* Si no hay JS necesario, omitir el bloque script */
  </script>
</body>
</html>
```

## Implementación fiel del DESIGN.md

### 1. CSS Variables desde el YAML
Extrae TODOS los tokens del frontmatter YAML y defínelos como CSS custom properties en `:root`.

```css
:root {
  /* Colors */
  --color-primary: #1a73e8;
  --color-primary-hover: #1557b0;
  /* ... todos los colores */

  /* Typography */
  --font-display: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
  --fs-display-lg: 3.5rem;
  --fw-display-lg: 700;
  --lh-display-lg: 1.1;
  /* ... */

  /* Spacing */
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  /* ... */

  /* Rounded */
  --rounded-sm: 4px;
  --rounded-md: 8px;
  --rounded-lg: 16px;
  /* ... */
}
```

### 2. Componentes CSS exactos
Para cada componente definido en DESIGN.md, escribe CSS exacto:

```css
.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-on-primary);
  border-radius: var(--rounded-md);
  padding: var(--space-sm) var(--space-lg);
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 1rem;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}
.btn-primary:hover {
  background-color: var(--color-primary-hover);
}
```

### 3. Glassmorphism (si aplica)
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}
```

### 4. Efectos visuales
- Gradientes → `background: linear-gradient(...)` exacto
- Sombras → `box-shadow: ...` exacto del DESIGN.md
- Animaciones → `@keyframes` + `animation` en CSS, sin JS
- Hover states → pseudo-clase `:hover` en CSS

### 5. Responsividad
Usa Tailwind para grid/flex/responsive. Para breakpoints custom usa media queries CSS.

### 6. Google Fonts
Incluye SOLO las fuentes mencionadas en el DESIGN.md. Usa el link de Google Fonts correcto.

## Sections obligatorias del HTML

1. **Navbar** — Logo + navegación + CTA button (si aplica)
2. **Hero** — Headline principal, subtítulo, CTA primario. Grande e impactante.
3. **Features** — 3-4 cards que muestren la paleta de colores y tipografía
4. **Components Showcase** — Grid que demuestra todos los componentes del DESIGN.md:
   - Buttons (primary, secondary, hover states)
   - Cards (normal, featured)
   - Inputs (normal, focus, error)
   - Typography scale (display, headline, body, label)
   - Color palette (swatches de todos los colores)
5. **CTA Section** — Llamada a acción final
6. **Footer** — Links, copyright

## Calidad del código

- HTML semántico: `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`
- ARIA labels donde sea apropiado
- Imágenes → usa `background-color` o gradientes, no `<img>` con URLs externas
- Iconos → usa emojis Unicode o SVG inline (no font-awesome, no externos)
- Sin console.log en producción
- CSS limpio: clases descriptivas, sin IDs innecesarios
"""


async def generate_code(context: DesignContext) -> DesignContext:
    """
    PASO 2: Generar HTML completo autocontenido desde DESIGN.md.

    Genera un archivo HTML que implementa fielmente TODOS los tokens,
    componentes y decisiones del DESIGN.md. Es el output visual final
    que el usuario ve en el iframe de preview.

    Enfoque HTML (como Google Stitch): sin React, sin transpilación,
    funciona directamente con <iframe srcDoc={html}>.

    Args:
        context: DesignContext con design_markdown (DESIGN.md completo)

    Returns:
        context actualizado con html_output (HTML autocontenido)
    """
    if not context.design_markdown:
        raise ValueError("❌ DESIGN.md no encontrado en el contexto")

    logger.info("🌐 PASO 2: Generando HTML completo desde DESIGN.md...")

    try:
        client = GeminiClient()

        user_prompt = f"""Genera un archivo HTML COMPLETO y AUTOCONTENIDO que implemente fielmente este DESIGN.md.

---
{context.design_markdown}
---

INSTRUCCIONES CRÍTICAS:

1. **PARSE EXACTO DEL DESIGN.MD**
   - Extrae TODOS los tokens del YAML: colors, typography, rounded, spacing, components
   - Lee ## Overview: entiende la referencia visual, personalidad, audiencia
   - Implementa CADA componente especificado

2. **FIDELIDAD EXTREMA**
   - Colores: exactamente los #HEX del YAML, sin aproximaciones
   - Tipografía: fontFamily, fontSize, fontWeight, lineHeight, letterSpacing exactos
   - Google Fonts: incluye las fuentes mencionadas vía CDN
   - Espaciado: valores exactos del spacing scale
   - Rounded: valores exactos del rounded scale

3. **HTML AUTOCONTENIDO**
   - Empieza con <!DOCTYPE html>, termina con </html>
   - Todo CSS en <style> dentro del <head>
   - Tailwind CDN para grid/flex/responsive
   - JavaScript vanilla MÍNIMO en <script> al final del body (solo si hace falta)
   - NO React, NO Vue, NO Angular, NO imports de frameworks JS

4. **SECTIONS OBLIGATORIAS**
   Navbar + Hero + Features (3-4 cards) + Components Showcase + CTA + Footer

5. **EFECTOS VISUALES**
   - Si glassmorphism: backdrop-filter: blur(), rgba(), border rgba()
   - Si gradientes: linear-gradient() exacto
   - Si sombras: box-shadow exacto del DESIGN.md
   - Hover states en CSS puro con :hover

6. **OUTPUT**
   - SOLO código HTML — sin explicaciones, sin bloques markdown (sin ```)
   - Primera línea: <!DOCTYPE html>
   - Última línea: </html>

Hazlo HERMOSO y FIEL al DESIGN.md. Este es el output que ve el usuario.
"""

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        html_output = await client.generate_text(
            prompt=full_prompt,
            model="flash",
            temperature=0.5,
        )

        # Limpiar bloques markdown si Gemini los incluyó de todas formas
        html_output = html_output.strip()
        html_output = re.sub(r'^```html\s*\n?', '', html_output)
        html_output = re.sub(r'^```\s*\n?', '', html_output)
        html_output = re.sub(r'\n?```\s*$', '', html_output)
        html_output = html_output.strip()

        context.html_output = html_output

        logger.info(
            "✅ HTML generado: %d caracteres, %d líneas",
            len(html_output),
            html_output.count('\n'),
        )

        return context

    except Exception as e:
        logger.error("❌ Error en PASO 2: %s", str(e))
        raise
