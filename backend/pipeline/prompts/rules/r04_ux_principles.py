"""
r04_ux_principles.py -- Principios UX: above-the-fold, Hick, patron F/Z, color, senales visuales.
Principios del POR QUE, no del como (eso va en technical.py).
"""

UX_PRINCIPLES = (
    "=== PRINCIPIOS UX ===\n\n"
    "ABOVE THE FOLD:\n"
    "  El primer viewport debe comunicar: quien eres, que ofreces, que hacer.\n"
    "  Hero: headline + subtitulo + 1 CTA + imagen/visual, todo visible sin scroll.\n"
    "  Hero height: min 90vh desktop, 70vh mobile.\n\n"
    "LEY DE HICK (menos opciones = menos friccion):\n"
    "  Navegacion: maximo 6-7 items. Formularios: solo campos imprescindibles.\n"
    "  Una accion primaria por seccion. Maximo 3 opciones por cualquier decision.\n\n"
    "PATRON F/Z (como el ojo escanea):\n"
    "  Info clave en la parte superior. Elementos de accion en los trayectos F y Z.\n"
    "  Usar flechas, chevrons o gradientes que apuntan hacia el CTA principal.\n"
    "  Si hay persona en imagen mirando hacia el texto, el ojo del usuario la sigue.\n\n"
    "COLOR CON PROPOSITO:\n"
    "  Color primario: acciones (CTAs, links). Max 20% del area visible.\n"
    "  Color neutro/superficie: fondos y contenedores. 60-70% del area.\n"
    "  Color acento: badges, highlights, alertas. Max 10% del area.\n"
    "  Alternar secciones: claro / oscuro / claro. No mas de 2-3 colores de fondo distintos.\n\n"
    "MOBILE-FIRST (principio, no CSS -- el CSS va en technical.py):\n"
    "  Disenar primero para 375px. En mobile: columna unica, stacks verticales.\n"
    "  Touch targets: minimo 44x44px para cualquier elemento interactivo.\n"
)
