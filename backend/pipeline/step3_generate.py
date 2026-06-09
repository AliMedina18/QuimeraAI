import asyncio
import logging
import os
import re
import requests
from models import DesignContext
from services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CURATED UNSPLASH PHOTO IDs BY INDUSTRY
# Format: https://images.unsplash.com/photo-{ID}?w=W&h=H&fit=crop&auto=format
# These are permanent URLs, no API key needed.
# ---------------------------------------------------------------------------
CURATED_PHOTOS = {
    # --- Food & Restaurant ---
    "sushi": {
        "hero":    "1579871494447-9811cf80d66c",  # sushi platter dark bg
        "hero2":   "1617196034183-421b4040ed20",  # sushi close-up
        "card1":   "1553621042-f6e147245754",      # nigiri
        "card2":   "1569050467447-ce54b3bbc37d",  # japanese food spread
        "card3":   "1562802378-063ec186a863",      # ramen bowl
        "card4":   "1540189309485-53f81c76df70",  # sashimi
        "card5":   "1611143669185-af224c5e3252",  # maki rolls
        "card6":   "1574484284002-952d92456975",  # sushi chef
        "section": "1414235077428-338989a2e8c0",  # restaurant ambiance
    },
    "restaurante": {
        "hero":    "1414235077428-338989a2e8c0",  # elegant restaurant
        "hero2":   "1517248135467-4c7edcad34c4",  # restaurant interior
        "card1":   "1504674900247-0877df9cc836",  # food plate
        "card2":   "1565299585323-38d6b0865b47",  # pasta
        "card3":   "1567620905732-2d1ec7ab7445",  # pizza
        "card4":   "1551782045-a5f838d9f5d3",      # steak
        "card5":   "1600891964599-f61ba0e24092",  # salad
        "card6":   "1482049016688-2d3e1291311a",  # breakfast
        "section": "1559339352-11d035aa65ce",      # chef cooking
    },
    "cafe": {
        "hero":    "1447933601403-0c6688de566e",  # coffee shop
        "hero2":   "1509042239860-f550ce710b93",  # latte art
        "card1":   "1495474472287-4d71bcdd2085",  # espresso
        "card2":   "1533827432537-1e9a2c3e4b7b",  # barista
        "card3":   "1519219788971-8d9797fe8897",  # coffee beans
        "card4":   "1486427944299-d1955d23e17d",  # cake slice
        "card5":   "1501339847302-ac426a4a7cbb",  # cafe interior
        "card6":   "1513558161293-cdaf765ed8fb",  # avocado toast
        "section": "1559056189-fe9c7fda55c1",      # cozy cafe
    },
    # --- Tech & SaaS ---
    "tech": {
        "hero":    "1518770660439-4636190af475",  # circuit board
        "hero2":   "1451187580459-43490279c0fa",  # earth tech
        "card1":   "1551288049-bebda4e38f71",      # laptop data
        "card2":   "1504384308090-c894fdcc538d",  # office coworking
        "card3":   "1497366216548-37526070297c",  # modern office
        "card4":   "1526374965328-7f61d4dc18c5",  # code screen
        "card5":   "1581092921461-eab10380ed66",  # servers
        "card6":   "1573164713988-8665fc963095",  # robot AI
        "section": "1485827404703-89b55fcc595e",  # future tech
    },
    "saas": {
        "hero":    "1551434678-e076c223a692",      # dashboard UI
        "hero2":   "1498050108023-c5249f4df085",  # laptop coding
        "card1":   "1611532736597-de2d4265fba3",  # analytics
        "card2":   "1504384308090-c894fdcc538d",  # team coworking
        "card3":   "1460925895917-afdab827c52f",  # growth chart
        "card4":   "1556155092-490a1ba16284",      # mobile app
        "card5":   "1551288049-bebda4e38f71",      # data visualization
        "card6":   "1497366811353-6870744d04b2",  # office meeting
        "section": "1553877522-43269d4ea984",      # collaboration
    },
    "fintech": {
        "hero":    "1620714223084-8fcacc2107b5",  # digital finance
        "hero2":   "1611974789855-9c2a0a7236a3",  # crypto
        "card1":   "1460925895917-afdab827c52f",  # charts
        "card2":   "1563986768609-322da13575f3",  # payment
        "card3":   "1611532736597-de2d4265fba3",  # analytics dark
        "card4":   "1605792657660-596af9009e82",  # phone banking
        "card5":   "1534951009808-766178b47a4f",  # coins
        "card6":   "1551434678-e076c223a692",      # fintech dashboard
        "section": "1520594923568-7ceff76a4ee3",  # financial city
    },
    # --- Lifestyle ---
    "fitness": {
        "hero":    "1517836357463-d25dfeac3438",  # gym workout
        "hero2":   "1549060279-7e168fcee0c2",      # running
        "card1":   "1571019613576-2b22c76fd955",  # weight training
        "card2":   "1566351557863-467aab31fe49",  # yoga
        "card3":   "1574680096145-d05b474e2155",  # crossfit
        "card4":   "1591311590757-9b1c5ea42c49",  # swimming
        "card5":   "1544367567-0f2fcb009e0b",      # cycling
        "card6":   "1552674605-db5fecabfe68",      # sports nutrition
        "section": "1558611439-36efce2638b2",      # athlete outdoors
    },
    "wellness": {
        "hero":    "1540555700478-4be290a303f5",  # spa candles
        "hero2":   "1506126613408-eca07ce68773",  # meditation
        "card1":   "1519823551278-64ac92734fb1",  # yoga mat
        "card2":   "1515377905703-c4788e51af15",  # essential oils
        "card3":   "1547592166-23ac45744acd",      # massage
        "card4":   "1512290923902-8a9f81dc236c",  # tea ceremony
        "card5":   "1571019613454-1cb2f99b2d8b",  # nature walk
        "card6":   "1556228578-8c89e6adf883",      # healthy food
        "section": "1508739773434-c26b3d09e071",  # peaceful nature
    },
    "travel": {
        "hero":    "1469474968028-56623f02e42e",  # landscape horizon
        "hero2":   "1476514525535-07fb3b4ae5f1",  # city at night
        "card1":   "1530521954074-e0a03810b15a",  # beach
        "card2":   "1502786129-2351a4ac7b4a",      # mountains
        "card3":   "1513635269975-59663e0ac1ad",  # European city
        "card4":   "1506905925346-21bda4d32df4",  # airplane window
        "card5":   "1508739773434-c26b3d09e071",  # tropical
        "card6":   "1493246507139-91e8fad9978e",  # adventure
        "section": "1477959858617-67f85cf4f1df",  # city skyline
    },
    # --- Premium / Luxury ---
    "inmobiliaria": {
        "hero":    "1600596542815-0c7bf8e7af73",  # luxury house
        "hero2":   "1512917774080-9991f1c7f6b6",  # modern interior
        "card1":   "1556228578-8c89e6adf883",      # minimalist room
        "card2":   "1600566752355-35792bedcfea",  # modern kitchen
        "card3":   "1560185893-a55a847d9a08",      # outdoor pool
        "card4":   "1568605114967-8130f3a36994",  # living room
        "card5":   "1616137422495-1e9e46e2aa1b",  # architecture
        "card6":   "1502005097973-24a506b2e285",  # estate exterior
        "section": "1600607687939-ce8a6c25a745",  # luxury lifestyle
    },
    "hotel": {
        "hero":    "1571896349842-33c89424de2d",  # luxury hotel lobby
        "hero2":   "1551882547-ff40c599fb5d",      # hotel pool
        "card1":   "1578683010236-d5bfe2632bbd",  # hotel room
        "card2":   "1555396273-367ea4eb4db5",      # restaurant hotel
        "card3":   "1534430480872-3498386e7856",  # spa hotel
        "card4":   "1560347876-aeef00ee58a1",      # suite
        "card5":   "1564501049412-61d2ad2b1ebd",  # gym hotel
        "card6":   "1566073771259-470de1bed0ce",  # hotel bar
        "section": "1520250497591-112f2f40a3f4",  # aerial hotel
    },
    # --- Fashion ---
    "fashion": {
        "hero":    "1558618666-fcd25c85cd64",      # fashion model
        "hero2":   "1509631179647-0177331693ae",  # runway
        "card1":   "1539109136881-3be0616acf4b",  # clothing
        "card2":   "1490481651871-ab68de25d43d",  # shoes
        "card3":   "1469334031218-e382a71b716b",  # accessories
        "card4":   "1445205170230-053b83016050",  # handbag
        "card5":   "1515886657613-9f3515b0c78f",  # model closeup
        "card6":   "1467043237213-65f2da53396f",  # street style
        "section": "1558618047-3c8c76ca7d13",      # editorial fashion
    },
}

# Fallback: picsum.photos with descriptive seeds (always works)
def _picsum(seed: str, w: int, h: int) -> str:
    return f"https://picsum.photos/seed/{seed}/{w}/{h}"

# Curated Unsplash URL builder
def _unsplash(photo_id: str, w: int, h: int) -> str:
    return f"https://images.unsplash.com/photo-{photo_id}?w={w}&h={h}&fit=crop&auto=format&q=80"

# Curated portrait photos for avatars
AVATAR_PHOTOS = [
    "1507003211169-0a1dd7228f2d",  # man professional
    "1494790108377-be9c29b29330",  # woman professional
    "1438761681033-6461ffad8d80",  # woman smiling
    "1472099645785-5658abf4ff4e",  # man casual
    "1544005313-94ddf0286df2",      # woman casual
]


def _extract_keywords(brief: str) -> str:
    """Extrae 2-3 keywords relevantes del brief para buscar imágenes."""
    # Remove common filler words
    stop = {
        "para", "una", "un", "de", "del", "la", "el", "en", "con", "por", "que",
        "for", "a", "an", "the", "of", "in", "and", "or", "with", "to", "is",
        "create", "crea", "make", "sitio", "web", "website", "página", "page",
        "generate", "genera", "diseño", "design", "company", "empresa", "negocio",
        "business", "quiero", "want", "need", "necesito",
    }
    words = re.findall(r'[a-záéíóúüñA-ZÁÉÍÓÚÜÑ]{4,}', brief, re.IGNORECASE)
    filtered = [w for w in words if w.lower() not in stop]
    return " ".join(filtered[:4]) if filtered else brief[:60]


def _fetch_unsplash(query: str, count: int, orientation: str = "landscape") -> list:
    """Llama la Unsplash API. Retorna lista de URLs regulares (1080px)."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not key:
        return []
    try:
        resp = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": query, "count": count, "orientation": orientation},
            headers={"Authorization": f"Client-ID {key}"},
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json()
            return [p["urls"]["regular"] for p in data if "urls" in p]
    except Exception as e:
        logger.warning("Unsplash API error: %s", e)
    return []


async def _get_image_urls(brief: str) -> dict:
    """
    Retorna URLs de imágenes relevantes al brief.
    - Si UNSPLASH_ACCESS_KEY está configurada: usa la API de Unsplash con keywords del brief.
    - Fallback: IDs de Unsplash curados por industria → picsum.photos.
    """
    # --- PATH 1: Unsplash API (universal, qualquer brief) ---
    keywords = _extract_keywords(brief)
    landscape_urls = await asyncio.to_thread(_fetch_unsplash, keywords, 9, "landscape")
    portrait_urls  = await asyncio.to_thread(_fetch_unsplash, keywords, 3, "portrait")

    if len(landscape_urls) >= 9:
        return {
            "hero":       landscape_urls[0],
            "hero_alt":   landscape_urls[1],
            "section_bg": landscape_urls[2],
            "card_1":     landscape_urls[3],
            "card_2":     landscape_urls[4],
            "card_3":     landscape_urls[5],
            "card_4":     landscape_urls[6],
            "card_5":     landscape_urls[7],
            "card_6":     landscape_urls[8],
            "avatar_1":   portrait_urls[0] if len(portrait_urls) > 0 else _unsplash(AVATAR_PHOTOS[0], 200, 200),
            "avatar_2":   portrait_urls[1] if len(portrait_urls) > 1 else _unsplash(AVATAR_PHOTOS[1], 200, 200),
            "avatar_3":   portrait_urls[2] if len(portrait_urls) > 2 else _unsplash(AVATAR_PHOTOS[2], 200, 200),
        }

    # --- PATH 2: Curated Unsplash IDs by industry ---
    brief_l = brief.lower()
    
    # Match industry from brief
    matched_industry = None
    for industry in CURATED_PHOTOS:
        if industry in brief_l:
            matched_industry = industry
            break
    
    # Fallback heuristics
    if not matched_industry:
        if any(w in brief_l for w in ["restaurant", "food", "eat", "menu", "chef"]):
            matched_industry = "restaurante"
        elif any(w in brief_l for w in ["hotel", "resort", "stay", "accommodation"]):
            matched_industry = "hotel"
        elif any(w in brief_l for w in ["fitness", "gym", "workout", "sport"]):
            matched_industry = "fitness"
        elif any(w in brief_l for w in ["spa", "wellness", "yoga", "meditation"]):
            matched_industry = "wellness"
        elif any(w in brief_l for w in ["tech", "software", "app", "platform", "saas"]):
            matched_industry = "saas"
        elif any(w in brief_l for w in ["finance", "bank", "payment", "crypto"]):
            matched_industry = "fintech"
        elif any(w in brief_l for w in ["travel", "trip", "vacation", "tour"]):
            matched_industry = "travel"
        elif any(w in brief_l for w in ["fashion", "clothes", "clothing", "style"]):
            matched_industry = "fashion"
        elif any(w in brief_l for w in ["real estate", "inmobiliaria", "property", "apartment"]):
            matched_industry = "inmobiliaria"
    
    if matched_industry and matched_industry in CURATED_PHOTOS:
        ids = CURATED_PHOTOS[matched_industry]
        urls = {
            "hero":      _unsplash(ids["hero"], 1600, 900),
            "hero_alt":  _unsplash(ids["hero2"], 1600, 900),
            "section_bg": _unsplash(ids["section"], 1400, 800),
            "card_1":    _unsplash(ids["card1"], 800, 600),
            "card_2":    _unsplash(ids["card2"], 800, 600),
            "card_3":    _unsplash(ids["card3"], 800, 600),
            "card_4":    _unsplash(ids["card4"], 800, 600),
            "card_5":    _unsplash(ids["card5"], 800, 600),
            "card_6":    _unsplash(ids["card6"], 800, 600),
        }
    else:
        # Generic beautiful photos via picsum
        urls = {
            "hero":       _picsum("nature-landscape-hero", 1600, 900),
            "hero_alt":   _picsum("architecture-modern", 1600, 900),
            "section_bg": _picsum("city-night-lights", 1400, 800),
            "card_1":     _picsum("product-minimal-1", 800, 600),
            "card_2":     _picsum("product-minimal-2", 800, 600),
            "card_3":     _picsum("product-minimal-3", 800, 600),
            "card_4":     _picsum("product-minimal-4", 800, 600),
            "card_5":     _picsum("product-minimal-5", 800, 600),
            "card_6":     _picsum("product-minimal-6", 800, 600),
        }
    
    # Always add avatar portraits
    urls["avatar_1"] = _unsplash(AVATAR_PHOTOS[0], 200, 200)
    urls["avatar_2"] = _unsplash(AVATAR_PHOTOS[1], 200, 200)
    urls["avatar_3"] = _unsplash(AVATAR_PHOTOS[2], 200, 200)
    
    return urls


# ---------------------------------------------------------------------------
# DESIGN PRINCIPLES ENGINE  (from Google design.md spec, designmd.app, Stitch)
# ---------------------------------------------------------------------------
DESIGN_PRINCIPLES = (
    "=== VISUAL COMPOSITION LAWS ===\n"
    "\n"
    "RULE OF THIRDS\n"
    "  Divide the page into a 3x3 grid (3 cols x 3 rows).\n"
    "  Place primary focal points (hero text, CTA) at the 4 intersection points.\n"
    "  Hero section: text occupies left 2/3, visual element occupies right 1/3 (or vice versa).\n"
    "  Never center EVERYTHING — centered layouts feel static. Alternate alignment per section.\n"
    "\n"
    "GESTALT PRINCIPLES\n"
    "  Proximity: Group related elements with small gap (8-16px). Separate groups with large gap (48-80px).\n"
    "  Similarity: Use consistent card size, button style, and icon size within a section.\n"
    "  Continuity: Align text baselines, card tops, and icon centers along invisible grid lines.\n"
    "  Figure-Ground: The primary CTA must visually 'pop' from its background. Use contrast >= 4.5:1.\n"
    "  Closure: Use incomplete shapes (partial circles, cut-off images) to create visual tension.\n"
    "\n"
    "F-PATTERN READING (desktop)\n"
    "  Line 1 (top): Logo left + Nav right + CTA rightmost\n"
    "  Line 2 (hero): Headline starts left, eye scans right\n"
    "  Vertical drop: Left column carries more visual weight\n"
    "  Place key information left-of-center or in first card of a grid.\n"
    "\n"
    "Z-PATTERN READING (landing pages)\n"
    "  Top-left (logo) → Top-right (nav CTA) → diagonal → Bottom-left (feature) → Bottom-right (CTA)\n"
    "  Each section should guide the eye to the next section's starting point.\n"
    "\n"
    "=== TYPOGRAPHY HIERARCHY LAWS ===\n"
    "\n"
    "SCALE RATIO: Use a modular scale (1.25 — Major Third or 1.333 — Perfect Fourth).\n"
    "  base: 16px → sm: 14px → md: 16px → lg: 20px → xl: 25px → 2xl: 31px → 3xl: 39px → 4xl: 49px\n"
    "\n"
    "HIERARCHY RULES:\n"
    "  Display (hero): clamp(2.5rem, 6vw, 5rem). Weight 700-800. Letter-spacing: -0.03em to -0.05em.\n"
    "  Headline (sections): clamp(1.75rem, 3.5vw, 2.75rem). Weight 600-700. Letter-spacing: -0.02em.\n"
    "  Subheadline: clamp(1.1rem, 2vw, 1.4rem). Weight 400-500. Normal letter-spacing.\n"
    "  Body: 16-18px. Weight 400. Line-height 1.6-1.75. Letter-spacing: 0 to 0.01em.\n"
    "  Caption/Label: 12-14px. Weight 500-600. Letter-spacing: 0.04em to 0.1em. Often UPPERCASE.\n"
    "\n"
    "CONTRAST RULES:\n"
    "  NEVER put similar-sized text of similar weights adjacent (headline vs subheadline).\n"
    "  Minimum 2x size difference between heading levels.\n"
    "  One dominant font family for headings, optionally different for body.\n"
    "\n"
    "=== SPACING & LAYOUT RHYTHM ===\n"
    "\n"
    "8px BASE GRID: All padding, margin, gap must be multiples of 8 (8, 16, 24, 32, 48, 64, 96, 128px).\n"
    "\n"
    "SECTION BREATHING ROOM:\n"
    "  Section padding: min 80px top/bottom desktop, 48px mobile.\n"
    "  Card internal padding: 24-32px.\n"
    "  Between headline and body: 16-24px.\n"
    "  Between body and CTA: 32-40px.\n"
    "\n"
    "MAX-WIDTH CONTAINERS:\n"
    "  Full-bleed: images, hero backgrounds, section color fills (100vw)\n"
    "  Content: max-width 1200px, centered with padding 0 24px\n"
    "  Narrow (articles): max-width 720px\n"
    "\n"
    "=== COLOR APPLICATION HIERARCHY ===\n"
    "\n"
    "PRIMARY COLOR: Use for ONE thing per screen — the most important CTA.\n"
    "  Buttons: background-color: primary. Hover: brightness(1.1) or darken 10%.\n"
    "  Accent text: sparingly, max 2-3 words per paragraph.\n"
    "  Borders/underlines: section dividers, card hover borders.\n"
    "\n"
    "SECONDARY COLOR: Badges, tags, icon fills, progress bars, secondary CTAs.\n"
    "\n"
    "SURFACE HIERARCHY (light theme):\n"
    "  canvas (#fff or near-white): page background\n"
    "  surface-soft (slightly off-white): alternating section backgrounds\n"
    "  card (white or surface): card backgrounds, slightly elevated\n"
    "\n"
    "SURFACE HIERARCHY (dark theme):\n"
    "  background: darkest surface\n"
    "  surface: slightly lighter (cards, panels)\n"
    "  surface-elevated: hover state, modals\n"
    "\n"
    "CONTRAST REQUIREMENTS (WCAG AA):\n"
    "  Normal text (<18px): 4.5:1 minimum\n"
    "  Large text (>18px bold): 3:1 minimum\n"
    "  UI components (buttons, inputs): 3:1 minimum\n"
    "\n"
    "=== COMPONENT DESIGN PATTERNS ===\n"
    "\n"
    "HERO SECTION (full-viewport):\n"
    "  Background: CSS background-image with linear-gradient overlay (NOT filter on <img>)\n"
    "  Overlay: linear-gradient(to bottom, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.7) 100%)\n"
    "  Content: centered or left-aligned (per rule of thirds)\n"
    "  Text: white, display size, tight tracking\n"
    "  Two CTAs: primary (solid) + secondary (ghost/outline)\n"
    "  Optional: floating card with stat or rating (adds depth)\n"
    "\n"
    "CARD DESIGN:\n"
    "  Image: aspect-ratio 4/3 or 16/9, object-fit cover. On hover: scale(1.05).\n"
    "  Body: 24px padding. Title bold 18-20px. Description 14-16px muted. CTA link at bottom.\n"
    "  Hover: translateY(-6px) + enhanced shadow (not just color change).\n"
    "  Border: 1px solid rgba(0,0,0,0.07) — visible but not distracting.\n"
    "\n"
    "NAVIGATION:\n"
    "  Fixed: position fixed, starts transparent, gets background on scroll.\n"
    "  Height: 64-72px. Logo: 160-200px wide. Links: 16px regular, 400-500 weight.\n"
    "  CTA in nav: contrasting button, not just a link.\n"
    "  Mobile: hamburger at 768px, fullscreen overlay or slide-in panel.\n"
    "\n"
    "TESTIMONIALS:\n"
    "  Card: white background, 24px padding, subtle shadow.\n"
    "  Avatar: 56px circle with brand-color border.\n"
    "  Quote: 16-18px, italic, line-height 1.7. Name: bold. Role: muted caption.\n"
    "  Stars: use CSS-drawn stars or Unicode ★ in primary color.\n"
    "\n"
    "FORMS:\n"
    "  Labels: above inputs, 14px medium weight, 8px margin-bottom.\n"
    "  Inputs: 48px height, 16px padding, 8px radius. Border: 1.5px solid.\n"
    "  Focus: primary-color border + 0 0 0 3px primary-color at 20% opacity.\n"
    "  Submit: full-width on mobile, 200px min-width on desktop.\n"
)


# ---------------------------------------------------------------------------
# SYSTEM PROMPT — Premium HTML generation engine
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a senior UI/UX engineer and visual designer producing award-winning websites.\n"
    "You have mastered visual composition, typography hierarchy, color theory, and CSS engineering.\n"
    "Your designs are indistinguishable from Stripe, Linear, Airbnb, or Apple marketing pages.\n"
    "\n"
    + DESIGN_PRINCIPLES +
    "\n"
    "=== HTML GENERATION RULES ===\n"
    "\n"
    "1. READ THE DESIGN.MD PROSE FIRST — identify the visual reference/mood before writing CSS.\n"
    "   'glassmorphism' => frosted-glass panels, blur, semi-transparent borders.\n"
    "   'editorial' => asymmetric layout, strong type, large whitespace.\n"
    "   'warm & premium' => earth tones, generous padding, serif accents.\n"
    "   NEVER collapse a rich prose description into a generic equal-column Tailwind grid.\n"
    "\n"
    "2. IMAGES — ALL PROVIDED URLs MUST BE USED\n"
    "   Hero background: CSS background-image on .hero-bg div. NOT a raw <img>.\n"
    "   Cards: <img src='card_N_url'> inside .card-image-wrap div.\n"
    "   Avatars: <img src='avatar_N_url'> in 56px circle.\n"
    "   section_bg: CSS background-image on section with ::before pseudo-overlay.\n"
    "   NEVER use placeholder.com or empty src.\n"
    "\n"
    "3. EVERY CSS value must use the token custom properties (--color-primary, etc.).\n"
    "4. NEVER use Tailwind for card hover states, transitions, or typography — use custom CSS.\n"
    "5. Tailwind CDN optional for grid/flex utilities only.\n"
    "\n"
    "=== OUTPUT FORMAT ===\n"
    "First line: <!DOCTYPE html>  Last line: </html>\n"
    "CSS in <style>. JS in <script> at end of <body>. Google Fonts via <link>.\n"
    "No markdown, no explanations.\n"
)


# ---------------------------------------------------------------------------
# MAIN PIPELINE STEP
# ---------------------------------------------------------------------------
async def generate_code(context: DesignContext) -> DesignContext:
    """
    PASO 3 v5: HTML premium desde DESIGN.md completo + imágenes reales.
    - Pasa DESIGN.md COMPLETO (prose + tokens)
    - IDs de Unsplash curados por industria (URLs permanentes)
    - Patterns CSS premium en system prompt
    - Temperatura 0.4
    """
    if not context.design_markdown:
        raise ValueError("DESIGN.md no encontrado")

    logger.info("PASO 3 v5: Generando HTML premium...")

    client = GeminiClient()
    image_urls = await _get_image_urls(context.design_brief)

    img_lines = "\n".join(f"  {k}: {v}" for k, v in image_urls.items())

    user_prompt = (
        f"Generate a COMPLETE, PRODUCTION-READY HTML website for this brief.\n\n"
        f"=== BRIEF ===\n{context.design_brief}\n\n"
        f"=== DESIGN.MD (this is your SPEC — implement it faithfully) ===\n"
        f"{context.design_markdown}\n\n"
        f"=== IMAGES — use ALL of these exact URLs, zero broken ===\n"
        f"{img_lines}\n\n"
        f"=== HOW TO BUILD THIS SITE ===\n\n"
        f"PHASE 1 — READ THE DESIGN.MD OVERVIEW\n"
        f"Before writing a single line of CSS, read the Overview prose.\n"
        f"Answer: What TYPE of website is this? (restaurant, SaaS, law firm, portfolio, etc.)\n"
        f"Answer: What VISUAL REFERENCE was chosen? (glassmorphism? editorial? luxury? minimal?)\n"
        f"Answer: What ELEVATION style? (tonal layers, shadows, blur, flat?)\n"
        f"These answers determine EVERY CSS decision below.\n\n"
        f"PHASE 2 — DECIDE THE PAGE STRUCTURE\n"
        f"Based on the brief and Overview, choose sections that fit THIS specific site.\n"
        f"Do NOT use a generic template. Ask: what does this business actually need?\n"
        f"Examples of site-appropriate structures:\n"
        f"  Restaurant: Hero > Menu Highlights > Chef Story > Gallery > Reservations > Footer\n"
        f"  SaaS:       Hero > Features > How It Works > Pricing > Testimonials > CTA > Footer\n"
        f"  Law Firm:   Hero > Practice Areas > Team > Case Results > Contact > Footer\n"
        f"  Portfolio:  Hero > Work Grid > About > Services > Contact > Footer\n"
        f"  E-commerce: Hero > Featured Products > Categories > Why Us > Newsletter > Footer\n"
        f"  Wellness:   Hero > Services > Philosophy > Team > Testimonials > Booking > Footer\n"
        f"Choose the right structure for THIS brief. The DESIGN.md components section hints at what exists.\n\n"
        f"PHASE 3 — CSS FOUNDATION (always required)\n"
        f"a) :root variables: every YAML token becomes a CSS custom property.\n"
        f"   --color-primary, --color-surface, --font-display, --radius-card, --spacing-lg, etc.\n"
        f"b) Load Google Fonts matching fontFamily tokens (via <link> in <head>).\n"
        f"c) Implement elevation from prose: if glassmorphism use backdrop-filter+alpha;\n"
        f"   if tonal use surface-container-* levels; if shadows define box-shadow scale.\n"
        f"PHASE 4 — IMPLEMENT EACH SECTION (use these CSS techniques)\n"
        f"Typography scale: clamp() for responsive text.\n"
        f"  Hero display: clamp(2.8rem,6vw,5.5rem), weight 700-800, letter-spacing -0.04em\n"
        f"  Section headline: clamp(1.75rem,3.5vw,2.75rem), weight 600-700\n"
        f"  Body: 16-18px, weight 400, line-height 1.6-1.75\n"
        f"  Caption/label: 12-14px, weight 500-600, letter-spacing 0.04em\n"
        f"Composition: apply rule of thirds — alternate left/right/center alignment per section.\n"
        f"Cards: aspect-ratio:4/3, overflow:hidden, hover translateY(-6px) + shadow + img scale(1.05)\n"
        f"Hero background: CSS background-image on a .hero-bg div + gradient overlay for contrast.\n"
        f"Sections: min 80px padding top/bottom (48px mobile). Max-width 1200px content container.\n"
        f"Avatars if testimonials: 56px circle, 2px primary-color border.\n"
        f"Inputs if forms: 48px height, var(--color-primary) focus ring.\n\n"
        f"PHASE 5 — JAVASCRIPT\n"
        f"a) IntersectionObserver: .fade-in elements get .visible class on viewport entry.\n"
        f"b) Navbar: .scrolled class at scrollY > 50 (opaque bg + blur).\n"
        f"c) Mobile menu toggle if navbar present.\n"
        f"d) html {{ scroll-behavior: smooth; }}\n\n"
        f"=== QUALITY CHECKLIST ===\n"
        f"[ ] Sections chosen match the brief (not a generic layout)\n"
        f"[ ] All DESIGN.md color tokens used correctly\n"
        f"[ ] All image URLs from the list used (no broken images)\n"
        f"[ ] Elevation style from prose implemented (not default shadows)\n"
        f"[ ] Every section: min 80px padding, proper heading hierarchy\n"
        f"[ ] Font loaded via Google Fonts and applied via CSS variables\n"
        f"[ ] WCAG AA contrast: text on backgrounds passes 4.5:1\n\n"
        f"OUTPUT: Only raw HTML. First line <!DOCTYPE html>. Last line </html>. No markdown.\n"
    )

    full_prompt = SYSTEM_PROMPT + "\n\n" + user_prompt

    # Use Pro for complex design generation (Flash struggles with visual instructions)
    html_output = await client.generate_text(
        prompt=full_prompt,
        model="pro",
        temperature=0.35,
    )

    context.html_output = html_output
    logger.info("PASO 3 v5: HTML generado (%d chars)", len(html_output))
    return context