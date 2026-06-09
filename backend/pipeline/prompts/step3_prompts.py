"""
step3_prompts.py -- Ensamblador del system prompt para Step 3.

Para editar una regla especifica, editar el archivo correspondiente en rules/:
  r01_layout.py       Variantes de layout (hero, sections, cards, nav)
  r02_no_overlap.py   Prohibicion de superposicion de contenido
  r03_visual.py       Composicion, jerarquia, botones, iconos
  r04_ux_principles.py  Above-fold, Hick, patron F/Z, color, mobile-first
  r05_gestalt.py      Leyes Gestalt, Occam, proporciones, tipografia
  r06_interactive.py  Carrusel, tabs, acordeon, hover, reveal
  r07_technical.py    CSS values: espaciado, responsive, fonts, imagenes, WCAG
  r08_flowbite.py     Flowbite UI: componentes interactivos y patrones visuales
"""

from pipeline.prompts.rules.r01_layout import LAYOUT_PATTERNS
from pipeline.prompts.rules.r02_no_overlap import NO_OVERLAP_RULES
from pipeline.prompts.rules.r03_visual import VISUAL_PRINCIPLES
from pipeline.prompts.rules.r04_ux_principles import UX_PRINCIPLES
from pipeline.prompts.rules.r05_gestalt import GESTALT_RULES
from pipeline.prompts.rules.r06_interactive import INTERACTIVE_COMPONENTS
from pipeline.prompts.rules.r07_technical import TECHNICAL_QUALITY
from pipeline.prompts.rules.r08_flowbite import FLOWBITE_COMPONENTS

_CORE_IDENTITY = (
    "You are a senior UI/UX engineer and visual designer producing award-winning websites.\n"
    "Your designs are indistinguishable from Stripe, Linear, Airbnb, or Apple marketing pages.\n"
    "You never produce ugly, broken, or generic websites. Every output is polished and professional.\n\n"
    "=== GOLDEN RULE: DESIGN.MD IS YOUR CONSTITUTION ===\n"
    "Read DESIGN.md completely before writing any code.\n"
    "Let it guide EVERY layout, color, and spacing decision.\n"
    "If DESIGN.md says glassmorphism dark: blur + transparency.\n"
    "If DESIGN.md says brutalist: thick borders, raw type.\n"
    "NEVER collapse a rich DESIGN.md into a generic Tailwind grid.\n"
)

_BUILD_PROCESS = (
    "=== BUILD PROCESS ===\n\n"
    "1. READ DESIGN.MD: visual reference, elevation, shape, color roles.\n"
    "2. CHOOSE LAYOUT: different pattern per section, never repeat.\n"
    "3. CSS :root variables from every YAML token. Load Google Fonts.\n"
    "4. ELEVATION exactly as DESIGN.md describes.\n"
    "5. ALL color tokens used -- not just primary.\n"
    "6. IMAGES verbatim. Hero: background-image. Cards: img object-fit cover.\n"
    "7. CHECK: no overlapping content, balanced columns, no empty columns.\n"
    "8. RESPONSIVE @media 768px on every section.\n\n"
    "=== OUTPUT FORMAT ===\n"
    "First line: <!DOCTYPE html>  Last line: </html>\n"
    "No markdown, no explanations, no code fences.\n"
)

# Keywords que activan las reglas de componentes interactivos
_INTERACTIVE_KEYWORDS = [
    "carousel", "carrusel", "slider", "galeria", "gallery",
    "tabs", "acordeon", "accordion", "testimonial", "reviews",
]


def build_system_prompt(brief: str = "") -> str:
    """
    Ensambla el system prompt incluyendo solo las secciones relevantes.
    Usar esta funcion en step3_generate.py en lugar de importar SYSTEM_PROMPT.
    """
    brief_lower = brief.lower()

    sections = [
        _CORE_IDENTITY,
        LAYOUT_PATTERNS,
        NO_OVERLAP_RULES,
        VISUAL_PRINCIPLES,
        UX_PRINCIPLES,
        GESTALT_RULES,
        TECHNICAL_QUALITY,
        FLOWBITE_COMPONENTS,
    ]

    # Incluir reglas de interactivos solo si el brief los menciona
    if any(kw in brief_lower for kw in _INTERACTIVE_KEYWORDS):
        sections.insert(-2, INTERACTIVE_COMPONENTS)

    sections.append(_BUILD_PROCESS)
    return "\n".join(sections)


# Compatibilidad: SYSTEM_PROMPT sin brief (incluye todo)
SYSTEM_PROMPT = build_system_prompt()
