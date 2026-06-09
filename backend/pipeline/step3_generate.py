"""
step3_generate.py — Generación de HTML a partir de DESIGN.md
=============================================================
PASO 3 del pipeline: toma el DesignContext con DESIGN.md completo
y produce HTML production-ready usando Gemini + imágenes reales.

Dependencias:
    services/image_generator.py         -> get_image_urls()
    pipeline/prompts/step3_prompts.py   -> SYSTEM_PROMPT
"""

import logging

from models import DesignContext
from pipeline.prompts.step3_prompts import SYSTEM_PROMPT
from services.gemini_client import GeminiClient
from services.image_generator import get_image_urls

logger = logging.getLogger(__name__)


async def generate_code(context: DesignContext) -> DesignContext:
    """
    PASO 3: Genera HTML premium desde DESIGN.md + imagenes reales.

    - Pasa DESIGN.md completo (prose + tokens)
    - URLs de imagenes desde image_generator (cascada: API -> curado -> picsum)
    - Temperatura 0.35, modelo Pro
    """
    if not context.design_markdown:
        raise ValueError("DESIGN.md no encontrado en el contexto")

    logger.info("PASO 3: Generando HTML premium...")

    client = GeminiClient()
    image_urls = await get_image_urls(context.design_brief)

    img_lines = "\n".join(f"  {k}: {v}" for k, v in image_urls.items())

    user_prompt = (
        "Generate a COMPLETE, PRODUCTION-READY HTML website for this brief.\n\n"
        f"=== BRIEF ===\n{context.design_brief}\n\n"
        "=== DESIGN.MD (this is your SPEC -- implement it faithfully) ===\n"
        f"{context.design_markdown}\n\n"
        "=== IMAGES -- copy every URL verbatim, zero broken images allowed ===\n"
        f"{img_lines}\n\n"
        "=== HOW TO BUILD THIS SITE ===\n\n"
        "PHASE 1 -- READ THE DESIGN.MD OVERVIEW\n"
        "Before writing a single line of CSS, read the Overview prose.\n"
        "Answer: What TYPE of website is this? (restaurant, SaaS, law firm, portfolio, etc.)\n"
        "Answer: What VISUAL REFERENCE was chosen? (glassmorphism? editorial? luxury? minimal?)\n"
        "Answer: What ELEVATION style? (tonal layers, shadows, blur, flat?)\n"
        "These answers determine EVERY CSS decision below.\n\n"
        "PHASE 2 -- DECIDE THE PAGE STRUCTURE\n"
        "Based on the brief and Overview, choose sections that fit THIS specific site.\n"
        "Do NOT use a generic template. Ask: what does this business actually need?\n"
        "Examples of site-appropriate structures:\n"
        "  Restaurant: Hero > Menu Highlights > Chef Story > Gallery > Reservations > Footer\n"
        "  SaaS:       Hero > Features > How It Works > Pricing > Testimonials > CTA > Footer\n"
        "  Law Firm:   Hero > Practice Areas > Team > Case Results > Contact > Footer\n"
        "  Portfolio:  Hero > Work Grid > About > Services > Contact > Footer\n"
        "  E-commerce: Hero > Featured Products > Categories > Why Us > Newsletter > Footer\n"
        "  Wellness:   Hero > Services > Philosophy > Team > Testimonials > Booking > Footer\n"
        "Choose the right structure for THIS brief.\n\n"
        "PHASE 3 -- CSS FOUNDATION (always required)\n"
        "a) :root variables: every YAML token becomes a CSS custom property.\n"
        "   --color-primary, --color-surface, --font-display, --radius-card, --spacing-lg, etc.\n"
        "b) Load Google Fonts matching fontFamily tokens (via <link> in <head>).\n"
        "c) Implement elevation from prose: if glassmorphism use backdrop-filter+alpha;\n"
        "   if tonal use surface-container-* levels; if shadows define box-shadow scale.\n\n"
        "PHASE 4 -- IMPLEMENT EACH SECTION\n"
        "Typography: clamp() for responsive text.\n"
        "  Hero display: clamp(2.8rem,6vw,5.5rem), weight 700-800, letter-spacing -0.04em\n"
        "  Section headline: clamp(1.75rem,3.5vw,2.75rem), weight 600-700\n"
        "  Body: 16-18px, weight 400, line-height 1.6-1.75\n"
        "  Caption/label: 12-14px, weight 500-600, letter-spacing 0.04em\n"
        "Composition: apply rule of thirds -- alternate left/right/center alignment per section.\n"
        "Cards: aspect-ratio:4/3, overflow:hidden, hover translateY(-6px) + shadow + img scale(1.05)\n"
        "Hero background: CSS background-image on .hero-bg + gradient overlay for contrast.\n"
        "Sections: min 80px padding top/bottom (48px mobile). Max-width 1200px content container.\n"
        "Avatars if testimonials: 56px circle, 2px primary-color border.\n"
        "Inputs if forms: 48px height, var(--color-primary) focus ring.\n\n"
        "PHASE 5 -- JAVASCRIPT\n"
        "a) IntersectionObserver: .fade-in elements get .visible class on viewport entry.\n"
        "b) Navbar: .scrolled class at scrollY > 50 (opaque bg + blur).\n"
        "c) Mobile menu toggle if navbar present.\n"
        "d) html { scroll-behavior: smooth; }\n\n"
        "=== QUALITY CHECKLIST ===\n"
        "[ ] Sections chosen match the brief (not a generic layout)\n"
        "[ ] All DESIGN.md color tokens used correctly\n"
        "[ ] Every image URL from the list appears verbatim in the HTML (no broken images)\n"
        "[ ] Elevation style from prose implemented (not default shadows)\n"
        "[ ] Every section: min 80px padding, proper heading hierarchy\n"
        "[ ] Font loaded via Google Fonts and applied via CSS variables\n"
        "[ ] WCAG AA contrast: text on backgrounds passes 4.5:1\n\n"
        "OUTPUT: Only raw HTML. First line <!DOCTYPE html>. Last line </html>. No markdown.\n"
    )

    full_prompt = SYSTEM_PROMPT + "\n\n" + user_prompt

    html_output = await client.generate_text(
        prompt=full_prompt,
        model="pro",
        temperature=0.35,
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
