"""
r02_no_overlap.py -- Regla critica: prohibicion de superposicion.
"""

NO_OVERLAP_RULES = (
    "=== REGLA CRITICA: PROHIBICION DE SUPERPOSICION Y COLAPSO ===\n\n"

    "NUNCA SUPERPONGAS elementos entre si:\n"
    "  - Imagen sobre imagen, card sobre card, texto sobre imagen sin overlay.\n"
    "  - position: absolute en galerias que monta imagenes encima de otras.\n"
    "  - transform: translate() tan grande que un elemento pisa a otro.\n"
    "  - Negative margins que sacan elementos de su contenedor.\n"
    "  - z-index sin control. Collages CSS. Usar grid limpio.\n\n"

    "NUNCA USES height:100% SIN PADRE CON ALTURA DEFINIDA:\n"
    "  MAL: .card-img { height: 100%; }  /* colapsa a 0 si el padre no tiene altura */\n"
    "  BIEN opcion A: .card-img { aspect-ratio: 4/3; width: 100%; object-fit: cover; }\n"
    "  BIEN opcion B: usar grid-auto-rows en el grid padre para definir altura de filas.\n"
    "  Esto es el bug mas comun en grids de portfolio/galeria.\n\n"

    "EXCEPCIONES PERMITIDAS (solo estas 3):\n"
    "  1. HERO OVERLAY: texto sobre background-image del hero.\n"
    "     Obligatorio: gradiente rgba(0,0,0,0.55) minimo para legibilidad.\n"
    "  2. OVERLAY CARD: card entera con background-image + gradiente.\n"
    "     Texto en parte inferior, sobre el gradiente, con padding suficiente.\n"
    "  3. FULL-BLEED SECTION: background-image a 100vw + contenido centrado.\n"
    "     Siempre con overlay de contraste suficiente.\n\n"

    "GALERIAS -- IMPLEMENTACION CORRECTA:\n"
    "  .gallery {\n"
    "    display: grid;\n"
    "    grid-template-columns: repeat(3, 1fr);\n"
    "    grid-auto-rows: 280px;  /* CRITICO: define la altura de las filas */\n"
    "    gap: 16px;\n"
    "  }\n"
    "  .gallery-item:first-child { grid-column: span 2; grid-row: span 2; }\n"
    "  .gallery-item img { width: 100%; height: 100%; object-fit: cover; }\n"
    "  /* height:100% funciona aqui porque el padre .gallery-item tiene altura\n"
    "     definida por grid-auto-rows. Sin ese, colapsa. */\n\n"

    "STAGGERED = solo timing de animacion (transition-delay incremental).\n"
    "  NO significa superposicion fisica. Items siguen en su celda de grid.\n"
)
