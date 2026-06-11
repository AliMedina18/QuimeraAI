"""
suggestion_engine.py — Motor de sugerencias para el brief de diseño
====================================================================
Sin llamadas a Gemini. Lógica determinística + diccionarios.
Responde en <50ms. Usado por el endpoint POST /sugerir.

Retorna 4 tipos de sugerencias:
  1. missing   — elementos que faltan en el brief
  2. styles    — estilos de diseño que encajan
  3. templates — templates de la biblioteca que hacen match
  4. palettes  — paletas de color por industria
"""

from __future__ import annotations
import re
from typing import Optional

from services.keyword_translator import translate_brief_to_keywords


# ============================================================================
# DETECCIÓN DE ELEMENTOS FALTANTES
# ============================================================================

# Patrones para detectar qué YA está en el brief
_AUDIENCE_PATTERNS = [
    r"\bjóvenes?\b", r"\badultos?\b", r"\bmujeres?\b", r"\bhombres?\b",
    r"\bprofesionales?\b", r"\bfamilias?\b", r"\bempresas?\b",
    r"\bb2b\b", r"\bb2c\b", r"\bdirigido\b", r"\bpúblico\b", r"\btarget\b",
    r"\bedad\b", r"\busuarios?\b", r"\bclientes?\b", r"\b\d{2}[-–]\d{2}\b",
    r"\bpara\s+\w+\s+(que|con|de)\b",
]
_COLOR_PATTERNS = [
    r"#[0-9a-fA-F]{3,6}\b",
    r"\bazul\b", r"\brojo\b", r"\bverde\b", r"\bnegro\b", r"\bblanco\b",
    r"\bmorado\b", r"\bdorado\b", r"\bplateado\b", r"\bnaranja\b",
    r"\brosa\b", r"\bamarillo\b", r"\bgris\b", r"\bmarrón\b",
    r"\bcolor(es)?\b", r"\bpaleta\b", r"\btonos?\b", r"\boscuro\b", r"\bclaro\b",
    r"\bpurple\b", r"\bblue\b", r"\bgreen\b", r"\bblack\b", r"\bwhite\b",
]
_TONE_PATTERNS = [
    r"\bminimalista\b", r"\belegante\b", r"\bmoderno\b", r"\bdivertido\b",
    r"\bformal\b", r"\bprofesional\b", r"\blujoso?\b", r"\bjuvenil\b",
    r"\bserio\b", r"\baudaz\b", r"\bbold\b", r"\bpremium\b", r"\bcasual\b",
    r"\bdark\s*mode\b", r"\bglass\b", r"\bglassmorphism\b", r"\bvibrante\b",
    r"\bdinámico\b", r"\bclean\b", r"\bsimple\b", r"\bsofisticado\b",
    r"\bmayéutico\b", r"\blúdico\b", r"\bfresco\b", r"\bconservador\b",
]
_SECTION_PATTERNS = [
    r"\bhero\b", r"\babout\b", r"\bservicio(s)?\b", r"\bcontacto\b",
    r"\bprecios?\b", r"\bpricing\b", r"\btestimonio(s)?\b", r"\bgalería\b",
    r"\bblog\b", r"\bequipo\b", r"\bfooter\b", r"\bnavbar\b", r"\bmenú\b",
    r"\bcarousel\b", r"\bfaq\b", r"\bportafolio\b", r"\bfeature(s)?\b",
    r"\bsección(es)?\b",
]
_CTA_PATTERNS = [
    r"\breserva(r)?\b", r"\bcompra(r)?\b", r"\bcontacta(r)?\b",
    r"\bdescarga(r)?\b", r"\bregistra(rse)?\b", r"\bsuscri(be|bir)\b",
    r"\bllama(r)?\b", r"\bagenda(r)?\b", r"\bcontratar\b", r"\bpedir\b",
    r"\bstarted\b", r"\bsign.?up\b", r"\bget.?started\b", r"\bcta\b",
    r"\bbotón\b",
]
_REFERENCE_PATTERNS = [
    r"\btipo\b", r"\breferencia\b", r"\bsimilar\s+a\b", r"\binspira(do|ción)\b",
    r"\bstyle\b", r"\bcomo\s+(stripe|notion|figma|airbnb|apple)\b",
    r"\bdiseño\s+\w+\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    text_l = text.lower()
    return any(re.search(p, text_l) for p in patterns)


def detect_missing(brief: str) -> list[dict]:
    """
    Devuelve lista de elementos ausentes del brief.
    Cada item: {key, label, hint, chip_text}
    """
    missing = []

    if not _matches_any(brief, _AUDIENCE_PATTERNS):
        missing.append({
            "key": "audience",
            "label": "Público objetivo",
            "hint": "¿A quién va dirigido el sitio?",
            "chip_text": "Público objetivo: [jóvenes 25-35 / profesionales / familias / empresas B2B]",
        })

    if not _matches_any(brief, _COLOR_PATTERNS):
        missing.append({
            "key": "colors",
            "label": "Colores",
            "hint": "Sin colores definidos → Quimera los elegirá por industria",
            "chip_text": "Paleta de colores: [azul y blanco / negro y dorado / verde y gris]",
        })

    if not _matches_any(brief, _TONE_PATTERNS):
        missing.append({
            "key": "tone",
            "label": "Tono visual",
            "hint": "¿Qué personalidad debe transmitir el diseño?",
            "chip_text": "Tono visual: [minimalista y elegante / bold y llamativo / cálido y cercano]",
        })

    if not _matches_any(brief, _SECTION_PATTERNS):
        missing.append({
            "key": "sections",
            "label": "Secciones",
            "hint": "¿Qué páginas/secciones necesita?",
            "chip_text": "Secciones: hero, servicios, sobre nosotros, testimonios, contacto",
        })

    if not _matches_any(brief, _CTA_PATTERNS):
        missing.append({
            "key": "cta",
            "label": "Llamada a la acción",
            "hint": "¿Qué quieres que haga el visitante?",
            "chip_text": "Acción principal: [reservar cita / contactar / comprar / registrarse]",
        })

    return missing


# ============================================================================
# ESTILOS DE DISEÑO
# ============================================================================

# Estilos disponibles con su texto que se añade al brief al hacer click
_ALL_STYLES = [
    {
        "id": "minimalist",
        "label": "Minimalista",
        "emoji": "⬜",
        "description": "Clean, mucho espacio blanco, tipografía elegante",
        "chip_text": "Estilo visual minimalista: mucho espacio blanco, tipografía elegante, sin ornamentos, líneas limpias.",
        "industries": ["saas", "tech", "developer", "ai", "productivity", "architecture", "dental", "therapy"],
    },
    {
        "id": "dark",
        "label": "Dark mode",
        "emoji": "🌑",
        "description": "Oscuro, sofisticado, acentos de color sobre negro",
        "chip_text": "Modo oscuro: fondo negro profundo #0A0A0A, acentos luminosos, tipografía clara.",
        "industries": ["tech", "developer", "ai", "gaming", "fintech", "fitness", "crypto", "automotive"],
    },
    {
        "id": "bold",
        "label": "Bold & llamativo",
        "emoji": "🔴",
        "description": "Tipografía grande, colores saturados, alto impacto",
        "chip_text": "Diseño bold: tipografía impactante muy grande, colores saturados, alto contraste, energía visual alta.",
        "industries": ["fitness", "fashion", "restaurant", "cafe", "automotive", "sports"],
    },
    {
        "id": "glassmorphism",
        "label": "Glassmorphism",
        "emoji": "🫧",
        "description": "Translúcido, blur, bordes luminosos, paleta fría",
        "chip_text": "Estética glassmorphism: fondos translúcidos con blur, bordes sutiles luminosos, paleta fría azul/violeta.",
        "industries": ["tech", "ai", "saas", "developer", "fintech"],
    },
    {
        "id": "premium",
        "label": "Elegante & Premium",
        "emoji": "✨",
        "description": "Serif, dorados, neutros, mucho espacio",
        "chip_text": "Diseño premium y lujoso: tipografía serif, colores dorados y neutros profundos, espaciado generoso.",
        "industries": ["hotel", "realestate", "fashion", "legal", "automotive", "wellness", "restaurant"],
    },
    {
        "id": "colorful",
        "label": "Colorido & vibrante",
        "emoji": "🌈",
        "description": "Gradientes, colores vivos, mucha energía visual",
        "chip_text": "Paleta colorida y vibrante: gradientes múltiples, colores saturados, visual dinámico y enérgico.",
        "industries": ["education", "wellness", "travel", "cafe", "events", "fitness"],
    },
    {
        "id": "editorial",
        "label": "Editorial",
        "emoji": "📰",
        "description": "Inspirado en revistas, grid asimétrico, bold serif",
        "chip_text": "Estilo editorial: grid asimétrico tipo revista, tipografía serif bold, contraste fuerte entre secciones.",
        "industries": ["fashion", "media", "photography", "blog", "theverge", "wired"],
    },
    {
        "id": "brutalist",
        "label": "Brutalismo",
        "emoji": "🧱",
        "description": "Crudo, bordes visibles, tipografía agresiva",
        "chip_text": "Estilo brutalista: bordes visibles, tipografía agresiva, sin suavizado, raw y directo.",
        "industries": ["developer", "tech", "media", "photography", "gaming"],
    },
    {
        "id": "organic",
        "label": "Orgánico & cálido",
        "emoji": "🌿",
        "description": "Colores tierra, formas fluidas, cercanía humana",
        "chip_text": "Estética orgánica: colores tierra (beige, verde salvia, terracota), formas fluidas, calidez humana.",
        "industries": ["wellness", "cafe", "restaurant", "healthcare", "therapy", "agriculture", "pets"],
    },
]


def get_styles_for_industry(industry: str, brief: str = "") -> list[dict]:
    """
    Retorna 4-5 estilos relevantes para la industria detectada.
    Siempre incluye 2-3 que hacen match + 1-2 genéricos de contraste.
    """
    # Primero los que hacen match con la industria
    matched = [s for s in _ALL_STYLES if industry in s["industries"]]
    # Luego los que no hacen match (para dar variedad)
    unmatched = [s for s in _ALL_STYLES if industry not in s["industries"]]

    # Garantizar mínimo 3 estilos siempre (industria desconocida → usa todos como "unmatched")
    needed_from_unmatched = max(2, 3 - len(matched))
    result = matched[:3] + unmatched[:needed_from_unmatched]

    # Retornar sin el campo "industries" (innecesario para el cliente)
    return [
        {k: v for k, v in s.items() if k != "industries"}
        for s in result
    ]


# ============================================================================
# TEMPLATES RECOMENDADOS POR INDUSTRIA
# ============================================================================

# Mapping industria → lista de templates (nombres de carpetas en /backend/templates/)
# Con descripción corta de por qué encajan
_INDUSTRY_TEMPLATES: dict[str, list[dict]] = {
    "fintech": [
        {"slug": "stripe",     "label": "Stripe",     "mood": "SaaS profesional, confianza máxima"},
        {"slug": "revolut",    "label": "Revolut",    "mood": "Fintech moderno, dark + colores vivos"},
        {"slug": "wise",       "label": "Wise",       "mood": "Transparente, claro, internacional"},
        {"slug": "mastercard", "label": "Mastercard", "mood": "Premium, rojo/dorado, autoridad"},
    ],
    "crypto": [
        {"slug": "binance",  "label": "Binance",  "mood": "Crypto exchange, dark + amarillo"},
        {"slug": "kraken",   "label": "Kraken",   "mood": "Dark premium, violeta, autoridad crypto"},
        {"slug": "coinbase", "label": "Coinbase", "mood": "Crypto accesible, clean, azul"},
        {"slug": "revolut",  "label": "Revolut",  "mood": "Fintech vibrante, gradientes"},
    ],
    "saas": [
        {"slug": "notion",     "label": "Notion",     "mood": "Clean, documentación clara, minimalista"},
        {"slug": "figma",      "label": "Figma",      "mood": "Herramienta creativa, colorido-pastel"},
        {"slug": "linear.app", "label": "Linear",     "mood": "Dark, velocidad, developer-first"},
        {"slug": "airtable",   "label": "Airtable",   "mood": "Colorido, colaborativo, amigable"},
        {"slug": "intercom",   "label": "Intercom",   "mood": "Customer success, azul, conversacional"},
    ],
    "developer": [
        {"slug": "cursor",     "label": "Cursor",   "mood": "AI code editor, dark sofisticado"},
        {"slug": "warp",       "label": "Warp",     "mood": "Terminal moderno, dark gradient"},
        {"slug": "raycast",    "label": "Raycast",  "mood": "Productividad Mac, dark elegante"},
        {"slug": "vercel",     "label": "Vercel",   "mood": "Deploy instantáneo, black & white radical"},
        {"slug": "supabase",   "label": "Supabase", "mood": "Open-source BaaS, verde vibrante"},
    ],
    "tech": [
        {"slug": "vercel",     "label": "Vercel",    "mood": "Minimalista, blanco y negro, moderno"},
        {"slug": "linear.app", "label": "Linear",    "mood": "Dark, velocidad, precision"},
        {"slug": "cursor",     "label": "Cursor",    "mood": "AI-first, dark premium"},
        {"slug": "framer",     "label": "Framer",    "mood": "Animado, creativo, herramienta web"},
        {"slug": "hashicorp",  "label": "HashiCorp", "mood": "Infrastructure, clean oscuro"},
    ],
    "ai": [
        {"slug": "claude",      "label": "Claude",      "mood": "Cálido, accesible, arena + blanco"},
        {"slug": "mistral.ai",  "label": "Mistral",     "mood": "Oscuro elegante, europeo, técnico"},
        {"slug": "elevenlabs",  "label": "ElevenLabs",  "mood": "Dark impactante, audio-first"},
        {"slug": "cohere",      "label": "Cohere",       "mood": "Enterprise AI, azul corporativo"},
        {"slug": "x.ai",        "label": "xAI",         "mood": "Radical minimalista, blanco/negro"},
        {"slug": "runwayml",    "label": "Runway",      "mood": "Creativo, artístico, video IA"},
    ],
    "restaurant": [
        {"slug": "airbnb",    "label": "Airbnb",    "mood": "Cálido, fotografía protagonista, coral"},
        {"slug": "uber",      "label": "Uber",      "mood": "Dark elegante, minimalista, negro puro"},
        {"slug": "starbucks", "label": "Starbucks", "mood": "Verde oscuro, comunidad, cálido"},
    ],
    "cafe": [
        {"slug": "starbucks", "label": "Starbucks", "mood": "Verde oscuro, cálido, comunidad"},
        {"slug": "airbnb",    "label": "Airbnb",    "mood": "Fotografía protagonista, coral, cercano"},
        {"slug": "notion",    "label": "Notion",    "mood": "Clean, tipografía elegante, neutros"},
    ],
    "hotel": [
        {"slug": "airbnb",   "label": "Airbnb",   "mood": "Cálido, fotografía, coral/beige"},
        {"slug": "uber",     "label": "Uber",     "mood": "Dark premium, negro elegante"},
        {"slug": "apple",    "label": "Apple",    "mood": "Premium silencioso, blanco, espacio"},
    ],
    "wellness": [
        {"slug": "airbnb",  "label": "Airbnb",  "mood": "Cálido, fotografía, colores naturales"},
        {"slug": "claude",  "label": "Claude",  "mood": "Arena cálido, tipografía suave"},
        {"slug": "notion",  "label": "Notion",  "mood": "Clean minimalista, espacio, neutros"},
    ],
    "fitness": [
        {"slug": "nike",    "label": "Nike",    "mood": "Bold, negro y blanco, impacto máximo"},
        {"slug": "spotify", "label": "Spotify", "mood": "Dark + verde neón, energético"},
        {"slug": "apple",   "label": "Apple",   "mood": "Premium, limpio, aspiracional"},
    ],
    "fashion": [
        {"slug": "nike",      "label": "Nike",      "mood": "Bold, negro/blanco, icónico"},
        {"slug": "apple",     "label": "Apple",     "mood": "Premium minimalista, blanco puro"},
        {"slug": "pinterest", "label": "Pinterest", "mood": "Visual, grid discovery, coral"},
    ],
    "automotive": [
        {"slug": "tesla",        "label": "Tesla",       "mood": "Dark premium, minimalista radical"},
        {"slug": "bmw",          "label": "BMW",         "mood": "Azul y negro, alemán, ejecutivo"},
        {"slug": "ferrari",      "label": "Ferrari",     "mood": "Rojo y negro, emoción extrema"},
        {"slug": "lamborghini",  "label": "Lamborghini", "mood": "Negro + amarillo, agresivo, angular"},
        {"slug": "bugatti",      "label": "Bugatti",     "mood": "Súper premium, azul/negro, exclusivo"},
    ],
    "education": [
        {"slug": "notion",   "label": "Notion",   "mood": "Documentación clara, organizado"},
        {"slug": "figma",    "label": "Figma",    "mood": "Colorido, amigable, creativo"},
        {"slug": "airtable", "label": "Airtable", "mood": "Colaborativo, claro, visual"},
    ],
    "legal": [
        {"slug": "stripe",    "label": "Stripe",    "mood": "Confianza, azul, profesional"},
        {"slug": "intercom",  "label": "Intercom",  "mood": "Corporativo limpio, azul oscuro"},
        {"slug": "ibm",       "label": "IBM",       "mood": "Institucional, azul fuerte, autoridad"},
    ],
    "healthcare": [
        {"slug": "stripe",  "label": "Stripe",  "mood": "Confianza, azul, clean"},
        {"slug": "claude",  "label": "Claude",  "mood": "Cálido, accesible, humano"},
        {"slug": "notion",  "label": "Notion",  "mood": "Organizado, claro, información fácil"},
    ],
    "realestate": [
        {"slug": "airbnb",  "label": "Airbnb",  "mood": "Fotografía, cálido, exploración"},
        {"slug": "uber",    "label": "Uber",    "mood": "Dark elegante, minimalista"},
        {"slug": "apple",   "label": "Apple",   "mood": "Premium, espacio, aspiracional"},
    ],
    "ecommerce": [
        {"slug": "shopify",   "label": "Shopify",  "mood": "Ecommerce, verde, confiable"},
        {"slug": "pinterest", "label": "Pinterest","mood": "Visual discovery, coral, grid"},
        {"slug": "airbnb",    "label": "Airbnb",   "mood": "Marketplace, cálido, confianza"},
        {"slug": "stripe",    "label": "Stripe",   "mood": "Checkout, azul, profesional"},
    ],
    "media": [
        {"slug": "spotify",   "label": "Spotify",  "mood": "Dark, neón verde, energético"},
        {"slug": "theverge",  "label": "The Verge","mood": "Editorial, vibrante, rojo/negro"},
        {"slug": "wired",     "label": "Wired",    "mood": "Magazine tech, yellow accent"},
        {"slug": "pinterest", "label": "Pinterest","mood": "Visual, grid, coral discovery"},
    ],
    "productivity": [
        {"slug": "notion",     "label": "Notion",     "mood": "Clean, documentación, neutros"},
        {"slug": "linear.app", "label": "Linear",     "mood": "Dark, velocidad, precision"},
        {"slug": "cal",        "label": "Cal",        "mood": "Calendar, clean, scheduling"},
        {"slug": "raycast",    "label": "Raycast",    "mood": "Launcher, dark elegante, rápido"},
        {"slug": "superhuman", "label": "Superhuman", "mood": "Email premium, dark, velocidad"},
    ],
}

# Fallback genérico para industrias no mapeadas
_DEFAULT_TEMPLATES = [
    {"slug": "stripe",  "label": "Stripe",  "mood": "SaaS profesional, confianza, azul"},
    {"slug": "notion",  "label": "Notion",  "mood": "Clean minimalista, organizado, neutros"},
    {"slug": "airbnb",  "label": "Airbnb",  "mood": "Cálido, fotografía protagonista, coral"},
    {"slug": "figma",   "label": "Figma",   "mood": "Colorido pastel, creativo, moderno"},
    {"slug": "apple",   "label": "Apple",   "mood": "Premium silencioso, blanco puro, espacio"},
]


def get_templates_for_industry(industry: str) -> list[dict]:
    templates = _INDUSTRY_TEMPLATES.get(industry, _DEFAULT_TEMPLATES)
    # Añade chip_text a cada template
    result = []
    for t in templates[:4]:
        result.append({
            **t,
            "chip_text": f"Referencia visual: {t['label']}. {t['mood']}.",
        })
    return result


# ============================================================================
# PALETAS DE COLOR POR INDUSTRIA
# ============================================================================

_INDUSTRY_PALETTES: dict[str, list[dict]] = {
    "fintech": [
        {"name": "Azul confianza", "primary": "#1A56DB", "secondary": "#1E40AF", "accent": "#3B82F6",
         "surface": "#F8FAFF", "text": "#111827",
         "chip_text": "Colores: azul principal #1A56DB, azul oscuro #1E40AF, superficie #F8FAFF, texto #111827."},
        {"name": "Verde finanzas", "primary": "#059669", "secondary": "#065F46", "accent": "#10B981",
         "surface": "#F0FDF4", "text": "#111827",
         "chip_text": "Colores: verde #059669, verde oscuro #065F46, acento #10B981, fondo claro #F0FDF4."},
        {"name": "Dark premium", "primary": "#818CF8", "secondary": "#6366F1", "accent": "#A78BFA",
         "surface": "#0A0A0F", "text": "#F9FAFB",
         "chip_text": "Colores: fondo negro #0A0A0F, violeta #818CF8, acento púrpura #A78BFA, texto blanco."},
    ],
    "saas": [
        {"name": "Índigo SaaS", "primary": "#4F46E5", "secondary": "#3730A3", "accent": "#818CF8",
         "surface": "#FAFAFA", "text": "#111827",
         "chip_text": "Colores: índigo #4F46E5, índigo oscuro #3730A3, acento suave #818CF8, fondo #FAFAFA."},
        {"name": "Cyan tech", "primary": "#0EA5E9", "secondary": "#0284C7", "accent": "#38BDF8",
         "surface": "#F8FAFF", "text": "#0F172A",
         "chip_text": "Colores: cyan #0EA5E9, cyan oscuro #0284C7, acento #38BDF8, fondo frío #F8FAFF."},
        {"name": "Dark developer", "primary": "#22D3EE", "secondary": "#06B6D4", "accent": "#67E8F9",
         "surface": "#030712", "text": "#F9FAFB",
         "chip_text": "Colores: fondo casi negro #030712, cyan brillante #22D3EE, acento #67E8F9."},
    ],
    "restaurant": [
        {"name": "Carbón & oro", "primary": "#B7791F", "secondary": "#92400E", "accent": "#F59E0B",
         "surface": "#1C1917", "text": "#FEF3C7",
         "chip_text": "Colores: fondo carbón #1C1917, dorado #B7791F, acento ámbar #F59E0B, texto crema."},
        {"name": "Rojo pasión", "primary": "#DC2626", "secondary": "#991B1B", "accent": "#FCA5A5",
         "surface": "#FFF5F5", "text": "#1C1917",
         "chip_text": "Colores: rojo #DC2626, rojo oscuro #991B1B, acento rosado #FCA5A5, fondo crema."},
        {"name": "Mediterráneo", "primary": "#2563EB", "secondary": "#1D4ED8", "accent": "#F97316",
         "surface": "#FFFBF0", "text": "#1E3A5F",
         "chip_text": "Colores: azul mediterráneo #2563EB, naranja acento #F97316, fondo cálido #FFFBF0."},
    ],
    "cafe": [
        {"name": "Café & crema", "primary": "#78350F", "secondary": "#451A03", "accent": "#D97706",
         "surface": "#FFFBEB", "text": "#1C1917",
         "chip_text": "Colores: marrón café #78350F, marrón oscuro #451A03, ámbar #D97706, crema #FFFBEB."},
        {"name": "Verde matcha", "primary": "#166534", "secondary": "#14532D", "accent": "#4ADE80",
         "surface": "#F0FDF4", "text": "#14532D",
         "chip_text": "Colores: verde oscuro #166534, acento verde brillante #4ADE80, fondo menta #F0FDF4."},
    ],
    "hotel": [
        {"name": "Lujo neutro", "primary": "#44403C", "secondary": "#1C1917", "accent": "#D4AF37",
         "surface": "#FAFAF9", "text": "#1C1917",
         "chip_text": "Colores: piedra #44403C, acento dorado #D4AF37, fondo casi blanco #FAFAF9."},
        {"name": "Azul marino", "primary": "#1E3A5F", "secondary": "#0F2044", "accent": "#C9A84C",
         "surface": "#F8F8F6", "text": "#0F2044",
         "chip_text": "Colores: azul marino #1E3A5F, dorado acento #C9A84C, fondo marfil #F8F8F6."},
    ],
    "wellness": [
        {"name": "Tierra & salvia", "primary": "#4A7C59", "secondary": "#2D5016", "accent": "#A3B18A",
         "surface": "#F9F6F0", "text": "#2D3A1E",
         "chip_text": "Colores: verde salvia #4A7C59, oliva #A3B18A, fondo crema #F9F6F0, tierra."},
        {"name": "Lavanda paz", "primary": "#7C3AED", "secondary": "#5B21B6", "accent": "#C4B5FD",
         "surface": "#FAF5FF", "text": "#2E1065",
         "chip_text": "Colores: lavanda #7C3AED, violeta suave #C4B5FD, fondo lila #FAF5FF."},
    ],
    "fitness": [
        {"name": "Negro & energía", "primary": "#EF4444", "secondary": "#B91C1C", "accent": "#FCD34D",
         "surface": "#0A0A0A", "text": "#F9FAFB",
         "chip_text": "Colores: negro #0A0A0A, rojo energía #EF4444, amarillo acento #FCD34D, texto blanco."},
        {"name": "Naranja potencia", "primary": "#EA580C", "secondary": "#9A3412", "accent": "#FB923C",
         "surface": "#111111", "text": "#FFFFFF",
         "chip_text": "Colores: naranja #EA580C, naranja claro #FB923C, fondo oscuro #111111."},
    ],
    "healthcare": [
        {"name": "Azul salud", "primary": "#0369A1", "secondary": "#0C4A6E", "accent": "#7DD3FC",
         "surface": "#F0F9FF", "text": "#0C2340",
         "chip_text": "Colores: azul médico #0369A1, azul marino #0C4A6E, celeste #7DD3FC, fondo #F0F9FF."},
        {"name": "Verde confianza", "primary": "#059669", "secondary": "#064E3B", "accent": "#6EE7B7",
         "surface": "#F0FDF4", "text": "#022C22",
         "chip_text": "Colores: verde salud #059669, acento menta #6EE7B7, fondo claro #F0FDF4."},
    ],
    "fashion": [
        {"name": "Noir & blanc", "primary": "#0A0A0A", "secondary": "#18181B", "accent": "#D4AF37",
         "surface": "#FFFFFF", "text": "#0A0A0A",
         "chip_text": "Colores: negro #0A0A0A, blanco puro #FFFFFF, acento dorado #D4AF37. Editorial."},
        {"name": "Beis & tierra", "primary": "#8B6F47", "secondary": "#5C4A2A", "accent": "#D4B896",
         "surface": "#FAF7F2", "text": "#2D2010",
         "chip_text": "Colores: beis tierra #8B6F47, arena #D4B896, fondo crema cálido #FAF7F2."},
    ],
    "automotive": [
        {"name": "Racing negro", "primary": "#EF4444", "secondary": "#7F1D1D", "accent": "#FBBF24",
         "surface": "#0A0A0A", "text": "#F9FAFB",
         "chip_text": "Colores: negro #0A0A0A, rojo racing #EF4444, acento amarillo #FBBF24."},
        {"name": "Titanio BMW", "primary": "#1C4ED8", "secondary": "#1E3A8A", "accent": "#93C5FD",
         "surface": "#0F172A", "text": "#F8FAFC",
         "chip_text": "Colores: azul BMW #1C4ED8, fondo oscuro #0F172A, acento celeste #93C5FD."},
    ],
    "education": [
        {"name": "Azul académico", "primary": "#1D4ED8", "secondary": "#1E3A8A", "accent": "#FCD34D",
         "surface": "#F8FAFF", "text": "#0F172A",
         "chip_text": "Colores: azul academia #1D4ED8, amarillo acento #FCD34D, fondo claro #F8FAFF."},
        {"name": "Colorido amigable", "primary": "#7C3AED", "secondary": "#2563EB", "accent": "#F59E0B",
         "surface": "#FAFAFA", "text": "#111827",
         "chip_text": "Colores: violeta #7C3AED, azul #2563EB, ámbar #F59E0B, fondo neutro. Vibrante y amigable."},
    ],
    "realestate": [
        {"name": "Tierra premium", "primary": "#92400E", "secondary": "#451A03", "accent": "#D97706",
         "surface": "#FFFBEB", "text": "#1C1917",
         "chip_text": "Colores: ámbar profundo #92400E, dorado #D97706, fondo crema cálido #FFFBEB."},
        {"name": "Azul corporativo", "primary": "#1E3A5F", "secondary": "#0F2044", "accent": "#3B82F6",
         "surface": "#F8FAFF", "text": "#0F172A",
         "chip_text": "Colores: azul marino #1E3A5F, azul acento #3B82F6, fondo frío #F8FAFF."},
    ],
    "legal": [
        {"name": "Azul autoridad", "primary": "#1E3A5F", "secondary": "#0F2044", "accent": "#C9A84C",
         "surface": "#F8F8F6", "text": "#0F2044",
         "chip_text": "Colores: azul marino profundo #1E3A5F, acento dorado #C9A84C, fondo marfil #F8F8F6."},
        {"name": "Gris ejecutivo", "primary": "#374151", "secondary": "#111827", "accent": "#6B7280",
         "surface": "#FAFAFA", "text": "#111827",
         "chip_text": "Colores: gris oscuro #374151, casi negro #111827, fondo muy claro #FAFAFA."},
    ],
    "ecommerce": [
        {"name": "Naranja acción", "primary": "#EA580C", "secondary": "#9A3412", "accent": "#FCD34D",
         "surface": "#FFFFFF", "text": "#111827",
         "chip_text": "Colores: naranja CTA #EA580C, amarillo acento #FCD34D, fondo blanco. Conversión alta."},
        {"name": "Verde tienda", "primary": "#059669", "secondary": "#065F46", "accent": "#34D399",
         "surface": "#F9FAFB", "text": "#111827",
         "chip_text": "Colores: verde confianza #059669, acento menta #34D399, fondo gris claro #F9FAFB."},
    ],
}

# Paletas genéricas para fallback
_DEFAULT_PALETTES = [
    {"name": "Índigo & blanco", "primary": "#4F46E5", "secondary": "#3730A3", "accent": "#818CF8",
     "surface": "#FAFAFA", "text": "#111827",
     "chip_text": "Colores: índigo principal #4F46E5, acento #818CF8, fondo claro #FAFAFA."},
    {"name": "Dark elegante", "primary": "#818CF8", "secondary": "#6366F1", "accent": "#F472B6",
     "surface": "#0A0A0F", "text": "#F9FAFB",
     "chip_text": "Colores: modo oscuro #0A0A0F, violeta #818CF8, rosa acento #F472B6, texto blanco."},
    {"name": "Verde & neutral", "primary": "#059669", "secondary": "#065F46", "accent": "#6EE7B7",
     "surface": "#FAFAFA", "text": "#111827",
     "chip_text": "Colores: verde #059669, menta #6EE7B7, fondo neutro #FAFAFA."},
]


def get_palettes_for_industry(industry: str) -> list[dict]:
    return _INDUSTRY_PALETTES.get(industry, _DEFAULT_PALETTES)[:3]


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def analyze_brief(brief: str) -> dict:
    """
    Análisis completo de un brief. Retorna dict con todas las sugerencias.
    Sin Gemini, sin IO, sin red. Puro Python < 50ms.
    """
    kw = translate_brief_to_keywords(brief)
    industry = kw.industry
    confidence = kw.confidence

    return {
        "industry": industry,
        "confidence": round(confidence, 2),
        "missing": detect_missing(brief),
        "styles": get_styles_for_industry(industry, brief),
        "templates": get_templates_for_industry(industry),
        "palettes": get_palettes_for_industry(industry),
    }
