"""
wcag_contrast.py — Cálculo WCAG 2.1 de contraste de color
===========================================================
Funciones puras y determinísticas.
Sin dependencias externas. Python puro.

Fórmula WCAG:
    ratio = (L_claro + 0.05) / (L_oscuro + 0.05)

Donde L es la luminancia relativa:
    L = 0.2126·R_lin + 0.7152·G_lin + 0.0722·B_lin

    La linearización aplica gamma expansion:
    si canal <= 0.04045: canal / 12.92
    si canal > 0.04045:  ((canal + 0.055) / 1.055) ^ 2.4

Niveles WCAG:
    AA  (mínimo): 4.5:1 para texto normal, 3:1 para texto grande (≥18pt o 14pt bold)
    AAA (óptimo): 7:1 para texto normal

Uso:
    from backend.pipeline.scorers.wcag_contrast import calculate_wcag_ratio, classify_wcag_level

    ratio = calculate_wcag_ratio('#000000', '#FFFFFF')  # 21.0
    level = classify_wcag_level(ratio)                   # 'AAA'
"""

import logging

logger = logging.getLogger(__name__)


def linearize_channel(channel: float) -> float:
    """
    Aplica gamma expansion a un canal RGB normalizado (0-1).
    Convierte de espacio gamma (sRGB) a espacio lineal.

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
        '#FF0000' → 0.2126    (rojo puro)
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


def validate_pair(text_color: str, bg_color: str, label: str = "") -> dict:
    """
    Valida un par texto/fondo completo y retorna resultado estructurado.

    Args:
        text_color: Color del texto en hex.
        bg_color: Color del fondo en hex.
        label: Etiqueta descriptiva del par (para logging).

    Returns:
        Dict con: ratio, level, passes_aa, passes_aaa
    """
    try:
        ratio = calculate_wcag_ratio(text_color, bg_color)
        level = classify_wcag_level(ratio)
        result = {
            "ratio": round(ratio, 2),
            "level": level,
            "passes_aa": level in ("AA", "AAA"),
            "passes_aaa": level == "AAA",
            "text_color": text_color,
            "bg_color": bg_color,
        }
        if label:
            logger.debug("WCAG %s: %s sobre %s → %.1f:1 (%s)",
                         label, text_color, bg_color, ratio, level)
        return result
    except ValueError as e:
        logger.warning("Color inválido en par '%s': %s", label, e)
        return {
            "ratio": 0.0,
            "level": "FAIL",
            "passes_aa": False,
            "passes_aaa": False,
            "text_color": text_color,
            "bg_color": bg_color,
            "error": str(e),
        }
