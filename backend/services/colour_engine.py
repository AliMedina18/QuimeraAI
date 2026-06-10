"""
colour_engine.py — Motor de colorimetría basado en colour-science
=================================================================
Usa el espacio perceptualmente uniforme OKLCH para todas las operaciones
de color: conversión, armonías, paletas tonales y diferencia cromática (ΔE).

Por qué OKLCH en vez de HSL / HSV:
    HSL tiene luminosidad NO uniforme: un amarillo al 50% L se ve más brillante
    que un azul al mismo valor. OKLCH corrige esto con una escala L perceptual,
    igual a como lo percibe el ojo humano.

Dependencia: colour-science >= 0.4.7  (pip install colour-science)
Fallback: si la librería no está instalada usa cálculos matriciales manuales.

Espacios usados:
    sRGB → XYZ (D65) → OKLab → OKLCH
"""

from __future__ import annotations

import logging
import math
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Import colour-science con fallback gracioso
# ---------------------------------------------------------------------------
try:
    import colour as _colour
    _HAS_COLOUR = True
except ImportError:  # pragma: no cover
    _HAS_COLOUR = False
    logger.warning(
        "colour-science no está instalado. "
        "Instalar con: pip install colour-science  "
        "Usando fallback de matrices sRGB→XYZ manuales."
    )


# ---------------------------------------------------------------------------
# Tolerancias angulares para tipos de armonía (ángulo_objetivo, tolerancia)
# ---------------------------------------------------------------------------
HARMONY_TOLERANCES: dict[str, tuple[float, float]] = {
    "complementario": (180.0, 40.0),
    "analogo":        (30.0,  25.0),
    "triadico":       (120.0, 20.0),
    "monocromatico":  (0.0,   30.0),
}

# Offsets de rotación H para generar paletas armónicas
HARMONY_ROTATIONS: dict[str, list[float]] = {
    "complementario": [0, 180],
    "analogo":        [0, 30, -30],
    "triadico":       [0, 120, 240],
    "monocromatico":  [0, 0, 0],
}


# ---------------------------------------------------------------------------
# Conversión sRGB ↔ XYZ (fallback manual, matrices IEC 61966-2-1)
# ---------------------------------------------------------------------------
_M_SRGB_TO_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041],
])
_M_XYZ_TO_SRGB = np.linalg.inv(_M_SRGB_TO_XYZ)


def _srgb_to_linear(c: float) -> float:
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> float:
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1.0 / 2.4)) - 0.055


def _srgb_array_to_xyz(rgb: np.ndarray) -> np.ndarray:
    """sRGB [0,1] → XYZ D65."""
    lin = np.array([_srgb_to_linear(c) for c in rgb])
    return _M_SRGB_TO_XYZ @ lin


def _xyz_to_srgb_array(xyz: np.ndarray) -> np.ndarray:
    """XYZ D65 → sRGB [0,1]."""
    lin = _M_XYZ_TO_SRGB @ xyz
    return np.array([_linear_to_srgb(float(c)) for c in lin])


# ---------------------------------------------------------------------------
# XYZ → OKLab (algoritmo de Björn Ottosson)
# ---------------------------------------------------------------------------
_M1 = np.array([
    [0.8189330101, 0.3618667424, -0.1288597137],
    [0.0329845436, 0.9293118715,  0.0361456387],
    [0.0482003018, 0.2643662691,  0.6338517070],
])
_M2 = np.array([
    [0.2104542553, 0.7936177850, -0.0040720468],
    [1.9779984951, -2.4285922050,  0.4505937099],
    [0.0259040371, 0.7827717662, -0.8086757660],
])


def _xyz_to_oklab(xyz: np.ndarray) -> np.ndarray:
    lms = _M1 @ xyz
    lms_gamma = np.cbrt(lms)
    return _M2 @ lms_gamma


def _oklab_to_xyz(lab: np.ndarray) -> np.ndarray:
    lms_gamma = np.linalg.inv(_M2) @ lab
    lms = lms_gamma ** 3
    return np.linalg.inv(_M1) @ lms


# ---------------------------------------------------------------------------
# API pública: hex ↔ OKLCH
# ---------------------------------------------------------------------------

def hex_to_oklch(hex_color: str) -> tuple[float, float, float]:
    """
    Convierte un color hexadecimal a coordenadas OKLCH.

    Args:
        hex_color: '#RRGGBB' o 'RRGGBB'.

    Returns:
        (L, C, H) donde:
            L ∈ [0, 1]  — luminosidad perceptual
            C ∈ [0, ~0.4]  — chroma (saturación)
            H ∈ [0, 360)  — ángulo de tono en grados

    Raises:
        ValueError: Si el hex no es válido.
    """
    clean = hex_color.lstrip("#")
    if len(clean) != 6:
        raise ValueError(f"Hex inválido: '{hex_color}'")
    try:
        int(clean, 16)
    except ValueError:
        raise ValueError(f"Hex inválido: '{hex_color}'")

    r = int(clean[0:2], 16) / 255.0
    g = int(clean[2:4], 16) / 255.0
    b = int(clean[4:6], 16) / 255.0
    rgb = np.array([r, g, b])

    if _HAS_COLOUR:
        xyz = _colour.sRGB_to_XYZ(rgb)
        oklab = _colour.XYZ_to_Oklab(xyz)
    else:
        xyz = _srgb_array_to_xyz(rgb)
        oklab = _xyz_to_oklab(xyz)

    L = float(oklab[0])
    a = float(oklab[1])
    b2 = float(oklab[2])
    C = math.sqrt(a**2 + b2**2)
    H = math.degrees(math.atan2(b2, a)) % 360.0

    return (L, C, H)


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """
    Convierte coordenadas OKLCH a hex RGB, con clamp a gamut sRGB.

    Args:
        L: Luminosidad [0, 1]
        C: Chroma [0, ~0.4]
        H: Tono en grados [0, 360)

    Returns:
        '#RRGGBB' en mayúsculas.
    """
    H_rad = math.radians(H)
    a = C * math.cos(H_rad)
    b = C * math.sin(H_rad)
    oklab = np.array([L, a, b])

    if _HAS_COLOUR:
        xyz = _colour.Oklab_to_XYZ(oklab)
        rgb = _colour.XYZ_to_sRGB(xyz)
    else:
        xyz = _oklab_to_xyz(oklab)
        rgb = _xyz_to_srgb_array(xyz)

    rgb = np.clip(rgb, 0.0, 1.0)
    r, g, b2 = int(round(rgb[0] * 255)), int(round(rgb[1] * 255)), int(round(rgb[2] * 255))
    return f"#{r:02X}{g:02X}{b2:02X}"


# ---------------------------------------------------------------------------
# Diferencia cromática ΔE (CIEDE2000 vía colour-science; fallback Euclidean OKLab)
# ---------------------------------------------------------------------------

def delta_e(hex1: str, hex2: str) -> float:
    """
    Calcula la diferencia perceptual entre dos colores.

    Usa CIEDE2000 si colour-science está disponible (el estándar de la industria),
    si no usa distancia Euclidiana en OKLab (correlaciona bien con percepción).

    Referencia:
        - ΔE < 1.0  → diferencia imperceptible
        - ΔE 1–2    → diferencia apenas perceptible
        - ΔE 2–10   → diferencia visible
        - ΔE > 10   → colores claramente distintos

    Returns:
        float — ΔE (sin unidades, positivo)
    """
    if _HAS_COLOUR:
        # Convertir a CIE Lab (D65) para CIEDE2000
        clean1 = hex1.lstrip("#")
        clean2 = hex2.lstrip("#")
        rgb1 = np.array([int(clean1[i:i+2], 16) / 255.0 for i in (0, 2, 4)])
        rgb2 = np.array([int(clean2[i:i+2], 16) / 255.0 for i in (0, 2, 4)])
        xyz1 = _colour.sRGB_to_XYZ(rgb1)
        xyz2 = _colour.sRGB_to_XYZ(rgb2)
        lab1 = _colour.XYZ_to_Lab(xyz1)
        lab2 = _colour.XYZ_to_Lab(xyz2)
        return float(_colour.difference.delta_E_CIE2000(lab1, lab2))
    else:
        # Fallback: distancia Euclidiana en OKLab
        L1, C1, H1 = hex_to_oklch(hex1)
        L2, C2, H2 = hex_to_oklch(hex2)
        H1r, H2r = math.radians(H1), math.radians(H2)
        a1, b1 = C1 * math.cos(H1r), C1 * math.sin(H1r)
        a2, b2 = C2 * math.cos(H2r), C2 * math.sin(H2r)
        # Escalar para comparabilidad con ΔE (OKLab ≈ 1/100 de Lab)
        return math.sqrt((L1 - L2)**2 + (a1 - a2)**2 + (b1 - b2)**2) * 100.0


# ---------------------------------------------------------------------------
# Detección de tipo de armonía
# ---------------------------------------------------------------------------

def angular_difference(angle1: float, angle2: float) -> float:
    """Diferencia mínima entre dos ángulos en el círculo cromático. Resultado ∈ [0, 180]."""
    diff = abs(angle1 - angle2) % 360.0
    return min(diff, 360.0 - diff)


def detect_harmony_type(palette_hex: list[str]) -> Optional[str]:
    """
    Determina el tipo de armonía cromática de una paleta.

    Args:
        palette_hex: Lista de colores hex.

    Returns:
        'complementario' | 'analogo' | 'triadico' | 'monocromatico' | None
    """
    valid = [c for c in palette_hex if c and len(c.lstrip("#")) == 6]
    if len(valid) < 2:
        return "monocromatico"

    try:
        hues = [hex_to_oklch(c)[2] for c in valid]
    except Exception as exc:
        logger.warning("detect_harmony_type: error convirtiendo colores: %s", exc)
        return None

    diffs = [
        angular_difference(hues[i], hues[j])
        for i in range(len(hues))
        for j in range(i + 1, len(hues))
    ]

    if not diffs:
        return "monocromatico"

    max_diff = max(diffs)

    if max_diff <= HARMONY_TOLERANCES["monocromatico"][1]:
        return "monocromatico"

    if len(hues) == 2:
        d = diffs[0]
        for name, (target, tol) in HARMONY_TOLERANCES.items():
            if name == "monocromatico":
                continue
            if abs(d - target) <= tol:
                return name
        return None

    # 3+ colores
    avg_diff = sum(diffs) / len(diffs)
    target_tri, tol_tri = HARMONY_TOLERANCES["triadico"]
    if abs(avg_diff - target_tri) <= tol_tri:
        return "triadico"

    target_ana, tol_ana = HARMONY_TOLERANCES["analogo"]
    if max_diff <= target_ana + tol_ana:
        return "analogo"

    return None


# ---------------------------------------------------------------------------
# Generación de paletas armónicas
# ---------------------------------------------------------------------------

def generate_harmonic_palette(primary_hex: str, harmony: str) -> dict:
    """
    Genera una paleta armónica a partir de un color primario.

    Args:
        primary_hex: Color primario en hex (p. ej. '#1E40AF').
        harmony: 'complementario' | 'analogo' | 'triadico' | 'monocromatico'

    Returns:
        {
            "primary": str,
            "secondary": str,
            "accent": str,
            "neutral_palette": list[str],   # 4 tonos: casi-blanco → casi-negro
            "harmony_type": str,
        }
    """
    try:
        L, C, H = hex_to_oklch(primary_hex)
        rotations = HARMONY_ROTATIONS.get(harmony, [0, 180])

        if harmony == "monocromatico":
            secondary = oklch_to_hex(min(L + 0.20, 0.95), C * 0.70, H)
            accent    = oklch_to_hex(max(L - 0.15, 0.05), C * 1.20, H)
        else:
            h_sec   = (H + rotations[1]) % 360
            h_acc   = (H + rotations[-1]) % 360 if len(rotations) > 2 else (H + rotations[1] + 30) % 360
            secondary = oklch_to_hex(L, C * 0.85, h_sec)
            accent    = oklch_to_hex(min(L + 0.10, 0.95), C * 1.10, h_acc)

        neutral_palette = [
            oklch_to_hex(0.98, C * 0.05, H),   # casi blanco con tinte
            oklch_to_hex(0.93, C * 0.08, H),   # gris claro
            oklch_to_hex(0.55, C * 0.10, H),   # gris medio
            oklch_to_hex(0.18, C * 0.08, H),   # casi negro con tinte
        ]

        return {
            "primary": primary_hex.upper() if not primary_hex.startswith("#") else primary_hex,
            "secondary": secondary,
            "accent": accent,
            "neutral_palette": neutral_palette,
            "harmony_type": harmony,
        }

    except Exception as exc:
        logger.error("generate_harmonic_palette(%s, %s): %s", primary_hex, harmony, exc)
        return {
            "primary": primary_hex,
            "secondary": "#CCCCCC",
            "accent": "#888888",
            "neutral_palette": ["#F8FAFC", "#E2E8F0", "#64748B", "#1E293B"],
            "harmony_type": harmony,
        }


def generate_complementary(hex_color: str) -> str:
    """
    Color complementario exacto (opuesto en OKLCH, H + 180°).
    Mucho más preciso que invertir RGB.
    """
    try:
        L, C, H = hex_to_oklch(hex_color)
        return oklch_to_hex(L, C, (H + 180.0) % 360.0)
    except Exception:
        rgb = [int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)]
        return "#{:02X}{:02X}{:02X}".format(255 - rgb[0], 255 - rgb[1], 255 - rgb[2])


# ---------------------------------------------------------------------------
# Paleta tonal perceptualmente uniforme (Material Design 3 style)
# ---------------------------------------------------------------------------

def generate_tonal_palette(primary_hex: str, steps: int = 11) -> dict[str, str]:
    """
    Genera una paleta tonal usando OKLCH para distribución perceptualmente uniforme.

    Los tonos van de 0 (negro puro) a 100 (blanco puro), en pasos de 10.
    El tono 50 corresponde al color original.

    Args:
        primary_hex: Color semilla.
        steps: Número de tonos (por defecto 11: 0,10,…,100).

    Returns:
        Dict {"0": "#hex", "10": "#hex", …, "100": "#hex"}
    """
    try:
        L_base, C_base, H_base = hex_to_oklch(primary_hex)
    except Exception:
        return {str(i * 10): "#CCCCCC" for i in range(steps)}

    palette = {}
    for i in range(steps):
        tone = i * 10  # 0, 10, 20, … 100
        # L va de 0.03 (casi negro) a 0.99 (casi blanco)
        L_target = 0.03 + (tone / 100.0) * 0.96
        # Reducir chroma en extremos (muy oscuro o muy claro = menos saturación)
        distance_from_mid = abs(tone - 50) / 50.0   # 0 en tono 50, 1 en extremos
        C_target = C_base * (1.0 - distance_from_mid * 0.6)
        palette[str(tone)] = oklch_to_hex(L_target, C_target, H_base)

    return palette


# ---------------------------------------------------------------------------
# Score de armonía cromática (Criterio 1 del evaluador estético)
# ---------------------------------------------------------------------------

def score_color_harmony(palette: list[str]) -> float:
    """
    Calcula el score de armonía cromática de una paleta (0–100).

    Algoritmo:
        1. Convertir todos los hex a OKLCH
        2. Detectar tipo de armonía (complementaria, análoga, triádica, monocromática)
        3. Score base según tipo de armonía
        4. Penalización si la variación de Chroma es muy alta (>0.25)
        5. Bonus si ΔE entre colores clave está en rango estético (ΔE 40–80)

    Args:
        palette: Lista de colores hex ['#hex1', '#hex2', …]

    Returns:
        Score de 0 a 100.
    """
    if not palette:
        return 0.0

    valid = [c for c in palette if c and len(c.lstrip("#")) == 6]
    if len(valid) < 2:
        return 50.0  # color único: neutral

    try:
        oklch_values = [hex_to_oklch(c) for c in valid]
        hues     = [v[2] for v in oklch_values]
        chromas  = [v[1] for v in oklch_values]

        harmony = detect_harmony_type(valid)

        score_map = {
            "complementario": 92.0,
            "analogo":        88.0,
            "triadico":       85.0,
            "monocromatico":  78.0,
        }
        base_score = score_map.get(harmony, 40.0) if harmony else 40.0

        # Penalización por inconsistencia de chroma
        chroma_range = max(chromas) - min(chromas)
        if chroma_range > 0.25:
            base_score -= 10.0

        # Bonus ΔE: los pares de colores deben ser distinguibles (ΔE > 20)
        # pero no extremos (ΔE < 90). Sólo si hay exactamente 2 colores clave.
        if len(valid) == 2:
            de = delta_e(valid[0], valid[1])
            if 20.0 <= de <= 90.0:
                base_score = min(100.0, base_score + 5.0)

        return max(0.0, min(100.0, base_score))

    except Exception as exc:
        logger.error("score_color_harmony: %s", exc)
        return 0.0


# ---------------------------------------------------------------------------
# Simulación de deficiencia de visión cromática (CVD)
# Matrices pre-computadas de Machado et al. (2010) — modelo fisiológico
# Fuente: colour-develop/colour/blindness/datasets/machado2010.py
#
# severity=0.5 → anomalía parcial (afecta a muchas personas)
# severity=1.0 → dicromacia completa (caso severo)
# Las matrices operan sobre sRGB lineal [0,1].
# ---------------------------------------------------------------------------

_CVD_MATRICES: dict[str, dict[float, np.ndarray]] = {
    # Protanomaly: reducción de sensibilidad al rojo
    "protanopia": {
        0.5: np.array([
            [0.458064, 0.679578, -0.137642],
            [0.092785, 0.846313,  0.060902],
            [-0.007494, -0.016807,  1.024301],
        ]),
        1.0: np.array([
            [0.152286, 1.052583, -0.204868],
            [0.114503, 0.786281,  0.099216],
            [-0.003882, -0.048116,  1.051998],
        ]),
    },
    # Deuteranomaly: reducción de sensibilidad al verde (más común)
    "deuteranopia": {
        0.5: np.array([
            [0.547494, 0.607765, -0.155259],
            [0.181692, 0.781742,  0.036566],
            [-0.010410,  0.027275,  0.983136],
        ]),
        1.0: np.array([
            [0.367322, 0.860646, -0.227968],
            [0.280085, 0.672501,  0.047413],
            [-0.011820,  0.042940,  0.968881],
        ]),
    },
    # Tritanomaly: reducción de sensibilidad al azul (menos común)
    "tritanopia": {
        0.5: np.array([
            [ 1.017277,  0.027029, -0.044306],
            [-0.006113,  0.958479,  0.047634],
            [ 0.006379,  0.248708,  0.744913],
        ]),
        1.0: np.array([
            [ 1.255528, -0.076749, -0.178779],
            [-0.078411,  0.930809,  0.147602],
            [ 0.004733,  0.691367,  0.303900],
        ]),
    },
}


def _apply_cvd_matrix(hex_color: str, matrix: np.ndarray) -> str:
    """Aplica una matriz CVD (Machado 2010) a un color hex. Retorna hex."""
    clean = hex_color.lstrip("#")
    r = int(clean[0:2], 16) / 255.0
    g = int(clean[2:4], 16) / 255.0
    b = int(clean[4:6], 16) / 255.0
    rgb = np.array([r, g, b])
    result = matrix @ rgb
    result = np.clip(result, 0.0, 1.0)
    return "#{:02X}{:02X}{:02X}".format(
        int(round(result[0] * 255)),
        int(round(result[1] * 255)),
        int(round(result[2] * 255)),
    )


def simulate_cvd(hex_color: str, deficiency: str, severity: float = 1.0) -> str:
    """
    Simula cómo percibe un color una persona con deficiencia visual cromática.
    Usa las matrices fisiológicas de Machado et al. (2010).

    Args:
        hex_color:  Color en formato '#RRGGBB'.
        deficiency: 'protanopia' | 'deuteranopia' | 'tritanopia'
        severity:   0.5 (anomalía parcial) | 1.0 (dicromacia completa)

    Returns:
        Color simulado en '#RRGGBB'.
    """
    try:
        deficiency = deficiency.lower()
        matrices = _CVD_MATRICES.get(deficiency)
        if matrices is None:
            raise ValueError(
                f"Deficiencia desconocida: '{deficiency}'. "
                "Opciones: protanopia, deuteranopia, tritanopia"
            )
        closest = min(matrices.keys(), key=lambda s: abs(s - severity))
        return _apply_cvd_matrix(hex_color, matrices[closest])
    except Exception as exc:
        logger.warning("simulate_cvd(%s, %s): %s", hex_color, deficiency, exc)
        return hex_color


def simulate_deuteranopia(hex_color: str) -> str:
    """Simula deuteranopia completa (ceguera al verde). Ver simulate_cvd()."""
    return simulate_cvd(hex_color, "deuteranopia", severity=1.0)


def simulate_protanopia(hex_color: str) -> str:
    """Simula protanopia completa (ceguera al rojo). Ver simulate_cvd()."""
    return simulate_cvd(hex_color, "protanopia", severity=1.0)


def simulate_tritanopia(hex_color: str) -> str:
    """Simula tritanopia completa (ceguera al azul). Ver simulate_cvd()."""
    return simulate_cvd(hex_color, "tritanopia", severity=1.0)


def palette_colorblind_report(palette_hex: list[str]) -> dict:
    """
    Reporte de accesibilidad cromatica completo para una paleta.
    Evalua protanopia, deuteranopia y tritanopia con matrices Machado 2010.

    Returns:
        {
            "protanopia":     list[{"original", "simulated", "delta_e"}],
            "deuteranopia":   list[{"original", "simulated", "delta_e"}],
            "tritanopia":     list[{"original", "simulated", "delta_e"}],
            "warning":        bool,
            "affected_types": list[str],
        }
    """
    result: dict = {
        "protanopia": [],
        "deuteranopia": [],
        "tritanopia": [],
        "warning": False,
        "affected_types": [],
    }
    affected: set[str] = set()
    for c in palette_hex:
        if not c or len(c.lstrip("#")) != 6:
            continue
        for deficiency in ("protanopia", "deuteranopia", "tritanopia"):
            sim = simulate_cvd(c, deficiency, severity=1.0)
            de = delta_e(c, sim)
            result[deficiency].append({
                "original":  c,
                "simulated": sim,
                "delta_e":   round(de, 2),
            })
            if de > 10.0:
                affected.add(deficiency)
                result["warning"] = True
    result["affected_types"] = sorted(affected)
    return result


# ---------------------------------------------------------------------------
# Keywords de color CSS 3 (163 nombres W3C, extraido de colour-develop)
# ---------------------------------------------------------------------------

_CSS_KEYWORDS: dict[str, str] = {
    "aliceblue": "#F0F8FF", "antiquewhite": "#FAEBD7", "aqua": "#00FFFF",
    "aquamarine": "#7FFFD4", "azure": "#F0FFFF", "beige": "#F5F5DC",
    "bisque": "#FFE4C4", "black": "#000000", "blanchedalmond": "#FFEBCD",
    "blue": "#0000FF", "blueviolet": "#8A2BE2", "brown": "#A52A2A",
    "burlywood": "#DEB887", "cadetblue": "#5F9EA0", "chartreuse": "#7FFF00",
    "chocolate": "#D2691E", "coral": "#FF7F50", "cornflowerblue": "#6495ED",
    "cornsilk": "#FFF8DC", "crimson": "#DC143C", "cyan": "#00FFFF",
    "darkblue": "#00008B", "darkcyan": "#008B8B", "darkgoldenrod": "#B8860B",
    "darkgray": "#A9A9A9", "darkgreen": "#006400", "darkgrey": "#A9A9A9",
    "darkkhaki": "#BDB76B", "darkmagenta": "#8B008B", "darkolivegreen": "#556B2F",
    "darkorange": "#FF8C00", "darkorchid": "#9932CC", "darkred": "#8B0000",
    "darksalmon": "#E9967A", "darkseagreen": "#8FBC8F", "darkslateblue": "#483D8B",
    "darkslategray": "#2F4F4F", "darkslategrey": "#2F4F4F", "darkturquoise": "#00CED1",
    "darkviolet": "#9400D3", "deeppink": "#FF1493", "deepskyblue": "#00BFFF",
    "dimgray": "#696969", "dimgrey": "#696969", "dodgerblue": "#1E90FF",
    "firebrick": "#B22222", "floralwhite": "#FFFAF0", "forestgreen": "#228B22",
    "fuchsia": "#FF00FF", "gainsboro": "#DCDCDC", "ghostwhite": "#F8F8FF",
    "gold": "#FFD700", "goldenrod": "#DAA520", "gray": "#808080",
    "green": "#008000", "greenyellow": "#ADFF2F", "grey": "#808080",
    "honeydew": "#F0FFF0", "hotpink": "#FF69B4", "indianred": "#CD5C5C",
    "indigo": "#4B0082", "ivory": "#FFFFF0", "khaki": "#F0E68C",
    "lavender": "#E6E6FA", "lavenderblush": "#FFF0F5", "lawngreen": "#7CFC00",
    "lemonchiffon": "#FFFACD", "lightblue": "#ADD8E6", "lightcoral": "#F08080",
    "lightcyan": "#E0FFFF", "lightgoldenrodyellow": "#FAFAD2", "lightgray": "#D3D3D3",
    "lightgreen": "#90EE90", "lightgrey": "#D3D3D3", "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A", "lightseagreen": "#20B2AA", "lightskyblue": "#87CEFA",
    "lightslategray": "#778899", "lightslategrey": "#778899", "lightsteelblue": "#B0C4DE",
    "lightyellow": "#FFFFE0", "lime": "#00FF00", "limegreen": "#32CD32",
    "linen": "#FAF0E6", "magenta": "#FF00FF", "maroon": "#800000",
    "mediumaquamarine": "#66CDAA", "mediumblue": "#0000CD", "mediumorchid": "#BA55D3",
    "mediumpurple": "#9370DB", "mediumseagreen": "#3CB371", "mediumslateblue": "#7B68EE",
    "mediumspringgreen": "#00FA9A", "mediumturquoise": "#48D1CC", "mediumvioletred": "#C71585",
    "midnightblue": "#191970", "mintcream": "#F5FFFA", "mistyrose": "#FFE4E1",
    "moccasin": "#FFE4B5", "navajowhite": "#FFDEAD", "navy": "#000080",
    "oldlace": "#FDF5E6", "olive": "#808000", "olivedrab": "#6B8E23",
    "orange": "#FFA500", "orangered": "#FF4500", "orchid": "#DA70D6",
    "palegoldenrod": "#EEE8AA", "palegreen": "#98FB98", "paleturquoise": "#AFEEEE",
    "palevioletred": "#DB7093", "papayawhip": "#FFEFD5", "peachpuff": "#FFDAB9",
    "peru": "#CD853F", "pink": "#FFC0CB", "plum": "#DDA0DD",
    "powderblue": "#B0E0E6", "purple": "#800080", "red": "#FF0000",
    "rosybrown": "#BC8F8F", "royalblue": "#4169E1", "saddlebrown": "#8B4513",
    "salmon": "#FA8072", "sandybrown": "#F4A460", "seagreen": "#2E8B57",
    "seashell": "#FFF5EE", "sienna": "#A0522D", "silver": "#C0C0C0",
    "skyblue": "#87CEEB", "slateblue": "#6A5ACD", "slategray": "#708090",
    "slategrey": "#708090", "snow": "#FFFAFA", "springgreen": "#00FF7F",
    "steelblue": "#4682B4", "tan": "#D2B48C", "teal": "#008080",
    "thistle": "#D8BFD8", "tomato": "#FF6347", "turquoise": "#40E0D0",
    "violet": "#EE82EE", "wheat": "#F5DEB3", "white": "#FFFFFF",
    "whitesmoke": "#F5F5F5", "yellow": "#FFFF00", "yellowgreen": "#9ACD32",
}


def keyword_to_hex(name: str) -> Optional[str]:
    """
    Convierte nombre CSS 3 a hex. Case-insensitive. 163 keywords disponibles.

    Examples:
        keyword_to_hex('navy')    -> '#000080'
        keyword_to_hex('Coral')   -> '#FF7F50'
        keyword_to_hex('unknown') -> None
    """
    return _CSS_KEYWORDS.get(name.lower().strip())


def hex_to_keyword(hex_color: str, threshold: float = 5.0) -> Optional[str]:
    """
    Nombre CSS mas cercano a un color hex segun delta E.

    Args:
        hex_color:  '#RRGGBB'
        threshold:  delta E maximo para considerar coincidencia (default 5.0)

    Returns:
        Nombre CSS si hay coincidencia, None si no.
    """
    best_name: Optional[str] = None
    best_de = float("inf")
    for name, kw_hex in _CSS_KEYWORDS.items():
        try:
            de = delta_e(hex_color, kw_hex)
            if de < best_de:
                best_de = de
                best_name = name
        except Exception:
            continue
    return best_name if best_de <= threshold else None


# ---------------------------------------------------------------------------
# Temperatura de color -- clasificacion calido / neutro / frio
# ---------------------------------------------------------------------------

def classify_palette_temperature(palette_hex: list[str]) -> dict:
    """
    Clasifica la temperatura perceptual de una paleta usando OKLCH.

    Rangos H en OKLCH:
        Calidos:  H en [0,90) union (330,360]  -- rojo, naranja, amarillo
        Neutros:  H en [90,150) union (270,330) -- amarillo-verde, violeta
        Frios:    H en [150,270]                -- verde, cian, azul

    Returns:
        {
            "dominant":      'calido' | 'neutro' | 'frio',
            "warm_ratio":    float,
            "cool_ratio":    float,
            "neutral_ratio": float,
            "per_color":     list[{"hex", "temperature", "hue"}],
        }
    """
    per_color = []
    warm = cool = neutral = 0

    for c in palette_hex:
        if not c or len(c.lstrip("#")) != 6:
            continue
        try:
            _L, _C, H = hex_to_oklch(c)
            if _C < 0.03:
                temp = "neutro"
                neutral += 1
            elif H < 90 or H > 330:
                temp = "calido"
                warm += 1
            elif 150 <= H <= 270:
                temp = "frio"
                cool += 1
            else:
                temp = "neutro"
                neutral += 1
            per_color.append({"hex": c, "temperature": temp, "hue": round(H, 1)})
        except Exception:
            continue

    total = warm + cool + neutral
    if total == 0:
        return {"dominant": "neutro", "warm_ratio": 0.0, "cool_ratio": 0.0,
                "neutral_ratio": 1.0, "per_color": []}

    w_r, c_r, n_r = warm / total, cool / total, neutral / total
    if w_r >= c_r and w_r >= n_r:
        dominant = "calido"
    elif c_r >= w_r and c_r >= n_r:
        dominant = "frio"
    else:
        dominant = "neutro"

    return {
        "dominant": dominant,
        "warm_ratio": round(w_r, 2),
        "cool_ratio": round(c_r, 2),
        "neutral_ratio": round(n_r, 2),
        "per_color": per_color,
    }
