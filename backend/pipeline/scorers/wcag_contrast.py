"""
wcag_contrast.py — Criterio 2: Contraste WCAG 2.1
==================================================
Scorer algorítmico y determinístico.
Implementa el estándar W3C WCAG 2.1 para accesibilidad de contraste.

La fórmula WCAG es matemáticamente exacta. Negros sobre blanco siempre = 21:1.
No hay ambigüedad ni aleatoriedad.

Fórmula:
    ratio = (L_claro + 0.05) / (L_oscuro + 0.05)

Donde L es la luminancia relativa:
    L = 0.2126·R_lin + 0.7152·G_lin + 0.0722·B_lin

    La linearización aplica gamma expansion:
    si canal <= 0.04045: canal / 12.92
    si canal > 0.04045:  ((canal + 0.055) / 1.055) ^ 2.4

Niveles WCAG:
    AA  (mínimo): 4.5:1 para texto normal, 3:1 para texto grande (≥18pt o 14pt bold)
    AAA (óptimo): 7:1 para texto normal

Sin dependencias externas. Python puro.
"""

import logging

logger = logging.getLogger(__name__)


def linearize_channel(channel: float) -> float:
    """
    Aplica gamma expansion a un canal RGB normalizado (0-1).
    Convierte de espacio gamma (sRGB) a espacio lineal.

    Los monitores aplican una corrección gamma al mostrar colores.
    Para calcular la luminancia física real debemos deshacerla.

    Args:
        channel: Valor del canal en [0, 1].

    Returns:
        Valor linearizado en [0, 1].
    """
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def calculate_relative_luminance(hex_color: str) -> float:
    """
    Calcula la luminancia relativa de un color según WCAG 2.1.
    Rango: 0 (negro absoluto) a 1 (blanco absoluto).

    Args:
        hex_color: Color en formato '#RRGGBB' o 'RRGGBB'.

    Returns:
        Luminancia relativa [0, 1].

    Ejemplos:
        '#000000' → 0.0       (negro)
        '#FFFFFF' → 1.0       (blanco)
        '#FF0000' → 0.2126    (rojo puro — contribución del canal R)
        '#767676' → 0.2158    (gris que bordea el 4.5:1 sobre blanco)
    """
    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) != 6:
        raise ValueError(f"Hex inválido: '{hex_color}'. Formato esperado: #RRGGBB")

    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0

    r_lin = linearize_channel(r)
    g_lin = linearize_channel(g)
    b_lin = linearize_channel(b)

    # Pesos perceptuales estándar ITU-R BT.709
    # El ojo humano es más sensible al verde (0.7152) que al rojo (0.2126) o azul (0.0722)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def calculate_wcag_ratio(foreground: str, background: str) -> float:
    """
    Calcula el ratio de contraste WCAG entre texto y fondo.

    Args:
        foreground: Color del texto en hex.
        background: Color del fondo en hex.

    Returns:
        Ratio de contraste [1.0, 21.0].
        1:1 = sin contraste (mismo color).
        21:1 = máximo contraste (negro sobre blanco).

    Invariante: foreground y background son intercambiables.
    calculate_wcag_ratio('#000000', '#FFFFFF') == calculate_wcag_ratio('#FFFFFF', '#000000') == 21.0
    """
    l1 = calculate_relative_luminance(foreground)
    l2 = calculate_relative_luminance(background)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def classify_wcag_level(ratio: float, is_large_text: bool = False) -> str:
    """
    Clasifica un ratio de contraste según el nivel WCAG que cumple.

    Args:
        ratio: Ratio de contraste calculado con calculate_wcag_ratio().
        is_large_text: True si el texto es ≥18pt o ≥14pt bold.

    Returns:
        'AAA' | 'AA' | 'AA_large' | 'FAIL'
    """
    if ratio >= 7.0:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if is_large_text and ratio >= 3.0:
        return "AA_large"
    return "FAIL"


def score_wcag_contrast(context) -> float:
    """
    Criterio 2: Evalúa el contraste de todos los pares texto/fondo del diseño.

    Pares evaluados:
        1. primary_color (texto) sobre neutrales[0] (fondo más claro)
        2. primary_color (texto) sobre neutrales[-1] (fondo más oscuro)
        3. neutrales[-1] (texto oscuro) sobre neutrales[0] (fondo claro) — el par más común
        4. accent_color sobre neutrales[0]

    Penalizaciones:
        -15 puntos por par que no alcance 4.5:1 (WCAG AA)
        -8  puntos por par entre 3:1 y 4.5:1 (solo pasa texto grande)
        -5  puntos si ningún par alcanza 7:1 (WCAG AAA)

    Args:
        context: DesignContext con primary_color, accent_color, neutral_palette.

    Returns:
        Score de 0 a 100.

    Ejemplos esperados (para tests del Día 3):
        '#000000' sobre '#FFFFFF' → ~100 (ratio 21:1, perfecta accesibilidad)
        '#767676' sobre '#FFFFFF' → ~70  (ratio ~4.48:1, bordea el mínimo)
        '#AAAAAA' sobre '#FFFFFF' → ~30  (ratio ~2.3:1, falla WCAG AA)

    TODO Día 3: refinar el cálculo de pares y las penalizaciones.
    """
    if not context.primary_color or not context.neutral_palette:
        logger.warning("score_wcag_contrast: faltan colores en el contexto")
        return 50.0  # Score neutral si no hay datos suficientes

    score = 100.0
    evaluated_pairs = []

    # Definir los pares a evaluar
    bg_light = context.neutral_palette[0] if context.neutral_palette else "#FFFFFF"
    bg_dark = context.neutral_palette[-1] if len(context.neutral_palette) > 1 else "#000000"

    pairs = [
        (context.primary_color, bg_light, "primary sobre fondo claro"),
        (bg_dark, bg_light, "texto oscuro sobre fondo claro"),
    ]

    if context.secondary_color:
        pairs.append((context.secondary_color, bg_light, "secondary sobre fondo claro"))

    if context.accent_color:
        pairs.append((context.accent_color, bg_light, "accent sobre fondo claro"))

    for fg, bg, label in pairs:
        try:
            ratio = calculate_wcag_ratio(fg, bg)
            level = classify_wcag_level(ratio)
            evaluated_pairs.append((label, ratio, level))

            if level == "FAIL":
                score -= 15.0
                logger.debug("Par '%s': ratio %.1f:1 — FALLA WCAG AA", label, ratio)
            elif level == "AA_large":
                score -= 8.0
                logger.debug("Par '%s': ratio %.1f:1 — solo pasa texto grande", label, ratio)
            else:
                logger.debug("Par '%s': ratio %.1f:1 — %s", label, ratio, level)

        except ValueError as e:
            logger.warning("Error evaluando par '%s': %s", label, e)
            score -= 10.0  # Penalizar color inválido

    # Bonus si todos los pares tienen ratio muy alto (AAA)
    if all(level in ("AA", "AAA") for _, _, level in evaluated_pairs):
        aaa_count = sum(1 for _, _, level in evaluated_pairs if level == "AAA")
        if aaa_count == len(evaluated_pairs):
            score = min(100.0, score + 5.0)  # Bonus por excelencia en accesibilidad

    return max(0.0, min(100.0, score))
