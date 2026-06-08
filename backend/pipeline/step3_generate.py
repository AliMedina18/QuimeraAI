import logging
import re
import yaml
from backend.models import DesignContext
from backend.services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


def _extract_tokens_from_design_md(design_md: str) -> dict:
    """Extrae SOLO los tokens YAML. NO incluye markdown body."""
    if not design_md.startswith('---'):
        return {}
    
    parts = design_md.split('---', 2)
    if len(parts) < 3:
        return {}
    
    try:
        tokens = yaml.safe_load(parts[1])
        return tokens or {}
    except Exception as e:
        logger.warning(f"Error extrayendo YAML: {e}")
        return {}


def _format_tokens_for_prompt(tokens: dict) -> str:
    """Formatea tokens en formato legible para Gemini."""
    sections = []
    
    if 'colors' in tokens and tokens['colors']:
        sections.append("## COLORES")
        for name, hex_color in tokens['colors'].items():
            sections.append(f"  {name}: {hex_color}")
        sections.append("")
    
    if 'typography' in tokens and tokens['typography']:
        sections.append("## TIPOGRAFIA")
        for name, props in tokens['typography'].items():
            if isinstance(props, dict):
                ff = props.get('fontFamily', '')
                fs = props.get('fontSize', '')
                sections.append(f"  {name}: {ff} {fs}")
        sections.append("")
    
    if 'spacing' in tokens and tokens['spacing']:
        sections.append("## ESPACIADO")
        for name, value in tokens['spacing'].items():
            sections.append(f"  {name}: {value}")
        sections.append("")
    
    if 'rounded' in tokens and tokens['rounded']:
        sections.append("## BORDER RADIUS")
        for name, value in tokens['rounded'].items():
            sections.append(f"  {name}: {value}")
        sections.append("")
    
    return "\n".join(sections)


SYSTEM_PROMPT = """Eres experto en HTML, CSS y diseño visual.

OBJETIVO: Generar HTML COMPLETO y AUTOCONTENIDO que implemente el sitio web
del usuario (basado en su brief).

DIFERENCIA IMPORTANTE: 
- El DESIGN.md define tokens (colores, tipografia, espaciado)
- TU debes crear el SITIO WEB REAL, NO un "showcase" de componentes
- Aplica tokens, pero NO muestres especificaciones internas
- Usuario NO quiere ver "Paleta", "Tipografia", "Componentes" 
- Usuario QUIERE su sitio web terminado, hermoso, funcional

REGLAS CRITICAS:
1. SOLO HTML sin explicaciones, sin codigo blocks, sin comentarios fuera del codigo
2. Primera linea: <!DOCTYPE html>
3. Ultima linea: </html>
4. CSS + JS inline, SIN React/Vue/Angular
5. Tailwind CDN para grid/flex/responsive
6. Google Fonts via <link>

ESTRUCTURA:
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Nombre]</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="..." rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root { /* tokens */ }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { /* estilos base */ }
    /* componentes CSS */
  </style>
</head>
<body>
  <!-- Navbar, Hero, Secciones, CTA, Footer -->
  <script>
    /* JS vanilla minimo, solo si necesario */
  </script>
</body>
</html>

IMPLEMENTACION:
- Aplica tokens EXACTAMENTE (colores #HEX exactos, fonts exactas, spacing exacto)
- Colores de manera PREMIUM (primary en hero/CTAs, secondary en acentos)
- Contenido desde el BRIEF (todas las secciones solicitadas)
- Responsivo (mobile/tablet/desktop)
- Efectos visuales exactos (glassmorphism, gradientes, sombras)
- HTML semantico (nav, main, section, article, footer)
- SIN especificaciones internas visibles"""


async def generate_code(context: DesignContext) -> DesignContext:
    """PASO 3: Generar HTML desde DESIGN.md.
    
    Extrae SOLO los tokens YAML del DESIGN.md.
    Genera HTML que implementa el sitio web real (NO especificaciones internas).
    """
    if not context.design_markdown:
        raise ValueError("DESIGN.md no encontrado")

    logger.info("PASO 3: Generando HTML desde DESIGN.md...")

    try:
        client = GeminiClient()
        
        tokens = _extract_tokens_from_design_md(context.design_markdown)
        tokens_formatted = _format_tokens_for_prompt(tokens)
        
        logger.info("Tokens extraidos (sin markdown body)")

        user_prompt = f"""Genera HTML COMPLETO y AUTOCONTENIDO para el sitio web del usuario.

BRIEF DEL USUARIO:
---
{context.design_brief}
---

DESIGN TOKENS (APLICAR EXACTAMENTE):
---
{tokens_formatted}
---

INSTRUCCIONES:

1. SITIO WEB REAL, NO especificaciones
   - Mostrar sitio web terminado, hermoso, funcional
   - NO mostrar Paleta de Colores
   - NO mostrar Escala de Tipografia
   - NO mostrar Componentes y variantes

2. Aplicar tokens EXACTAMENTE
   - Colores: #HEX exactos, aplicados de manera PREMIUM
   - Tipografia: fontFamily, fontSize, fontWeight exactos
   - Espaciado: valores exactos
   - Rounded: valores exactos

3. Contenido desde el BRIEF
   - Todas las secciones solicitadas
   - Contenido realista y relevante
   - Producto terminado y profesional

4. HTML AUTOCONTENIDO
   - <!DOCTYPE html> ... </html>
   - Todo CSS en <style> en <head>
   - Tailwind CDN para utilities
   - JS vanilla minimo (solo si necesario)
   - SIN React, Vue, Angular

5. CALIDAD
   - Responsive (mobile/tablet/desktop)
   - Efectos visuales exactos
   - HTML semantico
   - Premium y sofisticado

6. OUTPUT
   - SOLO codigo HTML
   - Primera linea: <!DOCTYPE html>
   - Ultima linea: </html>
   - SIN explicaciones, bloques markdown, comentarios
"""

        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        html_output = await client.generate_text(
            prompt=full_prompt,
            model="flash",
            temperature=0.5,
        )

        html_output = html_output.strip()
        html_output = re.sub(r'^```html\s*\n?', '', html_output)
        html_output = re.sub(r'^```\s*\n?', '', html_output)
        html_output = re.sub(r'\n?```\s*$', '', html_output)
        html_output = html_output.strip()

        context.html_output = html_output

        logger.info(
            "HTML generado: %d caracteres",
            len(html_output),
        )

        return context

    except Exception as e:
        logger.error("Error: %s", str(e))
        raise
