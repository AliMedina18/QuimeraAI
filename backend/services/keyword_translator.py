"""
keyword_translator.py — Mapea términos del brief a keywords en inglés para Unsplash.
=====================================================================================
Sin llamadas a Gemini ni APIs externas. Solo diccionario + heurísticas.

Retorna queries optimizadas por SLOT de imagen:
  - hero:       landscape atmosférico que define el mood del sitio
  - cards[0-5]: imágenes específicas de productos/servicios
  - section_bg: fondo inmersivo para sección de impacto
  - avatar:     retrato del tipo de persona relevante (profesional / cliente)
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# MODELO DE SALIDA
# ---------------------------------------------------------------------------

@dataclass
class ImageKeywords:
    industry: str                       # Industria detectada (ej: "healthcare")
    confidence: float                   # 0.0–1.0 qué tan seguro está el match
    hero: str                           # Query para imagen hero
    cards: list[str]                    # 6 queries para cards de servicios/productos
    section_bg: str                     # Query para sección inmersiva
    avatar: str                         # Query para fotos de personas / avatares
    portrait_orientation: str = "portrait"  # "portrait" o "squarish"


# ---------------------------------------------------------------------------
# BASE DE CONOCIMIENTO: 25+ INDUSTRIAS
# Cada entrada: keywords trigger (ES + EN) → queries Unsplash en inglés
# ---------------------------------------------------------------------------

_INDUSTRIES: list[dict] = [

    # ── SALUD / HEALTHCARE ───────────────────────────────────────────────────
    {
        "id": "healthcare",
        "triggers": [
            "salud", "ips", "clínica", "hospital", "médico",
            "medicina", "health", "doctor", "medical", "healthcare",
            "paciente", "patient", "enfermera", "nurse", "cirugía", "surgery",
            "farmacia", "pharmacy",
            "pediatría", "ginecología", "dermatología", "psicología",
            "bienestar médico", "atención médica", "consulta médica",
            "integral de salud", "centro médico", "eps", "consultorio",
        ],
        "hero":       "modern hospital interior bright professional healthcare",
        "cards": [
            "doctor patient consultation clinic",
            "medical team hospital professional",
            "healthcare professional white coat stethoscope",
            "modern clinic reception bright",
            "medical examination room professional",
            "wellness health center interior",
        ],
        "section_bg": "hospital corridor light modern architecture",
        "avatar":     "doctor professional portrait white coat",
    },

    # ── ODONTOLOGÍA ──────────────────────────────────────────────────────────
    {
        "id": "dental",
        "triggers": [
            "dental", "dentista", "odontología", "odontologia", "dientes",
            "sonrisa", "ortodoncia", "implante dental", "blanqueamiento",
            "clínica dental", "clinica dental", "consultorio dental",
        ],
        "hero":       "modern dental clinic bright professional",
        "cards": [
            "dental examination professional",
            "teeth whitening dental care",
            "orthodontics braces treatment",
            "dental implant procedure",
            "dentist patient consultation",
            "clean bright dental office",
        ],
        "section_bg": "dental clinic modern interior white",
        "avatar":     "dentist professional portrait smiling",
    },

    # ── PSICOLOGÍA / TERAPIA ─────────────────────────────────────────────────
    {
        "id": "therapy",
        "triggers": [
            "psicología", "psicologia", "terapia", "therapy", "psychology",
            "terapeuta", "therapist", "salud mental", "mental health",
            "counseling", "consejería", "bienestar emocional",
        ],
        "hero":       "calm therapy office couch plants serene",
        "cards": [
            "therapy session consultation room",
            "mental health wellness calm",
            "psychologist office professional",
            "meditation mindfulness peaceful",
            "person journaling therapy",
            "support group circle",
        ],
        "section_bg": "serene nature peaceful light bokeh",
        "avatar":     "therapist psychologist professional portrait",
    },

    # ── LEGAL / ABOGADOS ─────────────────────────────────────────────────────
    {
        "id": "legal",
        "triggers": [
            "abogado", "abogados", "jurídico", "juridico", "legal", "ley",
            "derecho", "law", "lawyer", "attorney", "firma legal", "law firm",
            "notaría", "notaria", "juzgado", "litigio", "bufete",
        ],
        "hero":       "law firm office dark wood professional books",
        "cards": [
            "lawyer attorney professional office",
            "legal books library court",
            "business law contract signing",
            "judge gavel courtroom",
            "legal consultation meeting",
            "corporate law office professional",
        ],
        "section_bg": "courthouse architecture columns classic",
        "avatar":     "lawyer attorney professional portrait suit",
    },

    # ── EDUCACIÓN ────────────────────────────────────────────────────────────
    {
        "id": "education",
        "triggers": [
            "educación", "educacion", "escuela", "colegio", "universidad",
            "academia", "school", "college", "university", "education",
            "curso", "course", "aprendizaje", "learning", "estudiante",
            "student", "enseñanza", "profesor", "teacher", "capacitación",
        ],
        "hero":       "modern university campus students bright",
        "cards": [
            "students learning classroom bright",
            "university library books knowledge",
            "teacher professor lecture hall",
            "online learning laptop student",
            "graduation ceremony students",
            "campus outdoor students studying",
        ],
        "section_bg": "university campus architecture aerial",
        "avatar":     "student young professional portrait smiling",
    },

    # ── CONSTRUCCIÓN / ARQUITECTURA ──────────────────────────────────────────
    {
        "id": "architecture",
        "triggers": [
            "construcción", "construccion", "arquitectura", "architecture",
            "constructora", "obra", "edificio", "building", "contractor",
            "ingeniería civil", "infrastructure", "estructura",
        ],
        "hero":       "modern architecture building construction aerial",
        "cards": [
            "construction site workers professional",
            "modern building architecture exterior",
            "architectural blueprint design",
            "construction crane infrastructure",
            "interior design modern home",
            "engineering project professional",
        ],
        "section_bg": "modern city skyline architecture sunset",
        "avatar":     "architect engineer professional portrait hard hat",
    },

    # ── INMOBILIARIA ─────────────────────────────────────────────────────────
    {
        "id": "realestate",
        "triggers": [
            "inmobiliaria", "propiedad", "real estate", "property", "apartamento",
            "apartment", "casa", "house", "vivienda", "housing", "arriendo",
            "rental", "compra venta", "bienes raíces", "bienes raices",
        ],
        "hero":       "luxury modern house exterior architecture",
        "cards": [
            "modern apartment interior living room",
            "luxury house exterior garden",
            "real estate property kitchen modern",
            "apartment bedroom minimalist",
            "house pool luxury exterior",
            "real estate agent keys",
        ],
        "section_bg": "aerial neighborhood houses architecture",
        "avatar":     "real estate agent professional portrait smiling",
    },

    # ── RESTAURANT / COMIDA ──────────────────────────────────────────────────
    {
        "id": "restaurant",
        "triggers": [
            "restaurante", "restaurant", "comida", "food", "cocina", "kitchen",
            "chef", "menu", "gastronomía", "gastronomy", "platos", "dishes",
            "sushi", "pizza", "pasta", "burger", "hamburguesa", "mariscos",
            "seafood", "grill", "parrilla", "bar", "bistro",
        ],
        "hero":       "elegant restaurant interior ambient lighting",
        "cards": [
            "gourmet food plating professional",
            "restaurant kitchen chef cooking",
            "fine dining table setting elegant",
            "food dish close up appetizing",
            "restaurant ambiance candles evening",
            "fresh ingredients vegetables colorful",
        ],
        "section_bg": "restaurant bar atmospheric evening bokeh",
        "avatar":     "chef professional portrait kitchen uniform",
    },

    # ── CAFÉ / COFFEE ────────────────────────────────────────────────────────
    {
        "id": "cafe",
        "triggers": [
            "café", "cafe", "cafetería", "cafeteria", "coffee", "barista", "espresso", "latte",
            "panadería", "bakery", "pastelería", "pastry", "brunch",
        ],
        "hero":       "cozy coffee shop interior warm light",
        "cards": [
            "latte art coffee cup close up",
            "barista preparing espresso professional",
            "coffee shop interior cozy people",
            "pastry cake dessert close up",
            "coffee beans roasted close up",
            "cafe brunch food presentation",
        ],
        "section_bg": "coffee shop window rain bokeh warm",
        "avatar":     "barista professional portrait apron coffee",
    },

    # ── HOTEL / HOSPITALIDAD ─────────────────────────────────────────────────
    {
        "id": "hotel",
        "triggers": [
            "hotel", "resort", "hostel", "hospedaje", "alojamiento",
            "accommodation", "boutique hotel", "posada", "bed breakfast",
        ],
        "hero":       "luxury hotel lobby elegant interior",
        "cards": [
            "hotel room luxury bed elegant",
            "hotel pool sunset tropical",
            "hotel restaurant fine dining",
            "spa hotel relaxation massage",
            "hotel suite view city",
            "hotel reception concierge",
        ],
        "section_bg": "luxury hotel infinity pool aerial",
        "avatar":     "hotel concierge staff professional portrait",
    },

    # ── WELLNESS / SPA ───────────────────────────────────────────────────────
    {
        "id": "wellness",
        "triggers": [
            "spa", "wellness", "bienestar", "relajación", "relaxation",
            "masaje", "massage", "meditación", "meditation", "yoga",
            "aromaterapia", "aromatherapy", "holístico", "holistic",
        ],
        "hero":       "spa wellness center serene interior candles",
        "cards": [
            "spa massage relaxation treatment",
            "yoga meditation serene calm woman",
            "essential oils aromatherapy wellness",
            "spa pool jacuzzi relaxation",
            "wellness center interior plants calm",
            "healthy lifestyle mindfulness nature",
        ],
        "section_bg": "nature peaceful zen garden water",
        "avatar":     "wellness therapist professional portrait serene",
    },

    # ── FITNESS / GYM ────────────────────────────────────────────────────────
    {
        "id": "fitness",
        "triggers": [
            "fitness", "gym", "gimnasio", "entrenamiento", "workout", "sport",
            "deporte", "ejercicio", "exercise", "crossfit", "personal trainer",
            "running", "correr", "nutrición deportiva",
        ],
        "hero":       "modern gym interior equipment professional",
        "cards": [
            "gym workout weights training",
            "personal trainer coaching athlete",
            "running outdoor sport motivation",
            "crossfit training group workout",
            "yoga fitness class group",
            "sports nutrition protein shake",
        ],
        "section_bg": "athlete running outdoor motivation dramatic",
        "avatar":     "personal trainer fitness professional portrait",
    },

    # ── MODA / FASHION ───────────────────────────────────────────────────────
    {
        "id": "fashion",
        "triggers": [
            "moda", "fashion", "ropa", "clothing", "boutique",
            "diseño de moda", "fashion design", "colección", "collection",
            "vestido", "dress", "zapatos", "shoes", "accesorios", "accessories",
        ],
        "hero":       "fashion editorial model studio professional",
        "cards": [
            "fashion clothing editorial lookbook",
            "model wearing outfit studio",
            "fashion accessories handbag shoes",
            "clothing store boutique interior",
            "fashion designer atelier",
            "street style fashion photography",
        ],
        "section_bg": "fashion runway editorial dramatic lighting",
        "avatar":     "fashion model professional portrait studio",
    },

    # ── TECH / SaaS ──────────────────────────────────────────────────────────
    {
        "id": "saas",
        "triggers": [
            "saas", "software", "app", "aplicación", "plataforma", "platform",
            "startup", "tech", "technology", "tecnología", "digital",
            "datos", "data", "analytics", "dashboard", "api", "cloud",
            "inteligencia artificial", "artificial intelligence", "ai", "ia",
        ],
        "hero":       "modern tech office open space professionals laptops",
        "cards": [
            "dashboard analytics data visualization",
            "software developer coding laptop",
            "team collaboration meeting modern office",
            "data visualization charts professional",
            "mobile app interface design",
            "cloud technology server infrastructure",
        ],
        "section_bg": "abstract data technology blue dark",
        "avatar":     "software developer tech professional portrait",
    },

    # ── FINTECH / FINANZAS ───────────────────────────────────────────────────
    {
        "id": "fintech",
        "triggers": [
            "fintech", "finanzas", "finance", "banco", "bank", "pagos",
            "payment", "inversión", "investment", "crypto", "blockchain",
            "seguros", "insurance", "contabilidad", "accounting",
            "crédito", "credit", "préstamo", "loan",
        ],
        "hero":       "financial district city skyline corporate",
        "cards": [
            "financial analyst charts data professional",
            "mobile banking payment app",
            "investment stock market charts",
            "business meeting finance professional",
            "credit card payment digital",
            "financial planning charts growth",
        ],
        "section_bg": "city financial district night lights",
        "avatar":     "financial advisor professional portrait suit",
    },

    # ── FOTOGRAFÍA / CREATIVE ────────────────────────────────────────────────
    {
        "id": "photography",
        "triggers": [
            "fotografía", "fotografia", "photography", "fotógrafo", "fotografo",
            "photographer", "estudio fotográfico", "creative", "creativo",
            "diseño gráfico", "graphic design", "agencia creativa",
        ],
        "hero":       "photographer studio professional camera setup",
        "cards": [
            "photography studio portrait lighting",
            "camera lens professional equipment",
            "photo editing retouching computer",
            "outdoor photography nature landscape",
            "wedding photography couple",
            "product photography studio setup",
        ],
        "section_bg": "photography studio dramatic lighting dark",
        "avatar":     "photographer professional portrait camera",
    },

    # ── VIAJES / TURISMO ─────────────────────────────────────────────────────
    {
        "id": "travel",
        "triggers": [
            "viajes", "viaje", "travel", "turismo", "tourism", "tour",
            "agencia de viajes", "travel agency", "destino", "destination",
            "aventura", "adventure", "vacaciones", "vacation",
        ],
        "hero":       "travel destination landscape beautiful scenic",
        "cards": [
            "tropical beach paradise",
            "mountain landscape adventure hiking",
            "european city travel tourism",
            "airplane window travel view",
            "exotic destination culture",
            "travel adventure couple landscape",
        ],
        "section_bg": "aerial landscape travel scenic beauty",
        "avatar":     "travel guide professional portrait adventure",
    },

    # ── BELLEZA / ESTÉTICA ───────────────────────────────────────────────────
    {
        "id": "beauty",
        "triggers": [
            "belleza", "beauty", "estética", "salón",
            "peluquería", "barbería", "maquillaje",
            "makeup", "nail", "uñas", "hair", "cabello", "spa facial",
        ],
        "hero":       "beauty salon interior elegant professional",
        "cards": [
            "hair salon styling professional",
            "makeup artist professional studio",
            "nail art manicure close up",
            "beauty treatment facial skincare",
            "barbershop interior professional",
            "cosmetics beauty products elegant",
        ],
        "section_bg": "beauty salon mirror lights elegant",
        "avatar":     "beauty stylist professional portrait smiling",
    },

    # ── MASCOTAS / VETERINARIA ───────────────────────────────────────────────
    {
        "id": "pets",
        "triggers": [
            "mascotas", "mascota", "pet", "pets", "veterinario", "veterinaria",
            "veterinary", "perro", "dog", "gato", "cat", "animal", "tienda mascotas",
            "canino", "canina", "felino", "felina", "peluquería canina", "peluqueria canina",
            "guardería mascotas", "adiestramiento", "clinica veterinaria",
        ],
        "hero":       "veterinary clinic bright professional pets",
        "cards": [
            "veterinarian dog examination professional",
            "cute puppy dog portrait",
            "pet store animals happy",
            "vet clinic cat examination",
            "pet grooming professional",
            "happy dog owner park",
        ],
        "section_bg": "nature park pets happy outdoor",
        "avatar":     "veterinarian professional portrait smiling",
    },

    # ── CONSULTORA / SERVICIOS PROFESIONALES ────────────────────────────────
    {
        "id": "consulting",
        "triggers": [
            "consultoría", "consultoria", "consulting", "asesoría", "asesoria",
            "advisory", "management", "gestión", "gestion", "recursos humanos",
            "human resources", "marketing", "estrategia", "strategy",
            "agencia", "agency", "servicios profesionales",
        ],
        "hero":       "modern professional office meeting business",
        "cards": [
            "business meeting professional team",
            "strategy planning whiteboard office",
            "consulting analysis data charts",
            "professional handshake partnership",
            "business growth success charts",
            "corporate office professional team",
        ],
        "section_bg": "corporate office building modern exterior",
        "avatar":     "business consultant professional portrait suit",
    },

    # ── EVENTOS / BODAS ──────────────────────────────────────────────────────
    {
        "id": "events",
        "triggers": [
            "eventos", "events", "boda", "wedding", "matrimonio", "fiesta",
            "party", "celebración", "celebration", "decoración de eventos",
            "planner", "organizador de eventos",
        ],
        "hero":       "elegant wedding venue decoration flowers",
        "cards": [
            "wedding ceremony decoration flowers",
            "event venue decoration elegant",
            "wedding couple romantic portrait",
            "party celebration lights decoration",
            "catering food elegant event",
            "event planning professional meeting",
        ],
        "section_bg": "wedding reception venue night lights bokeh",
        "avatar":     "event planner professional portrait elegant",
    },

    # ── AGRICULTURA / ALIMENTOS ──────────────────────────────────────────────
    {
        "id": "agriculture",
        "triggers": [
            "agricultura", "agriculture", "granja", "farm", "campo", "organic",
            "orgánico", "orgánico", "cultivo", "crop", "alimentos naturales",
            "natural food", "huerta", "garden", "productores",
        ],
        "hero":       "organic farm landscape countryside aerial",
        "cards": [
            "fresh vegetables organic farm harvest",
            "farmer agricultural field crops",
            "organic produce market colorful",
            "farm to table fresh food",
            "agricultural greenhouse plants",
            "natural food ingredients healthy",
        ],
        "section_bg": "countryside farm landscape sunrise",
        "avatar":     "farmer agricultural professional portrait outdoor",
    },

    # ── ONG / FUNDACIÓN ──────────────────────────────────────────────────────
    {
        "id": "nonprofit",
        "triggers": [
            "fundación", "fundacion", "foundation", "ong", "ngo",
            "organización sin ánimo de lucro", "nonprofit", "voluntariado",
            "volunteer", "solidaridad", "community", "comunidad", "social",
        ],
        "hero":       "community volunteers helping people outdoor",
        "cards": [
            "volunteers community service outdoor",
            "charity donation helping hands",
            "community meeting diverse people",
            "social impact project outdoor",
            "nonprofit teamwork collaboration",
            "children education developing countries",
        ],
        "section_bg": "diverse people community outdoor sunlight",
        "avatar":     "community leader professional portrait warm",
    },

    # ── AUTOMOTRIZ ───────────────────────────────────────────────────────────
    {
        "id": "automotive",
        "triggers": [
            "auto", "autos", "carro", "carros", "coche", "coches", "vehículo", "vehiculo",
            "automóvil", "automovil", "car", "cars", "vehicle", "automotive",
            "taller mecánico", "taller mecanico", "mecánico", "mecanico",
            "concesionario", "dealership", "garage", "gasolinera",
            "bmw", "mercedes", "audi", "toyota", "ford", "honda", "renault",
            "repuestos", "autopartes", "llanta", "llantas", "neumático",
        ],
        "hero":       "luxury car showroom modern architecture dramatic",
        "cards": [
            "car dealership interior modern",
            "luxury vehicle close up detail",
            "automotive workshop mechanic professional",
            "car engine detail technical",
            "vehicle test drive road scenic",
            "auto parts store professional",
        ],
        "section_bg": "automotive workshop dramatic lighting industrial",
        "avatar":     "automotive mechanic professional portrait uniform",
    },

    # ── INDUSTRIAL ───────────────────────────────────────────────────────────
    {
        "id": "industrial",
        "triggers": [
            "industria", "industry", "manufactura", "manufacturing", "fábrica",
            "factory", "planta", "plant", "maquinaria", "machinery",
            "logística", "logistics", "supply chain", "cadena de suministro",
        ],
        "hero":       "industrial factory modern manufacturing interior",
        "cards": [
            "industrial machinery manufacturing professional",
            "factory worker safety equipment",
            "logistics warehouse supply chain",
            "industrial equipment technology",
            "quality control inspection professional",
            "engineering industrial facility",
        ],
        "section_bg": "industrial architecture steel modern dramatic",
        "avatar":     "industrial engineer professional portrait safety helmet",
    },

    # ── PANADERÍA / BAKERY ──────────────────────────────────────────────────
    {
        "id": "bakery",
        "triggers": [
            "panadería", "panaderia", "pastelería", "pasteleria",
            "pan artesanal", "masa madre", "sourdough", "boulangerie",
            "repostería", "reposteria", "galletas", "croissant",
            "tortas personalizadas", "cake design", "cupcakes",
            "baker", "bakery", "baking",
        ],
        "hero":       "artisan bakery interior warm bread display",
        "cards":      [
            "sourdough bread loaves golden crust",
            "pastry selection display case",
            "baker kneading artisan dough",
            "cinnamon rolls fresh baked",
            "croissant golden flaky layers",
            "pastry chef decorating cake",
        ],
        "section_bg": "bakery warm light bread shelves",
        "avatar":     "baker chef portrait smiling apron",
    },

    # ── CHOCOLATERÍA / CHOCOLATE SHOP ───────────────────────────────────────
    {
        "id": "chocolate",
        "triggers": [
            "chocolate", "chocolates", "chocolatería", "chocolateria",
            "bombones", "trufas", "cacao", "cocoa", "bonbons",
            "chocolate artesanal", "artisan chocolate", "pralines",
            "ganache", "chocolate gourmet", "chocolatier",
        ],
        "hero":       "artisan chocolate shop premium display dark",
        "cards":      [
            "handcrafted chocolate bonbons assortment",
            "chocolate making process cacao",
            "premium chocolate selection box",
            "dark chocolate bar texture closeup",
            "chocolate tasting bar elegant",
            "chocolatier packaging luxury gift",
        ],
        "section_bg": "cacao dark chocolate background rich",
        "avatar":     "chocolatier craftsperson portrait professional",
    },

    # ── ARTES MARCIALES / MARTIAL ARTS ──────────────────────────────────────
    {
        "id": "martial_arts",
        "triggers": [
            "taekwondo", "karate", "judo", "boxeo", "boxing",
            "artes marciales", "martial arts", "muay thai",
            "kickboxing", "bjj", "jiu jitsu", "lucha",
            "academia de artes", "dojo", "gym boxing",
        ],
        "hero":       "martial arts dojo training professional",
        "cards":      [
            "taekwondo kick high belt",
            "karate kata discipline dojo",
            "martial arts students training",
            "boxing training gloves punching bag",
            "instructor belt black demonstration",
            "martial arts competition action",
        ],
        "section_bg": "martial arts gym dojo background",
        "avatar":     "martial arts instructor belt portrait",
    },

    # ── COCTELERÍA / COCKTAIL BAR ────────────────────────────────────────────
    {
        "id": "cocktail_bar",
        "triggers": [
            "cócteles", "cocteles", "coctelería", "cocteleria",
            "bebidas alcohólicas", "bebidas alcoholicas",
            "mixología", "mixologia", "bartender", "bar de tragos",
            "tragos", "whisky bar", "speakeasy", "lounge bar",
            "cocktails", "cocktail bar", "mixology",
        ],
        "hero":       "cocktail bar elegant backlit bottles atmosphere",
        "cards":      [
            "craft cocktail preparation bartender",
            "negroni stirred elegant glass",
            "whisky premium glass bar",
            "cocktail menu selection drinks",
            "bar counter mixology professional",
            "champagne celebration glasses luxury",
        ],
        "section_bg": "bar atmosphere dark elegant bokeh",
        "avatar":     "bartender professional portrait bar",
    },

    # ── FLORISTERÍA / FLOWER SHOP ────────────────────────────────────────────
    {
        "id": "florist",
        "triggers": [
            "floristería", "floristeria", "florería", "floreria",
            "arreglos florales", "flores", "bouquet", "ramo",
            "florist", "flower shop", "wedding flowers",
            "plantas y flores", "jardinería floral", "jardín floral",
        ],
        "hero":       "flower shop colorful bouquet arrangement bright",
        "cards":      [
            "colorful flower arrangement studio",
            "florist arranging bouquet hands",
            "wedding floral centerpiece elegant",
            "roses bouquet romantic red",
            "tropical exotic flower arrangement",
            "dried flower wreath botanical",
        ],
        "section_bg": "flower field bloom soft light",
        "avatar":     "florist professional portrait flowers",
    },

    # ── TATOO / ESTUDIO DE TATUAJES ──────────────────────────────────────────
    {
        "id": "tattoo",
        "triggers": [
            "tatuajes", "tatuaje", "tattoo", "tatoo", "tattooist",
            "piercing", "estudio de tatuajes", "tattoo studio",
            "tatuador", "tattoo artist", "body art",
            "tatuaje realismo", "blackwork", "fine line tattoo",
        ],
        "hero":       "tattoo studio professional clean modern interior",
        "cards":      [
            "tattoo artist working detail precision",
            "fine line tattoo arm healed",
            "tattoo flash sheet wall studio",
            "tattoo studio interior modern black",
            "sleeve tattoo detail intricate",
            "piercing jewelry professional display",
        ],
        "section_bg": "tattoo studio dark moody atmosphere",
        "avatar":     "tattoo artist portrait professional studio",
    },


]


# ---------------------------------------------------------------------------
# DICCIONARIO ES→EN VISUAL: para extraer keywords de imagen del brief directamente.
# Cubre nichos específicos que no tienen industria propia en _INDUSTRIES.
# ---------------------------------------------------------------------------

_ES_EN_VISUAL: dict[str, str] = {
    # Comida y bebida específica
    "chocolate": "chocolate", "chocolates": "chocolate", "cacao": "cacao",
    "bombones": "chocolate bonbons", "trufas": "chocolate truffles",
    "barista": "barista", "coctel": "cocktail", "cocteles": "cocktails",
    "cerveza": "beer", "vino": "wine", "licor": "liquor",
    "whisky": "whisky", "ron": "rum", "tequila": "tequila",
    "panaderia": "bakery", "pan": "bread artisan", "masa madre": "sourdough bread",
    "pasteleria": "pastry shop", "pasteles": "cake pastry", "tortas": "cake",
    "galletas": "cookies", "helado": "ice cream", "helados": "ice cream shop",
    "pizza": "pizza", "hamburguesas": "burger", "tacos": "tacos",
    # Arte y creatividad
    "tatuajes": "tattoo studio", "tatuaje": "tattoo art", "piercing": "piercing studio",
    "fotografia": "photography studio", "fotografo": "photographer",
    "arte": "art studio", "pintura": "painting art", "galeria": "art gallery",
    "musica": "music", "banda": "music band", "guitarra": "guitar",
    # Deportes y artes marciales
    "taekwondo": "taekwondo martial arts", "karate": "karate dojo",
    "judo": "judo martial arts", "boxeo": "boxing gym",
    "artes marciales": "martial arts", "lucha": "wrestling",
    "natacion": "swimming pool", "ciclismo": "cycling", "surf": "surfing",
    # Flores y eventos específicos
    "floreria": "flower shop", "floristeria": "florist flowers",
    "flores": "flowers bouquet", "arreglos florales": "floral arrangements",
    "bodas": "wedding", "boda": "wedding ceremony", "quinceañera": "quinceañera party",
    "cumpleanos": "birthday party", "concierto": "concert",
    # Animales específicos
    "perros": "dogs", "gatos": "cats", "canino": "dog grooming",
    "felino": "cat", "caballos": "horses", "aves": "birds parrots",
    "acuario": "aquarium fish", "reptiles": "reptiles",
    # Retail y productos específicos
    "joyeria": "jewelry store", "joyas": "jewelry", "relojes": "watches luxury",
    "juguetes": "toys children", "bebes": "baby products",
    "plantas": "plants nursery", "jardin": "garden",
    "muebles": "furniture store", "decoracion": "home decor interior",
    # Construcción y arquitectura
    "construccion": "construction", "arquitectura": "architecture modern",
    "carpinteria": "woodworking carpentry", "cerrajeria": "locksmith",
    "electricista": "electrician electrical",
    # Educación específica
    "idiomas": "language school", "ingles": "english learning",
    "musica escuela": "music school", "clases piano": "piano lessons",
    # Transporte
    "motos": "motorcycles", "bicicletas": "bicycles cycling",
    "camiones": "trucks", "mudanzas": "moving truck",
}

_BRIEF_STOPWORDS = {
    # Español
    "quiero", "necesito", "hacer", "crear", "diseno", "sitio", "pagina",
    "web", "empresa", "negocio", "tienda", "somos", "soy", "tengo",
    "vendo", "vender", "para", "que", "con", "sin", "pero", "como",
    "nuestro", "nuestra", "nuestros", "nuestras", "este", "esta",
    "especializado", "especializada", "premium", "profesional", "moderno",
    "elegante", "unico", "mejor", "nuevo", "gran", "pequeño",
    # English
    "want", "need", "make", "create", "design", "website", "page",
    "company", "business", "shop", "store", "our", "their", "this",
    "that", "professional", "modern", "premium", "specialized",
}


def _extract_visual_from_brief(brief: str) -> ImageKeywords:
    """
    Extrae keywords de imagen DIRECTAMENTE del brief.
    Funciona para cualquier nicho: chocolate, tatuajes, taekwondo, flores, etc.
    Traduce español→inglés para mejores resultados en servicios de imágenes.
    """
    normalized = _normalize(brief)

    # Buscar frases y palabras con word-boundary para evitar falsos positivos
    # ("arte" no debe capturar "artesanales", "pan" no captura "pantalla", etc.)
    translated: list[str] = []
    words_list = normalized.split()
    words_set = set(words_list)

    for es_phrase, en_phrase in _ES_EN_VISUAL.items():
        norm_phrase = _normalize(es_phrase)
        # Coincidencia exacta de palabra(s) — no substring parcial
        phrase_words = norm_phrase.split()
        if len(phrase_words) == 1:
            if norm_phrase in words_set and en_phrase not in translated:
                translated.append(en_phrase)
        else:
            # Frase compuesta: buscar como subcadena solo si está rodeada de espacios/inicio/fin
            import re as _re
            if _re.search(r'(?<![a-z])' + _re.escape(norm_phrase) + r'(?![a-z])', normalized):
                if en_phrase not in translated:
                    translated.append(en_phrase)

    # Palabras largas del brief que no se tradujeron pero son descriptivas
    for word in words_list:
        if len(word) > 4 and word not in _BRIEF_STOPWORDS and word not in words_set - {word}:
            en = _ES_EN_VISUAL.get(word)
            if en and en not in translated:
                translated.append(en)
            elif not en and word.isalpha() and word not in translated:
                translated.append(word)

    if not translated:
        return _FALLBACK

    primary = translated[0]
    top3 = translated[:3]
    base_q = " ".join(top3)

    cards = []
    for i in range(6):
        term = translated[i % len(translated)]
        suffix = ["professional", "detail", "closeup", "interior", "product", "atmosphere"][i]
        cards.append(f"{term} {suffix}")

    return ImageKeywords(
        industry="custom",
        confidence=0.4,
        hero=f"{base_q} bright professional high quality",
        cards=cards,
        section_bg=f"{primary} background atmosphere",
        avatar="professional person portrait smiling",
    )


# ---------------------------------------------------------------------------
# FALLBACK GENÉRICO (cuando no se detecta industria)
# ---------------------------------------------------------------------------

_FALLBACK = ImageKeywords(
    industry="generic_business",
    confidence=0.0,
    hero="modern professional office architecture bright",
    cards=[
        "professional team meeting office",
        "business growth success concept",
        "modern workspace laptop professional",
        "professional handshake partnership",
        "office interior modern design",
        "business presentation charts",
    ],
    section_bg="modern building architecture abstract light",
    avatar="professional business person portrait smiling",
)


# ---------------------------------------------------------------------------
# MOTOR DE DETECCIÓN
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Minúsculas, elimina tildes y puntuación extra."""
    text = text.lower()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r"[^\w\s]", " ", text)
    return text


def translate_brief_to_keywords(brief: str) -> ImageKeywords:
    """
    Analiza el brief y retorna ImageKeywords con queries Unsplash en inglés.

    Args:
        brief: Texto del brief en cualquier idioma.

    Returns:
        ImageKeywords con hero, cards (6), section_bg, avatar queries.
    """
    normalized = _normalize(brief)
    words = set(normalized.split())

    best_industry = None
    best_score = 0

    for industry in _INDUSTRIES:
        score = 0
        for trigger in industry["triggers"]:
            trigger_norm = _normalize(trigger)
            if trigger_norm in words:
                score += 2
            elif trigger_norm in normalized:
                score += 1
        if score > best_score:
            best_score = score
            best_industry = industry

    if best_industry is None or best_score == 0:
        # No industry matched → extract keywords directly from brief text.
        # Handles any niche: chocolate shop, tattoo studio, taekwondo academy, etc.
        return _extract_visual_from_brief(brief)

    confidence = min(1.0, best_score / 6.0)

    # Very weak match (score=1, single trigger hit): brief extraction is more specific.
    # Does NOT override score ≥ 2 (hotel, cafe, etc. with real industry matches).
    if best_score <= 1:
        extracted = _extract_visual_from_brief(brief)
        if extracted.industry == "custom":
            return extracted

    return ImageKeywords(
        industry=best_industry["id"],
        confidence=confidence,
        hero=best_industry["hero"],
        cards=best_industry["cards"],
        section_bg=best_industry["section_bg"],
        avatar=best_industry["avatar"],
    )


def get_unsplash_queries(brief: str) -> dict[str, str]:
    """
    Interfaz simplificada: recibe el brief, retorna dict listo para Unsplash.

    Returns:
        {"hero": "...", "card_1": "...", ..., "section_bg": "...", "avatar": "..."}
    """
    kw = translate_brief_to_keywords(brief)
    result = {"hero": kw.hero, "section_bg": kw.section_bg, "avatar": kw.avatar}
    for i, card in enumerate(kw.cards, 1):
        result[f"card_{i}"] = card
    return result
