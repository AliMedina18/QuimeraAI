"""
image_generator.py — Proveedor de imágenes para el pipeline de Quimera
=======================================================================
Fuente única de verdad para URLs de imágenes en step3_generate.py.

Estrategia en cascada:
  PATH 1 — Unsplash API (si UNSPLASH_ACCESS_KEY está configurada)
  PATH 2 — IDs de Unsplash curados por industria (URLs permanentes, sin API key)
  PATH 3 — picsum.photos con seed contextual (fallback siempre disponible)

Uso:
    from services.image_generator import get_image_urls
    urls = await get_image_urls(brief)
    # → {"hero": "https://...", "card_1": "https://...", ...}
"""

import asyncio
import logging
import os
import re
from typing import Optional, Tuple

import requests

logger = logging.getLogger(__name__)

# CURATED UNSPLASH PHOTO IDs BY INDUSTRY
# Format: https://images.unsplash.com/photo-{ID}?w=W&h=H&fit=crop&auto=format
# These are permanent URLs, no API key needed.

CURATED_PHOTOS = {
    # --- Food & Restaurant ---
    "sushi": {
        "hero":    "1579871494447-9811cf80d66c",  # sushi platter dark bg
        "hero2":   "1563245372-f21724e3856d",      # sushi close-up
        "card1":   "1553621042-f6e147245754",      # nigiri
        "card2":   "1569050467447-ce54b3bbc37d",  # japanese food spread
        "card3":   "1562802378-063ec186a863",      # ramen bowl
        "card4":   "1568901346375-23c9450c58cd",  # sashimi
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
        "card4":   "1600803907087-f56d462fd26b",  # food dish
        "card5":   "1600891964599-f61ba0e24092",  # salad
        "card6":   "1414235077428-338989a2e8c0",  # breakfast
        "section": "1556909114-f6e7ad7d3136",      # restaurant scene
    },
    "cafe": {
        "hero":    "1447933601403-0c6688de566e",  # coffee shop
        "hero2":   "1509042239860-f550ce710b93",  # latte art
        "card1":   "1495474472287-4d71bcdd2085",  # espresso
        "card2":   "1495474472287-4d71bcdd2085",  # barista
        "card3":   "1509042239860-f550ce710b93",  # coffee beans
        "card4":   "1558618666-fcd25c85cd64",      # cake slice
        "card5":   "1501339847302-ac426a4a7cbb",  # cafe interior
        "card6":   "1512621776951-a57141f2eefd",  # avocado toast
        "section": "1509042239860-f550ce710b93",      # coffee shop warm (repl: deleted photo)
    },
    # --- Tech & SaaS ---
    "tech": {
        "hero":    "1518770660439-4636190af475",  # circuit board
        "hero2":   "1451187580459-43490279c0fa",  # earth tech
        "card1":   "1551288049-bebda4e38f71",      # laptop data
        "card2":   "1504384308090-c894fdcc538d",  # office coworking
        "card3":   "1497366216548-37526070297c",  # modern office
        "card4":   "1526374965328-7f61d4dc18c5",  # code screen
        "card5":   "1558494949-ef010cbdcc31",      # servers
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
        "hero":    "1611974789855-9c2a0a7236a3",  # digital finance
        "hero2":   "1611974789855-9c2a0a7236a3",  # crypto
        "card1":   "1460925895917-afdab827c52f",  # charts
        "card2":   "1563986768609-322da13575f3",  # payment
        "card3":   "1611532736597-de2d4265fba3",  # analytics dark
        "card4":   "1605792657660-596af9009e82",  # phone banking
        "card5":   "1534951009808-766178b47a4f",  # coins
        "card6":   "1551434678-e076c223a692",      # fintech dashboard
        "section": "1563013544-824ae1b704d3",      # financial city
    },
    # --- Lifestyle ---
    "fitness": {
        "hero":    "1517836357463-d25dfeac3438",  # gym workout
        "hero2":   "1549060279-7e168fcee0c2",      # running
        "card1":   "1571019613576-2b22c76fd955",  # weight training
        "card2":   "1599058917212-d750089bc07e",  # yoga
        "card3":   "1574680096145-d05b474e2155",  # crossfit
        "card4":   "1571019614242-c5c5dee9f50b",  # swimming
        "card5":   "1544367567-0f2fcb009e0b",      # cycling
        "card6":   "1490645935967-10de6ba17061",  # fitness nutrition
        "section": "1476480862126-209bfaa8edc8",  # running street
    },
    "wellness": {
        "hero":    "1544161515-4ab6ce6db874",      # spa candles
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
        "card1":   "1507525428034-b723cf961d3e",  # beach
        "card2":   "1464822759023-fed622ff2c3b",      # mountain lake (repl: deleted photo)
        "card3":   "1513635269975-59663e0ac1ad",  # European city
        "card4":   "1506905925346-21bda4d32df4",  # airplane window
        "card5":   "1508739773434-c26b3d09e071",  # tropical
        "card6":   "1493246507139-91e8fad9978e",  # adventure
        "section": "1477959858617-67f85cf4f1df",  # city skyline
    },
    # --- Premium / Luxury ---
    "inmobiliaria": {
        "hero":    "1613977257592-4871e5fcd7c4",  # luxury house
        "hero2":   "1560448204-603b3fc33ddc",      # modern interior
        "card1":   "1556228578-8c89e6adf883",      # minimalist room
        "card2":   "1600566752355-35792bedcfea",  # modern kitchen
        "card3":   "1570129477492-45c003edd2be",      # luxury pool (repl: deleted photo)
        "card4":   "1568605114967-8130f3a36994",  # living room
        "card5":   "1489171078254-c3365d6e359f",  # architecture
        "card6":   "1568605114967-8130f3a36994",  # estate exterior
        "section": "1441986300917-64674bd600d8",  # luxury lifestyle
    },
    "hotel": {
        "hero":    "1571896349842-33c89424de2d",  # luxury hotel lobby
        "hero2":   "1520250497591-112f2f40a3f4",  # hotel aerial view
        "card1":   "1571896349842-33c89424de2d",  # hotel room
        "card2":   "1555396273-367ea4eb4db5",      # restaurant hotel
        "card3":   "1534430480872-3498386e7856",  # spa hotel
        "card4":   "1560347876-aeef00ee58a1",      # suite
        "card5":   "1582719508461-905c673771fd",  # gym hotel
        "card6":   "1514362545857-3bc16c4c7d1b",  # hotel bar
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
        "section": "1509631179647-0177331693ae",      # runway editorial (repl: deleted photo)
    },
}

# Curated portrait photos for avatars (permanent Unsplash IDs)
AVATAR_PHOTOS = [
    "1507003211169-0a1dd7228f2d",  # man professional
    "1494790108377-be9c29b29330",  # woman professional
    "1438761681033-6461ffad8d80",  # woman smiling
    "1472099645785-5658abf4ff4e",  # man casual
    "1544005313-94ddf0286df2",     # woman casual
]

# Mapping: industria detectada -> clave en CURATED_PHOTOS
INDUSTRY_TO_CURATED: dict[str, str] = {
    "restaurant": "restaurante", "cafe": "cafe", "hotel": "hotel",
    "fitness": "fitness", "wellness": "wellness", "saas": "saas",
    "fintech": "fintech", "travel": "travel", "fashion": "fashion",
    "realestate": "inmobiliaria",
    "bakery":       "cafe",
    "cocktail_bar": "hotel",
    "martial_arts": "fitness",
    "florist":      "wellness",
    "chocolate":    "sushi",
    "tattoo":       "saas",
    "dental":       "wellness",
    "healthcare":   "wellness",
    "therapy":      "wellness",
    "automotive":   "tech",
    "beauty":       "fashion",
    "education":    "saas",
    "legal":        "fintech",
    "events":       "hotel",
    "architecture": "inmobiliaria",
    "pets":         "wellness",
    "agriculture":  "travel",
    "nonprofit":    "wellness",
    "developer":    "saas",
    "consulting":   "saas",
    "photography":  "fashion",
}


# ---------------------------------------------------------------------------
# URL builders
# ---------------------------------------------------------------------------

def _unsplash(photo_id: str, w: int, h: int) -> str:
    """URL permanente de Unsplash CDN (no requiere API key)."""
    return (
        "https://images.unsplash.com/photo-" + photo_id
        + "?w=" + str(w) + "&h=" + str(h) + "&fit=crop&auto=format&q=80"
    )


def _picsum(seed: str, w: int, h: int) -> str:
    """picsum.photos con seed deterministico (siempre carga, sin CORS)."""
    return "https://picsum.photos/seed/" + seed + "/" + str(w) + "/" + str(h)


def _contextual_picsum(query: str, w: int, h: int) -> str:
    """Seed derivado de primeras 2 palabras significativas del query."""
    stopwords = {
        "and", "or", "the", "a", "an", "of", "in", "for", "with", "on",
        "high", "end", "top", "best", "new", "big", "full", "wide",
        "bright", "professional", "quality", "dark", "modern", "elegant",
    }
    words = re.sub(r"[^a-zA-Z0-9 ]", " ", query).lower().split()
    kws = [w for w in words if len(w) > 2 and w not in stopwords][:2]
    seed = "-".join(kws) if kws else "business"
    return "https://picsum.photos/seed/" + seed + "/" + str(w) + "/" + str(h)


# ---------------------------------------------------------------------------
# Unsplash API  (PATH 1 - requiere UNSPLASH_ACCESS_KEY)
# ---------------------------------------------------------------------------

def _fetch_unsplash_sync(query: str, count: int, orientation: str = "landscape") -> list:
    """Llama la Unsplash API. Retorna lista de URLs (1080px)."""
    key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if not key:
        return []
    try:
        resp = requests.get(
            "https://api.unsplash.com/photos/random",
            params={"query": query, "count": count, "orientation": orientation},
            headers={"Authorization": "Client-ID " + key},
            timeout=8,
        )
        if resp.status_code == 200:
            data = resp.json()
            return [p["urls"]["regular"] for p in data if "urls" in p]
    except Exception as e:
        logger.warning("Unsplash API error: %s", e)
    return []


async def _get_image_urls_via_api(queries: dict):
    """PATH 1: Unsplash API. Retorna dict completo o None."""
    if not os.environ.get("UNSPLASH_ACCESS_KEY"):
        return None

    async def fetch(query: str, orientation: str = "landscape"):
        results = await asyncio.to_thread(_fetch_unsplash_sync, query, 1, orientation)
        return results[0] if results else None

    slots = {
        "hero":       fetch(queries["hero"]),
        "hero_alt":   fetch(queries.get("hero_alt", queries["hero"])),
        "section_bg": fetch(queries.get("section_bg", queries["hero"])),
        "card_1":     fetch(queries.get("card_1", queries["hero"])),
        "card_2":     fetch(queries.get("card_2", queries["hero"])),
        "card_3":     fetch(queries.get("card_3", queries["hero"])),
        "card_4":     fetch(queries.get("card_4", queries["hero"])),
        "card_5":     fetch(queries.get("card_5", queries["hero"])),
        "card_6":     fetch(queries.get("card_6", queries["hero"])),
        "avatar_1":   fetch(queries.get("avatar", "person portrait"), "portrait"),
        "avatar_2":   fetch(queries.get("avatar", "person portrait"), "portrait"),
        "avatar_3":   fetch(queries.get("avatar", "person portrait"), "portrait"),
    }
    results = await asyncio.gather(*slots.values(), return_exceptions=True)
    urls = {}
    for slot_name, result in zip(slots.keys(), results):
        if isinstance(result, str):
            urls[slot_name] = result

    if not urls.get("hero"):
        return None

    for slot in slots:
        if slot not in urls:
            if "card" in slot:
                w, h = 800, 600
            elif "avatar" in slot:
                w, h = 200, 200
            else:
                w, h = 1600, 900
            urls[slot] = _picsum(slot, w, h)

    return urls


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def get_image_urls(brief: str) -> dict:
    """
    Retorna dict de URLs de imagenes para el brief dado.

    Slots: hero, hero_alt, section_bg, card_1..card_6, avatar_1..avatar_3

    Cascada:
        PATH 1 - Unsplash API    (requiere UNSPLASH_ACCESS_KEY)
        PATH 2 - Unsplash curado por industria (IDs permanentes)
        PATH 3 - picsum.photos con seed contextual (fallback universal)
    """
    from services.keyword_translator import translate_brief_to_keywords, get_unsplash_queries

    kw = translate_brief_to_keywords(brief)
    queries = get_unsplash_queries(brief)

    # PATH 1: Unsplash API
    api_result = await _get_image_urls_via_api(queries)
    if api_result:
        logger.info("get_image_urls: PATH 1 (Unsplash API)")
        return api_result

    # PATH 2: IDs curados por industria
    curated_key = INDUSTRY_TO_CURATED.get(kw.industry)
    if not curated_key:
        brief_lower = brief.lower()
        for industry in CURATED_PHOTOS:
            if industry in brief_lower:
                curated_key = industry
                break

    if curated_key and curated_key in CURATED_PHOTOS:
        ids = CURATED_PHOTOS[curated_key]
        logger.info("get_image_urls: PATH 2 curado - industria=%s", curated_key)
        return {
            "hero":       _unsplash(ids["hero"],    1600, 900),
            "hero_alt":   _unsplash(ids["hero2"],   1600, 900),
            "section_bg": _unsplash(ids["section"], 1400, 800),
            "card_1":     _unsplash(ids["card1"],   800, 600),
            "card_2":     _unsplash(ids["card2"],   800, 600),
            "card_3":     _unsplash(ids["card3"],   800, 600),
            "card_4":     _unsplash(ids["card4"],   800, 600),
            "card_5":     _unsplash(ids["card5"],   800, 600),
            "card_6":     _unsplash(ids["card6"],   800, 600),
            "avatar_1":   _unsplash(AVATAR_PHOTOS[0], 200, 200),
            "avatar_2":   _unsplash(AVATAR_PHOTOS[1], 200, 200),
            "avatar_3":   _unsplash(AVATAR_PHOTOS[2], 200, 200),
        }

    # PATH 3: picsum contextual (fallback universal)
    logger.info("get_image_urls: PATH 3 picsum - industria=%s", kw.industry)
    return {
        "hero":       _contextual_picsum(queries["hero"],                        1600, 900),
        "hero_alt":   _contextual_picsum(queries.get("card_1", queries["hero"]), 1600, 900),
        "section_bg": _contextual_picsum(queries.get("section_bg", queries["hero"]), 1400, 800),
        "card_1":     _contextual_picsum(queries.get("card_1", queries["hero"]), 800, 600),
        "card_2":     _contextual_picsum(queries.get("card_2", queries["hero"]), 800, 600),
        "card_3":     _contextual_picsum(queries.get("card_3", queries["hero"]), 800, 600),
        "card_4":     _contextual_picsum(queries.get("card_4", queries["hero"]), 800, 600),
        "card_5":     _contextual_picsum(queries.get("card_5", queries["hero"]), 800, 600),
        "card_6":     _contextual_picsum(queries.get("card_6", queries["hero"]), 800, 600),
        "avatar_1":   _picsum("avatar-1", 200, 200),
        "avatar_2":   _picsum("avatar-2", 200, 200),
        "avatar_3":   _picsum("avatar-3", 200, 200),
    }
