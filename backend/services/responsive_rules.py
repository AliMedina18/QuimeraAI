"""
responsive_rules.py — Reglas de diseño responsive para el pipeline HTML de Quimera.

Exporta RESPONSIVE_SYSTEM_RULES: bloque de texto inyectado en el prompt del Step 3.
Fuentes: Polypane Ground Rules, Adsmurai Best Practices, WCAG 2.1.
"""

RESPONSIVE_SYSTEM_RULES = (
    "\n=== RESPONSIVE DESIGN -- REGLAS OBLIGATORIAS ===\n"
    "El sitio DEBE verse perfecto en: 320px, 768px, 1024px, 1440px.\n\n"
    "[R01] VIEWPORT META en <head>: <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
    "[R02] MOBILE-FIRST: CSS base para movil (320px). Queries solo con min-width en em:\n"
    "      @media (min-width:44em){/*tablet*/}  @media (min-width:64em){/*desktop*/}\n"
    "[R03] OVERFLOW: html,body { overflow-x:hidden; } -- nunca scroll horizontal en ningun breakpoint.\n"
    "[R04] SIN PX FIJOS en contenedores -- usar %, clamp(), fr, vw, max-width en su lugar.\n"
    "[R05] CONTAINER: width:100%; max-width:1200px; margin-inline:auto; padding-inline:clamp(1rem,5vw,3rem);\n"
    "[R06] GRIDS FLUIDOS: grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr)); gap:clamp(1rem,3vw,2rem);\n"
    "      Movil:1 col -- Tablet(44em):2 col -- Desktop(64em):3-4 col.\n"
    "[R07] FLEXBOX: flex-wrap:wrap; cada columna: flex:1 1 min(300px,100%);\n"
    "[R08] TIPOGRAFIA FLUIDA con clamp() en TODOS los headings -- nunca font-size fijo en px.\n"
    "      h1:clamp(2rem,5vw,4rem)  h2:clamp(1.5rem,3vw,2.5rem)  body:clamp(1rem,1.5vw,1.125rem)\n"
    "[R09] LINEA LEGIBLE: p,li{ max-width:72ch } -- previene lineas ultra-largas en widescreen.\n"
    "[R10] OVERFLOW DE TEXTO: overflow-wrap:break-word; en cards y contenedores con ancho acotado.\n"
    "[R11] IMAGENES FLUIDAS: img,video{ max-width:100%; height:auto; display:block; }\n"
    "[R12] ASPECT-RATIO en contenedores de imagen: 16/9 (card), 1/1 (avatar), 4/3 (hero).\n"
    "[R13] HAMBURGER en movil (<44em): .nav-links ocultos, .nav-toggle visible (min 44x44px).\n"
    "      JS: toggle .open en .nav-links al click.\n"
    "[R14] STICKY NAV: position:sticky; top:0; z-index:100; backdrop-filter:blur(12px);\n"
    "[R15] TOUCH TARGETS: button,a,[role=button]{ min-height:44px; min-width:44px; } (WCAG 2.5.5)\n"
    "[R16] INPUTS: width:100% en movil. Desktop: grid 2col con @media(min-width:44em).\n"
    "[R17] HERO MOVIL: flex-direction:column, imagen debajo del texto o como background.\n"
    "[R18] CARDS: height:auto siempre -- nunca height fija.\n"
    "[R19] TABLAS: envolver en <div style='overflow-x:auto'> si existen.\n"
    "[R20] PADDING MOVIL: cada seccion tiene padding-inline >= 1rem; ningun texto toca el borde.\n"
    "[R21] SAFE AREAS: body{ padding-top:env(safe-area-inset-top); padding-bottom:env(safe-area-inset-bottom); }\n\n"
)
