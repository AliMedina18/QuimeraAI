"""
r02_no_overlap.py -- Regla critica: prohibicion de superposicion.
Explica que NUNCA debe ocurrir y las 3 unicas excepciones.
"""

NO_OVERLAP_RULES = (
    "=== REGLA CRITICA: PROHIBICION DE SUPERPOSICION DE CONTENIDO ===\n\n"
    "NUNCA SUPERPONGAS elementos entre si:\n"
    "  - Imagen sobre imagen, card sobre card, texto sobre imagen sin overlay.\n"
    "  - position: absolute en galerias que monta imagenes unas encima de otras.\n"
    "  - transform: translate() tan grande que un elemento pisa a otro.\n"
    "  - Negative margins que sacan elementos de su contenedor.\n"
    "  - z-index sin control. Collages CSS. Usar grid limpio en su lugar.\n\n"
    "EXCEPCIONES PERMITIDAS (solo estas 3):\n"
    "  1. HERO OVERLAY: texto sobre background-image del hero.\n"
    "     Obligatorio: gradiente rgba(0,0,0,0.55) minimo para legibilidad.\n"
    "  2. OVERLAY CARD: card entera con background-image + gradiente.\n"
    "     Texto en parte inferior, sobre el gradiente, con padding suficiente.\n"
    "  3. FULL-BLEED SECTION: background-image a 100vw + contenido centrado.\n"
    "     Siempre con overlay de contraste suficiente.\n\n"
    "GALERIAS -- IMPLEMENTACION CORRECTA:\n"
    "  .gallery { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }\n"
    "  .gallery-item:first-child { grid-column: span 2; grid-row: span 2; }\n"
    "  Cada item es independiente. Ninguno sale de su celda.\n\n"
    "STAGGERED = solo timing de animacion (transition-delay incremental).\n"
    "  NO significa superposicion fisica. Los items siguen en su celda de grid.\n"
)
