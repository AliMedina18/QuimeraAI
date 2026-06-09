"""
r06_interactive.py -- Reglas de implementacion de componentes interactivos.
Solo se incluye si el brief menciona carrusel, slider, galeria, tabs o acordeon.
"""

INTERACTIVE_COMPONENTS = (
    "=== COMPONENTES INTERACTIVOS ===\n\n"
    "PRINCIPIO: todo componente interactivo tiene modo automatico + modo manual.\n"
    "  Nunca construyas un carrusel que solo funcione si el usuario hace click.\n\n"
    "CARRUSEL / SLIDER:\n"
    "  CSS (NUNCA width en pixeles para slides):\n"
    "    .carousel-container { overflow: hidden; position: relative; width: 100%; }\n"
    "    .carousel-track { display: flex; transition: transform 0.5s ease; }\n"
    "    .carousel-slide { min-width: 100%; flex-shrink: 0; }\n"
    "  Multi-item (N visibles): .carousel-slide { min-width: calc(100% / N); }\n"
    "  JS: let idx=0; track.style.transform=`translateX(-${idx*100}%)`; idx=(idx+1)%total;\n"
    "  Auto-play: setInterval(nextSlide, 4500). Pausar en mouseenter.\n"
    "  Controles: botones prev/next position:absolute left/right 16px top 50%.\n"
    "  NUNCA translateX en pixeles -- siempre en porcentajes.\n"
    "  Mobile: siempre 1 item. Touch: touchstart/touchend, diff >50px = cambiar slide.\n\n"
    "TABS / ACORDEON: solo por click. Clase .active con estilo diferenciado.\n"
    "  Acordeon: transicion con max-height o opacity+transform.\n\n"
    "HOVER: 100% CSS. Cards: translateY(-4px) + shadow. Botones: scale(1.02).\n\n"
    "REVEAL (IntersectionObserver): automatico al entrar al viewport, no requiere click.\n"
)
