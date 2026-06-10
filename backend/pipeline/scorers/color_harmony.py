"""
color_harmony.py — Criterio 1: Armonía Cromática
=================================================
Scorer algorítmico y determinista para evaluar la armonía de una paleta.
Dado el mismo input, siempre produce el mismo output.

Delega toda la matemática a services/colour_engine.py que usa OKLCH
(espacio perceptualmente uniforme, mucho más preciso que HSL).

Tipos de armonía soportados:
    complementario  — ~180° (tolerancia 40°)
    analogo         — ~30°  (tolerancia 25°)
    triadico        — ~120° (tolerancia 20°)
    monocromatico   — ~0°   (tolerancia 30°)
"""

import logging
from typing import Optional

from services.colour_engine import (
    detect_harmony_type,
    score_color_harmony,
    delta_e,
)

logger = logging.getLogger(__name__)


def score_wcag_contrast_oklch(palette: list[str]) -> float:
    """
    Bonus scorer: penaliza paletas donde los colores son difícilmente distinguibles.
    Complementa el scorer WCAG numérico con percepción real en OKLCH.

    Returns:
        Score 0–100
    """
    if len(palette) < 2:
        return 100.0

    min_de = float("inf")
    for i in range(len(palette)):
        for j in range(i + 1, len(palette)):
            try:
                de = delta_e(palette[i], palette[j])
                min_de = min(min_de, de)
            except Exception:
                pass

    if min_de == float("inf"):
        return 50.0
    # ΔE mínimo deseable entre dos colores: ~30 para paletas UI
    return min(100.0, (min_de / 30.0) * 100.0)


def analyze_palette(palette_hex: list[str]) -> dict:
    """
    Análisis completo de una paleta: armonía, scores, y diagnóstico para el LLM.

    Args:
        palette_hex: lista de hex colors de la paleta a evaluar.

    Returns:
        {
            "harmony_type": str | None,
            "harmony_score": float,             # 0–100, Criterio 1
            "distinguishability_score": float,  # 0–100
            "combined_score": float,            # promedio ponderado
            "diagnosis": str,                   # texto para el loop de corrección
        }
    """
    harmony_type = detect_harmony_type(palette_hex)
    h_score = score_color_harmony(palette_hex)
    d_score = score_wcag_contrast_oklch(palette_hex)

    # Peso: armonía 60%, distinguibilidad 40%
    combined = h_score * 0.6 + d_score * 0.4

    diagnosis_parts = []
    if harmony_type:
        diagnosis_parts.append(
            f"Armonía detectada: {harmony_type} (score {h_score:.0f}/100)."
        )
    else:
        diagnosis_parts.append(
            "No se detectó armonía cromática clara. "
            "Considera usar colores complementarios, análogos o triádicos."
        )
    if d_score < 50:
        diagnosis_parts.append(
            "Los colores son difícilmente distinguibles entre sí (ΔE mínimo bajo). "
            "Aumenta el contraste entre colores de la paleta."
        )

    return {
        "harmony_type": harmony_type,
        "harmony_score": round(h_score, 1),
        "distinguishability_score": round(d_score, 1),
        "combined_score": round(combined, 1),
        "diagnosis": " ".join(diagnosis_parts),
    }
