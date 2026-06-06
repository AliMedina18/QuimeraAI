"""
color_harmony.py -- Criterio 1: Armonia Cromatica (OKLCH)
=========================================================
Scorer algoritmico y deterministico.
Dado el mismo input, siempre produce el mismo output.

Espacio de color OKLCH:
  L = Lightness (luminosidad perceptual, 0-1)
  C = Chroma    (saturacion, 0-0.4 aprox.)
  H = Hue       (angulo en el circulo cromatico, 0-360 grados)

Por que OKLCH en vez de HSL:
  HSL tiene luminosidad no uniforme: un amarillo al 50% de L se ve mas brillante
  que un azul al mismo 50%. OKLCH corrige esto: su escala L es perceptualmente
  uniforme, igual a como lo percibe el ojo humano.

Armonias soportadas:
  - Complementaria : ~180 grados (tolerancia 40)
  - Analoga        : ~30  grados (tolerancia 25)
  - Triadica       : ~120 grados (tolerancia 20)
  - Monocromatica  : ~0   grados (tolerancia 30)

Libreria: colour-science (pip install colour-science)
"""

import math
import logging
from typing import Optional

import numpy as np
import colour

logger = logging.getLogger(__name__)

# Tolerancias angulares para cada tipo de armonia (angulo_objetivo, tolerancia)
HARMONY_TOLERANCES = {
    "complementario": (180.0, 40.0),
    "analogo":        (30.0,  25.0),
    "triadico":       (120.0, 20.0),
    "monocromatico":  (0.0,   30.0),
}

# Offsets de rotacion H para generar paletas armonicas
HARMONY_ROTATIONS = {
    "complementario": [0, 180],
    "analogo":        [0, 30, -30],
    "triadico":       [0, 120, 240],
    "monocromatico":  [0, 0, 0],  # mismo H, diferente L y C
}


def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    """
    Convierte un color hexadecimal a coordenadas OKLCH usando colour-science.

    Args:
        hex_color: Color en formato '#RRGGBB' o 'RRGGBB'.

    Returns:
        Tupla (L, C, H) donde H esta en grados (0-360).

    Raises:
        ValueError: Si el hex no es valido.
    """
    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) != 6:
        raise ValueError(f"Hex invalido: {hex_color}")
    try:
        int(hex_clean, 16)
    except ValueError:
        raise ValueError(f"Hex invalido: {hex_color}")

    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0

    rgb = np.array([r, g, b])
    xyz = colour.sRGB_to_XYZ(rgb)
    oklab = colour.XYZ_to_Oklab(xyz)

    L = float(oklab[0])
    a = float(oklab[1])
    b2 = float(oklab[2])
    C = math.sqrt(a ** 2 + b2 ** 2)
    H = math.degrees(math.atan2(b2, a)) % 360

    return (L, C, H)


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """
    Convierte coordenadas OKLCH a hexadecimal RGB.

    Args:
        L: Luminosidad (0-1)
        C: Chroma (0-0.4 aprox)
        H: Hue en grados (0-360)

    Returns:
        Color en formato '#RRGGBB'.
    """
    H_rad = math.radians(H)
    a = C * math.cos(H_rad)
    b = C * math.sin(H_rad)

    oklab = np.array([L, a, b])
    xyz = colour.Oklab_to_XYZ(oklab)
    rgb = colour.XYZ_to_sRGB(xyz)

    # Clamp a [0, 1]
    rgb = np.clip(rgb, 0.0, 1.0)

    r = int(round(rgb[0] * 255))
    g = int(round(rgb[1] * 255))
    b2 = int(round(rgb[2] * 255))

    return f"#{r:02X}{g:02X}{b2:02X}"


def angular_difference(angle1: float, angle2: float) -> float:
    """
    Calcula la diferencia minima entre dos angulos en el circulo cromatico.
    El resultado siempre esta en [0, 180].

    Ejemplo: angular_difference(10, 350) = 20 (no 340)
    """
    diff = abs(angle1 - angle2) % 360
    return min(diff, 360 - diff)


def get_harmony_type(hue_angles: list[float]) -> Optional[str]:
    """
    Determina el tipo de armonia cromatica dado un conjunto de angulos hue.

    Args:
        hue_angles: Lista de angulos H (0-360 grados) extraidos de la paleta.

    Returns:
        Nombre de la armonia detectada, o None si no hay armonia reconocible.
    """
    if len(hue_angles) < 2:
        return "monocromatico"

    # Calcular todas las diferencias entre pares
    diffs = [
        angular_difference(hue_angles[i], hue_angles[j])
        for i in range(len(hue_angles))
        for j in range(i + 1, len(hue_angles))
    ]

    if not diffs:
        return "monocromatico"

    max_diff = max(diffs)
    min_diff = min(diffs)

    # Monocromatico: todos los colores muy similares en hue
    if max_diff <= HARMONY_TOLERANCES["monocromatico"][1]:
        return "monocromatico"

    # Para 2 colores: detectar por diferencia unica
    if len(hue_angles) == 2:
        diff = diffs[0]
        for harmony_name, (target, tol) in HARMONY_TOLERANCES.items():
            if harmony_name == "monocromatico":
                continue
            if abs(diff - target) <= tol:
                return harmony_name
        return None

    # Para 3+ colores: detectar triadica (diferencias cercanas a 120)
    if len(hue_angles) >= 3:
        avg_diff = sum(diffs) / len(diffs)
        target_tri, tol_tri = HARMONY_TOLERANCES["triadico"]
        if abs(avg_diff - target_tri) <= tol_tri:
            return "triadico"

        # Analoga: todas las diferencias pequenas
        target_ana, tol_ana = HARMONY_TOLERANCES["analogo"]
        if max_diff <= target_ana + tol_ana:
            return "analogo"

    return None


def generate_harmonic_palette(primary_hex: str, harmony: str) -> dict:
    """
    Dado un color primario y un tipo de armonia, calcula los colores secundario y acento.

    Args:
        primary_hex: Color primario en hex (ej: '#1E40AF').
        harmony: 'complementario' | 'analogo' | 'triadico' | 'monocromatico'

    Returns:
        Dict con: {primary, secondary, accent, neutral_palette}
    """
    try:
        L, C, H = hex_to_oklch(primary_hex)
        rotations = HARMONY_ROTATIONS.get(harmony, [0, 180])

        if harmony == "monocromatico":
            # Misma familia de color, diferente luminosidad
            secondary = oklch_to_hex(min(L + 0.2, 0.95), C * 0.7, H)
            accent = oklch_to_hex(max(L - 0.15, 0.1), C * 1.2, H)
        else:
            h_secondary = (H + rotations[1]) % 360
            h_accent = (H + rotations[-1]) % 360 if len(rotations) > 2 else (H + rotations[1] + 30) % 360
            secondary = oklch_to_hex(L, C * 0.85, h_secondary)
            accent = oklch_to_hex(min(L + 0.1, 0.95), C * 1.1, h_accent)

        # Paleta neutral basada en el hue primario (muy poca saturacion)
        neutral_palette = [
            oklch_to_hex(0.98, C * 0.05, H),  # casi blanco con tinte
            oklch_to_hex(0.93, C * 0.08, H),  # gris claro
            oklch_to_hex(0.55, C * 0.10, H),  # gris medio
            oklch_to_hex(0.20, C * 0.08, H),  # casi negro con tinte
        ]

        return {
            "primary": primary_hex,
            "secondary": secondary,
            "accent": accent,
            "neutral_palette": neutral_palette,
        }

    except Exception as e:
        logger.error("Error en generate_harmonic_palette: %s", e)
        return {
            "primary": primary_hex,
            "secondary": "#CCCCCC",
            "accent": "#888888",
            "neutral_palette": ["#F8FAFC", "#E2E8F0", "#64748B", "#1E293B"],
        }


def score_color_harmony(palette: list[str]) -> float:
    """
    Criterio 1: Calcula el score de armonia cromatica de una paleta.

    Algoritmo:
        1. Convertir todos los hex a OKLCH
        2. Extraer angulos H de cada color
        3. Detectar si los angulos corresponden a una armonia conocida
        4. Penalizar si la variacion de Chroma (saturacion) es muy alta
        5. Penalizar colores sin relacion cromatica identificable

    Args:
        palette: Lista de colores en hex ['#hex1', '#hex2', ...]

    Returns:
        Score de 0 a 100.
    """
    if not palette:
        return 0.0

    valid_colors = [c for c in palette if c and len(c.lstrip("#")) == 6]
    if len(valid_colors) < 2:
        return 50.0  # Solo 1 color: neutral

    try:
        oklch_colors = [hex_to_oklch(c) for c in valid_colors]
        hue_angles = [lch[2] for lch in oklch_colors]
        chroma_values = [lch[1] for lch in oklch_colors]

        harmony = get_harmony_type(hue_angles)

        score_map = {
            "complementario": 92.0,
            "analogo":        88.0,
            "triadico":       85.0,
            "monocromatico":  80.0,
        }
        base_score = score_map.get(harmony, 40.0) if harmony else 40.0

        # Penalizacion por inconsistencia de saturacion
        if len(chroma_values) > 1:
            chroma_range = max(chroma_values) - min(chroma_values)
            if chroma_range > 0.25:
                base_score -= 10.0

        return max(0.0, min(100.0, base_score))

    except Exception as e:
        logger.error("Error calculando color harmony: %s", e)
        return 0.0
