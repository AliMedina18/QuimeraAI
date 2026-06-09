"""
step3_generate.py - Generacion de HTML a partir de DESIGN.md
PASO 3 del pipeline: toma el DesignContext con DESIGN.md completo
y produce HTML production-ready usando Gemini + imagenes reales.
"""

import logging

from models import DesignContext
from pipeline.prompts.step3_prompts import build_system_prompt
from services.gemini_client import GeminiClient
from services.image_generator import get_image_urls

logger = logging.getLogger(__name__)

# Per-slot instructions for image placement
SLOT_INSTRUCTIONS = {
    "hero":       "Hero section -- use as CSS background-image on the hero wrapper div.",
    "hero_alt":   "Secondary hero or above-the-fold accent image.",
    "section_bg": "Section background -- use as CSS background-image on a full-bleed section.",
    "card_1":     "Card/feature image 1 -- use inside an img tag with object-fit: cover.",
    "card_2":     "Card/feature image 2 -- use inside an img tag with object-fit: cover.",
    "card_3":     "Card/feature image 3 -- use inside an img tag with object-fit: cover.",
    "card_4":     "Card/feature image 4 -- use inside an img tag with object-fit: cover.",
    "card_5":     "Card/feature image 5 -- use inside an img tag with object-fit: cover.",
    "card_6":     "Card/feature image 6 -- use inside an img tag with object-fit: cover.",
    "avatar_1":   "Testimonial/team avatar 1 -- 64px circle img.",
    "avatar_2":   "Testimonial/team avatar 2 -- 64px circle img.",
    "avatar_3":   "Testimonial/team avatar 3 -- 64px circle img.",
}

# Spanish detection keywords
SPANISH_KEYWORDS = [
    "para", "una", "con", "sitio", "web", "empresa", "que",
    " de ", " en ", " la ", " el ", "diseno", "pagina",
]


async def generate_code(context: DesignContext) -> DesignContext:
    """
    PASO 3: Genera HTML premium desde DESIGN.md + imagenes reales.
    Temperatura 0.55 -- balance entre creatividad y calidad tecnica.
    """
    if not context.design_markdown:
        raise ValueError("DESIGN.md no encontrado en el contexto")

    logger.info("PASO 3: Generando HTML premium...")

    client = GeminiClient()
    image_urls = await get_image_urls(context.design_brief)

    # Build explicit per-slot image instructions
    img_lines_list = []
    for k, v in image_urls.items():
        instruction = SLOT_INSTRUCTIONS.get(k, "Use in an appropriate section.")
        img_lines_list.append(f"  {k}: {v}\n    -> {instruction}")
    img_lines = "\n".join(img_lines_list)

    # Build image plan context from Step 2
    image_plan_context = ""
    if context.image_generation_plan and context.image_generation_plan.images:
        plan_lines = []
        for img in context.image_generation_plan.images:
            plan_lines.append(
                f"  section={img.section} | intent={img.description} | style={img.style}"
            )
        image_plan_context = (
            "\n=== IMAGE PLACEMENT PLAN (from Step 2) ===\n"
            "Match image slots to sections by intent. Do NOT always use default positions.\n"
            + "\n".join(plan_lines)
            + "\n"
        )

    # Language detection
    brief_lower = context.design_brief.lower()
    spanish_hits = sum(1 for w in SPANISH_KEYWORDS if w in brief_lower)
    if spanish_hits >= 3:
        lang_instruction = (
            "LANGUAGE: The brief is in SPANISH. ALL site text (headlines, body copy, "
            "labels, buttons, placeholders, footer text) MUST be written in Spanish. "
            "No English text anywhere in the site.\n\n"
        )
    else:
        lang_instruction = (
            "LANGUAGE: The brief is in ENGLISH. ALL site text must be in English.\n\n"
        )

    user_prompt = (
        "Generate a COMPLETE, PRODUCTION-READY HTML website.\n\n"
        + lang_instruction
        + "=== BRIEF ===\n"
        + context.design_brief
        + "\n\n"
        "=== DESIGN.MD -- YOUR CONSTITUTION. READ FULLY BEFORE WRITING CSS ===\n"
        + context.design_markdown
        + "\n\n"
        "=== IMAGES -- EVERY URL BELOW MUST APPEAR IN THE HTML, COPIED VERBATIM ===\n"
        "Rules:\n"
        "  (1) Copy each URL exactly -- no modifications, no shortening.\n"
        "  (2) Every slot must be used. No missing images.\n"
        "  (3) hero and section_bg: CSS background-image property.\n"
        "  (4) card_* and avatar_*: <img> tags with crossorigin='anonymous'.\n"
        "  (5) All image containers: object-fit: cover + defined width/height.\n"
        "  (6) Never placeholder.com or empty src.\n\n"
        + img_lines
        + "\n"
        + image_plan_context
        + "\n"
        "=== BUILD PROCESS ===\n\n"
        "STEP 1 -- READ DESIGN.MD PROSE\n"
        "Extract: visual reference/mood, elevation style, shape language, color roles.\n"
        "These OVERRIDE every default. If DESIGN.md says asymmetric, do asymmetric.\n\n"
        "STEP 2 -- DESIGN PAGE STRUCTURE FROM SCRATCH\n"
        "Do NOT pick from a preset list. Choose sections and layouts that make this\n"
        "brand feel SPECIFIC and MEMORABLE. Use the layout patterns in the system prompt.\n"
        "Different sections must use different layout patterns.\n\n"
        "STEP 3 -- CSS FOUNDATION\n"
        "Convert every YAML token from DESIGN.md into a CSS custom property:\n"
        "  --color-primary, --color-surface, --font-display, --radius-card, etc.\n"
        "Load Google Fonts for the fontFamily tokens. Apply via CSS variables throughout.\n"
        "Implement elevation EXACTLY as DESIGN.md describes:\n"
        "  glassmorphism: backdrop-filter + rgba backgrounds\n"
        "  tonal: surface-container color levels, no box-shadow\n"
        "  editorial flat: borders + scale, no blur\n\n"
        "STEP 4 -- IMPLEMENT EVERY SECTION\n"
        "Use clamp() for fluid typography. Use ALL color tokens -- if palette has 10, all 10 appear.\n"
        "Apply color to section backgrounds, borders, gradients -- not just buttons.\n"
        "Alternate layout patterns between sections.\n\n"
        "STEP 5 -- JAVASCRIPT (all required)\n"
        "  - html { scroll-behavior: smooth }\n"
        "  - IntersectionObserver: .reveal elements get .visible class on viewport entry.\n"
        "    CSS: .reveal { opacity: 0; transform: translateY(28px); transition: opacity 0.6s, transform 0.6s; }\n"
        "         .reveal.visible { opacity: 1; transform: none; }\n"
        "    Apply .reveal to: section headlines, cards, feature blocks, stat numbers.\n"
        "    Stagger: .reveal:nth-child(n) { transition-delay: calc(n * 0.1s) }\n"
        "  - Navbar: .scrolled class at scrollY > 50px\n"
        "  - Mobile nav toggle if nav has links\n\n"
        "=== FINAL CHECKLIST ===\n"
        "[ ] Layout reflects DESIGN.md visual reference, not a generic template\n"
        "[ ] All YAML color tokens are CSS custom properties AND all are used\n"
        "[ ] EVERY image URL appears verbatim (all 12 slots used, no broken images)\n"
        "[ ] hero/section_bg: background-image CSS. card_*/avatar_*: img with object-fit cover\n"
        "[ ] Elevation matches DESIGN.md prose exactly\n"
        "[ ] clamp() on all display/headline sizes. Google Fonts loaded. CSS variables applied.\n"
        "[ ] Sections alternate layout patterns\n"
        "[ ] .reveal/.visible IntersectionObserver on headlines, cards, features\n"
        "[ ] WCAG AA: text on backgrounds >= 4.5:1\n"
        "[ ] Mobile responsive at <= 768px with @media queries\n"
        "[ ] ALL text content is in the same language as the brief\n\n"
        "OUTPUT: Only raw HTML. First line <!DOCTYPE html>. Last line </html>. No markdown.\n"
    )

    full_prompt = build_system_prompt(context.design_brief) + "\n\n" + user_prompt

    html_output = await client.generate_text(
        prompt=full_prompt,
        model="pro",
        temperature=0.55,
    )

    # Strip markdown code fences -- Gemini sometimes wraps HTML in ```html...```
    html_output = html_output.strip()
    if html_output.startswith("```html"):
        html_output = html_output[7:]
    elif html_output.startswith("```"):
        html_output = html_output[3:]
    if html_output.endswith("```"):
        html_output = html_output[:-3]
    html_output = html_output.strip()

    context.html_output = html_output
    logger.info("PASO 3: HTML generado (%d chars)", len(html_output))
    return context
