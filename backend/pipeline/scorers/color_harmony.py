"""
color_harmony.py — Criterio 1: Armonía Cromática (OKLCH)
=========================================================
Scorer algorítmico y determinístico.
Dado el mismo input, siempre produce el mismo output.

Espacio de color OKLCH:
  L = Lightness (luminosidad perceptual, 0-1)
  C = Chroma    (saturación, 0-0.4 aprox.)
  H = Hue       (ángulo en el círculo cromático, 0-360°)

Por qué OKLCH en vez de HSL:
  HSL tiene luminosidad no uniforme: un amarillo al 50% de L se ve más brillante
  que un azul al mismo 50%. OKLCH corrige esto: su escala L es perceptualmente
  uniforme, igual a como lo percibe el ojo humano.

Armonías soportadas:
  - Complementaria : 180° (±15° tolerancia)
  - Análoga        : 30°  (±10° tolerancia)
  - Triádica       : 120° (±15° tolerancia)
  - Tetrádica      : 90°  (±15° tolerancia)
  - Monocromática  : 0°   (misma familia, ±20° tolerancia)

Librería: colour-science (pip install colour-science)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Tolerancias angulares para cada tipo de armonía
HARMONY_TOLERANCES = {
    "complementario": (180.0, 15.0),  # (ángulo_objetivo, tolerancia)
    "análogo":        (30.0,  10.0),
    "triádico":       (120.0, 15.0),
    "tetrádico":      (90.0,  15.0),
    "monocromático":  (0.0,   20.0),
}


def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    """
    Convierte un color hexadecimal a coordenadas OKLCH.

    Args:
        hex_color: Color en formato '#RRGGBB' o 'RRGGBB'.

    Returns:
        Tupla (L, C, H) donde H está en grados (0-360).

    Raises:
        ValueError: Si el hex no es válido.

    TODO Día 2/3: implementar con colour-science.
    Ejemplo de implementación:
        import colour
        hex_clean = hex_color.lstrip('#')
        r, g, b = [int(hex_clean[i:i+2], 16) / 255 for i in (0, 2, 4)]
        rgb = colour.RGB_to_XYZ(np.array([r, g, b]), ...)
        oklch = colour.XYZ_to_Oklab(rgb)  # luego Oklab → OKLCH
    """
    # TODO Día 3: implementar con colour-science
    # Por ahora retornamos valores placeholder
    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) != 6:
        raise ValueError(f"Hex inválido: {hex_color}")
    r = int(hex_clean[0:2], 16) / 255
    g = int(hex_clean[2:4], 16) / 255
    b = int(hex_clean[4:6], 16) / 255
    # Placeholder: convertir RGB a HSL y aproximar H como ángulo OKLCH
    import colorsys
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (l, s, h * 360)


def angular_difference(angle1: float, angle2: float) -> float:
    """
    Calcula la diferencia mínima entre dos ángulos en el círculo cromático.
    El resultado siempre está en [0, 180].

    Ejemplo: angular_difference(10, 350) = 20 (no 340)
    """
    diff = abs(angle1 - angle2) % 360
    return min(diff, 360 - diff)


def get_harmony_type(hue_angles: list[float]) -> Optional[str]:
    """
    Determina el tipo de armonía cromática dado un conjunto de ángulos hue.

    Args:
        hue_angles: Lista de ángulos H (0-360°) extraídos de la paleta.

    Returns:
        Nombre de la armonía detectada, o None si no hay armonía reconocible.

    Lógica:
        Para 2 colores: verificar si la diferencia angular corresponde a
          complementaria, análoga, o monocromática.
        Para 3+ colores: verificar todas las diferencias entre pares.

    TODO Día 2/3: implementar lógica completa.
    """
    if len(hue_angles) < 2:
        return "monocromático"

    # Para cada tipo de armonía, verificar si todos los pares cumplen la tolerancia
    for harmony_name, (target_angle, tolerance) in HARMONY_TOLERANCES.items():
        if harmony_name == "monocromático":
            # Todos los colores deben tener ángulos muy similares
            max_diff = max(
                angular_difference(hue_angles[i], hue_angles[j])
                for i in range(len(hue_angles))
                for j in range(i + 1, len(hue_angles))
            )
            if max_diff <= tolerance:
                return harmony_name
        elif len(hue_angles) == 2:
            diff = angular_difference(hue_angles[0], hue_angles[1])
            if abs(diff - target_angle) <= tolerance:
                return harmony_name

    return None  # No se detectó armonía reconocible


def generate_harmonic_palette(primary_hex: str, harmony: str) -> dict:
    """
    Dado un color primario y un tipo de armonía, calcula los colores secundario y de acento.

    Args:
        primary_hex: Color primario en hex.
        harmony: 'complementario' | 'análogo' | 'triádico' | 'monocromático'

    Returns:
        Dict con: {primary, secondary, accent, neutral_palette}

    TODO Día 2: implementar con colour-science y rotaciones OKLCH.
    """
    # TODO Día 2/3: implementar
    logger.warning("generate_harmonic_palette: stub — implementar en Día 2")
    return {
        "primary": primary_hex,
        "secondary": "#CCCCCC",  # placeholder
        "accent": "#888888",     # placeholder
        "neutral_palette": ["#F8FAFC", "#E2E8F0", "#64748B", "#1E293B"],
    }


def score_color_harmony(palette: list[str]) -> float:
    """
    Criterio 1: Calcula el score de armonía cromática de una paleta.

    Algoritmo:
        1. Convertir todos los hex a OKLCH
        2. Extraer ángulos H de cada color
        3. Detectar si los ángulos corresponden a una armonía conocida
        4. Penalizar si la variación de Chroma (saturación) es muy alta
        5. Penalizar colores sin relación cromática identificable

    Args:
        palette: Lista de colores en hex ['#hex1', '#hex2', ...]

    Returns:
        Score de 0 a 100.
        100 = armonía perfecta
        0   = colores sin ninguna relación cromática

    Ejemplos de scores esperados (para los tests del Día 3):
        ['#0000FF', '#FF8C00']   → ~90 (complementario azul/naranja)
        ['#1E40AF', '#3B82F6']   → ~85 (análogo, misma familia azul)
        ['#FF0000', '#00FF00', '#0000FF'] → ~88 (triádico)
        ['#FF0000', '#FFFF00']   → ~30 (sin armonía clara)

    TODO Día 3: implementar con colour-science.
    """
    if not palette:
        return 0.0

    # Filtrar valores None o vacíos
    valid_colors = [c for c in palette if c and len(c) >= 7]
    if len(valid_colors) < 2:
        return 50.0  # Solo 1 color: neutral

    try:
        oklch_colors = [hex_to_oklch(c) for c in valid_colors]
        hue_angles = [lch[2] for lch in oklch_colors]
        chroma_values = [lch[1] for lch in oklch_colors]

        harmony = get_harmony_type(hue_angles)

        if harmony is None:
            base_score = 40.0  # Sin armonía reconocible
        elif harmony == "complementario":
            base_score = 92.0
        elif harmony == "análogo":
            base_score = 88.0
        elif harmony == "triádico":
            base_score = 85.0
        elif harmony == "monocromático":
            base_score = 80.0
        else:
            base_score = 75.0

        # Penalización por inconsistencia de saturación
        if len(chroma_values) > 1:
            chroma_range = max(chroma_values) - min(chroma_values)
            if chroma_range > 0.3:  # Alta variación de saturación
                base_score -= 10.0

        return max(0.0, min(100.0, base_score))

    except Exception as e:
        logger.error("Error calculando color harmony: %s", e)
        return 0.0
