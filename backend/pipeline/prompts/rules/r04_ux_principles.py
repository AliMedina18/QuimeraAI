"""
r04_ux_principles.py -- Principios UX: Nielsen, Contentsquare, above-fold, Hick, F/Z, mobile.
"""

UX_PRINCIPLES = (
    "=== PRINCIPIOS UX (Nielsen + Contentsquare) ===\n\n"

    "ABOVE THE FOLD:\n"
    "  El primer viewport comunica: quien eres, que ofreces, que hacer ahora.\n"
    "  Hero: headline + subtitulo + 1 CTA + imagen/visual. Todo visible sin scroll.\n"
    "  Hero height: min 90vh desktop, 70vh mobile.\n\n"

    "LEY DE HICK (menos opciones = menos friccion):\n"
    "  Navegacion: maximo 6-7 items. Formularios: solo campos imprescindibles.\n"
    "  Una accion primaria por seccion. Maximo 3 opciones por cualquier decision.\n\n"

    "PATRON F/Z (como el ojo escanea):\n"
    "  Info clave en la parte superior. CTAs en los trayectos F y Z.\n"
    "  Usar flechas, chevrons o gradientes que apunten hacia el CTA.\n"
    "  Si hay persona en imagen mirando hacia texto, el ojo del usuario la sigue.\n\n"

    "COLOR CON PROPOSITO:\n"
    "  Color primario: acciones (CTAs, links activos). Max 20% del area visible.\n"
    "  Color neutro/superficie: fondos y contenedores. 60-70% del area.\n"
    "  Color acento: badges, highlights. Max 10% del area.\n\n"

    "MOBILE-FIRST:\n"
    "  Disenar primero para 375px. En mobile: columna unica, stacks verticales.\n"
    "  Touch targets: minimo 44x44px para cualquier elemento interactivo.\n"
    "  CTAs visibles en mobile sin scroll. Texto legible sin zoom.\n\n"

    "NIELSEN -- 10 HEURISTICAS (traduccion a CSS/HTML):\n"
    "  1. Visibilidad del estado: loaders en botones de submit, feedback visual de acciones.\n"
    "  2. Lenguaje del usuario: labels en espanol claro, no jerga tecnica, no \'Submit\' en espanol.\n"
    "  3. Control y libertad: formularios con botones de cancelar o limpiar.\n"
    "  4. Consistencia: mismo radius, shadow y padding para cards del mismo tipo en todo el sitio.\n"
    "  5. Prevencion de errores: campos con placeholder descriptivo, validacion en tiempo real.\n"
    "  6. Reconocer antes que recordar: iconos con labels, opciones visibles (no ocultas en menús).\n"
    "  7. Flexibilidad: shortcuts de teclado en formularios, tab-index correcto.\n"
    "  8. DISENO ESTETICO Y MINIMALISTA (KISS):\n"
    "     - Eliminar todo elemento que no guie al usuario ni comunique algo.\n"
    "     - Maximo 2-3 colores de fondo distintos en todo el sitio.\n"
    "     - No sobrecargar con efectos: maximo 3 tipos de animacion distintos.\n"
    "     - Cada seccion tiene UN mensaje central. No apilar 5 ideas en una seccion.\n"
    "  9. Mensajes de error entendibles: si hay formulario, mostrar feedback en lenguaje humano.\n"
    "  10. Ayuda accesible: FAQs o tooltips para campos no obvios.\n\n"

    "CONTENTSQUARE -- PRINCIPIOS CLAVE:\n"
    "  Proposito claro: cada seccion tiene una razon de existir. No hay secciones de relleno.\n"
    "  Recorrido fluido: la pagina guia al usuario de la propuesta de valor al CTA naturalmente.\n"
    "  Sencillez: si no mejora la experiencia del usuario, no va.\n"
    "  Diseno unico: el sitio debe sentirse especifico para esta marca, no un template generico.\n"
    "  Coherencia: tipografias, colores y espaciados consistentes en todas las secciones.\n"
)
