"""
color_science.py -- Análisis científico de colores para diseño
==============================================================
Valida WCAG contrast, genera paletas armónicas, implementa Material Design 3.

Las operaciones de generación cromática (complementario, paleta tonal) delegan
a services/colour_engine.py que usa OKLCH perceptualmente uniforme.
Las validaciones WCAG 2.1 se calculan localmente (sin dependencias externas).
"""

import logging
import re
from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass

from services.colour_engine import (
    generate_complementary as _oklch_complementary,
    generate_tonal_palette as _oklch_tonal_palette,
    generate_harmonic_palette as _oklch_harmonic_palette,
    detect_harmony_type,
    palette_colorblind_report,
    score_color_harmony,
    delta_e,
    simulate_cvd,
    simulate_tritanopia,
    keyword_to_hex,
    hex_to_keyword,
    classify_palette_temperature,
)

logger = logging.getLogger(__name__)


@dataclass
class ColorInfo:
    """Información sobre un color."""
    hex: str
    rgb: Tuple[int, int, int]
    name: str


class ColorScience:
    """Análisis científico de colores para UI design."""
    
    # Material Design 3 Semantic colors (defaults)
    MD3_DEFAULTS = {
        "primary": "#6750a4",
        "on-primary": "#ffffff",
        "primary-container": "#eaddff",
        "on-primary-container": "#21005e",
        "secondary": "#625b71",
        "on-secondary": "#ffffff",
        "tertiary": "#7d5260",
        "on-tertiary": "#ffffff",
        "error": "#b3261e",
        "on-error": "#ffffff",
        "background": "#fffbfe",
        "on-background": "#1c1b1f",
        "surface": "#fffbfe",
        "on-surface": "#1c1b1f",
        "surface-dim": "#ded8e1",
        "surface-bright": "#fffbfe",
        "surface-container-lowest": "#ffffff",
        "surface-container-low": "#f7f2fa",
        "surface-container": "#f3edf7",
        "surface-container-high": "#ede9f3",
        "surface-container-highest": "#e8e4ed",
    }
    
    def __init__(self):
        self._color_cache: Dict[str, ColorInfo] = {}
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Optional[Tuple[int, int, int]]:
        """Convierte hex a RGB."""
        hex_color = hex_color.strip()
        if not hex_color.startswith('#'):
            hex_color = '#' + hex_color
        
        hex_color = hex_color[1:]
        if len(hex_color) == 6:
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
            except ValueError:
                return None
        return None
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convierte RGB a hex."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    @staticmethod
    def relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calcula luminancia relativa (WCAG 2.1)."""
        r, g, b = [x / 255.0 for x in rgb]
        
        def adjust(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4
        
        r = adjust(r)
        g = adjust(g)
        b = adjust(b)
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def wcag_contrast_ratio(self, hex1: str, hex2: str) -> Optional[float]:
        """
        Calcula el ratio de contraste WCAG 2.1.
        
        Retorna:
            float: Ratio 1:1 (low) a 21:1 (high)
            None: si los colores no son válidos
        
        Niveles:
            < 4.5:1   → FAIL
            4.5:1     → AA (texto normal)
            7:1       → AAA (texto normal)
            3:1       → AA (texto grande 18px+)
        """
        rgb1 = self.hex_to_rgb(hex1)
        rgb2 = self.hex_to_rgb(hex2)
        
        if not rgb1 or not rgb2:
            return None
        
        l1 = self.relative_luminance(rgb1)
        l2 = self.relative_luminance(rgb2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def validate_wcag_aa(self, text_color: str, bg_color: str, is_large: bool = False) -> Tuple[bool, float]:
        """
        Valida que text_color sobre bg_color cumple WCAG AA.
        
        Args:
            text_color: Color del texto (hex)
            bg_color: Color del fondo (hex)
            is_large: True si texto >= 18px (requiere 3:1), False si normal (requiere 4.5:1)
        
        Returns:
            (is_valid, ratio)
        """
        ratio = self.wcag_contrast_ratio(text_color, bg_color)
        if ratio is None:
            return (False, 0.0)
        
        min_ratio = 3.0 if is_large else 4.5
        return (ratio >= min_ratio, ratio)
    
    def validate_wcag_aaa(self, text_color: str, bg_color: str) -> Tuple[bool, float]:
        """Valida WCAG AAA (7:1)."""
        ratio = self.wcag_contrast_ratio(text_color, bg_color)
        if ratio is None:
            return (False, 0.0)
        return (ratio >= 7.0, ratio)
    
    def generate_complementary(self, hex_color: str) -> str:
        """
        Genera color complementario exacto usando OKLCH (H + 180°).
        Perceptualmente más preciso que invertir RGB.
        """
        try:
            return _oklch_complementary(hex_color)
        except Exception:
            # fallback RGB por si el color es inválido
            rgb = self.hex_to_rgb(hex_color)
            if not rgb:
                return "#cccccc"
            r, g, b = rgb
            return self.rgb_to_hex((255 - r, 255 - g, 255 - b))
    
    def lighten(self, hex_color: str, amount: float = 0.1) -> str:
        """
        Aclara un color un porcentaje.
        
        Args:
            hex_color: Color original
            amount: Cantidad de aclarado (0.0-1.0)
        """
        rgb = self.hex_to_rgb(hex_color)
        if not rgb:
            return hex_color
        
        r, g, b = rgb
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        
        return self.rgb_to_hex((r, g, b))
    
    def darken(self, hex_color: str, amount: float = 0.1) -> str:
        """
        Oscurece un color un porcentaje.
        
        Args:
            hex_color: Color original
            amount: Cantidad de oscurecimiento (0.0-1.0)
        """
        rgb = self.hex_to_rgb(hex_color)
        if not rgb:
            return hex_color
        
        r, g, b = rgb
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        
        return self.rgb_to_hex((r, g, b))
    
    def generate_tonal_palette(self, primary: str) -> Dict[str, str]:
        """
        Genera paleta tonal con distribución perceptualmente uniforme (OKLCH).
        Material Design 3 style: 11 tonos del 0 (negro) al 100 (blanco).
        """
        try:
            return _oklch_tonal_palette(primary)
        except Exception:
            # fallback simple en RGB
            palette = {}
            base_rgb = self.hex_to_rgb(primary)
            if not base_rgb:
                return {str(i * 10): "#cccccc" for i in range(11)}
            for i in range(11):
                tone = i * 10
                if tone < 50:
                    palette[str(tone)] = self.darken(primary, (50 - tone) / 50 * 0.8)
                elif tone == 50:
                    palette[str(tone)] = primary
                else:
                    palette[str(tone)] = self.lighten(primary, (tone - 50) / 50 * 0.8)
            return palette

    def generate_harmonic_palette(self, primary: str, harmony: str = "complementario") -> Dict:
        """
        Genera paleta armónica completa usando OKLCH.

        Args:
            primary: Color primario en hex.
            harmony: 'complementario' | 'analogo' | 'triadico' | 'monocromatico'

        Returns:
            {"primary", "secondary", "accent", "neutral_palette", "harmony_type"}
        """
        return _oklch_harmonic_palette(primary, harmony)

    def analyze_palette(self, palette: List[str]) -> Dict:
        """
        Análisis de armonía y accesibilidad para daltonismo de una paleta completa.

        Returns:
            {
                "harmony_type": str,
                "harmony_score": float,
                "colorblind_report": dict,
            }
        """
        return {
            "harmony_type": detect_harmony_type(palette),
            "harmony_score": round(score_color_harmony(palette), 1),
            "colorblind_report": palette_colorblind_report(palette),
        }
    
    def extract_colors_from_markdown(self, markdown: str) -> Dict[str, str]:
        """
        Extrae colores hex del markdown body de DESIGN.md.
        
        Returns:
            Dict de {nombre: hex_color}
        """
        colors = {}
        
        # Buscar patrón: **ColorName** {colors.token} o #RRGGBB
        pattern = r'\*\*([^*]+)\*\*\s*(?:\{[^}]+\})?\s*([#a-fA-F0-9]{6})'
        matches = re.finditer(pattern, markdown)
        
        for match in matches:
            name = match.group(1).strip()
            hex_color = match.group(2)
            colors[name] = hex_color
        
        # También buscar solo hex colors
        hex_pattern = r'([#a-fA-F0-9]{6})\b'
        for match in re.finditer(hex_pattern, markdown):
            hex_color = match.group(1)
            colors[f"color-{hex_color}"] = hex_color
        
        return colors
    
    def validate_palette_accessibility(
        self,
        primary: str,
        text_on_primary: str,
        surface: str,
        text_on_surface: str
    ) -> Dict[str, Any]:
        """
        Valida que una paleta completa cumpla WCAG AA.
        
        Returns:
            Dict con validaciones y recomendaciones
        """
        result = {
            "primary_contrast": {
                "valid": False,
                "ratio": 0.0,
                "level": "FAIL"
            },
            "surface_contrast": {
                "valid": False,
                "ratio": 0.0,
                "level": "FAIL"
            },
            "recommendations": []
        }
        
        # Validar primary
        is_valid, ratio = self.validate_wcag_aa(text_on_primary, primary)
        result["primary_contrast"]["valid"] = is_valid
        result["primary_contrast"]["ratio"] = round(ratio, 2)
        if ratio >= 7:
            result["primary_contrast"]["level"] = "AAA"
        elif ratio >= 4.5:
            result["primary_contrast"]["level"] = "AA"
        else:
            result["primary_contrast"]["level"] = "FAIL"
            result["recommendations"].append(
                f"Text on primary has poor contrast ({ratio:.1f}:1). Try lighter text or darker primary."
            )
        
        # Validar surface
        is_valid, ratio = self.validate_wcag_aa(text_on_surface, surface)
        result["surface_contrast"]["valid"] = is_valid
        result["surface_contrast"]["ratio"] = round(ratio, 2)
        if ratio >= 7:
            result["surface_contrast"]["level"] = "AAA"
        elif ratio >= 4.5:
            result["surface_contrast"]["level"] = "AA"
        else:
            result["surface_contrast"]["level"] = "FAIL"
            result["recommendations"].append(
                f"Text on surface has poor contrast ({ratio:.1f}:1). Try darker text or lighter surface."
            )
        
        return result

    def simulate_cvd(self, hex_color: str, deficiency: str, severity: float = 1.0) -> str:
        """Simula CVD con matrices Machado 2010. deficiency: protanopia|deuteranopia|tritanopia. severity: 0.5|1.0"""
        return simulate_cvd(hex_color, deficiency, severity)

    def colorblind_report(self, palette: List[str]) -> Dict:
        """Reporte completo CVD (protanopia, deuteranopia, tritanopia) con matrices Machado 2010."""
        return palette_colorblind_report(palette)

    def palette_temperature(self, palette: List[str]) -> Dict:
        """Clasifica temperatura perceptual de la paleta: calido / neutro / frio."""
        return classify_palette_temperature(palette)

    @staticmethod
    def color_name(hex_color: str, threshold: float = 5.0) -> Optional[str]:
        """Nombre CSS mas cercano a un color hex (delta E <= threshold). None si no hay coincidencia."""
        return hex_to_keyword(hex_color, threshold)

    @staticmethod
    def name_to_hex(name: str) -> Optional[str]:
        """Convierte nombre CSS a hex. 'navy' -> '#000080'. Case-insensitive."""
        return keyword_to_hex(name)


# Singleton
_color_science_instance: Optional[ColorScience] = None

def get_color_science() -> ColorScience:
    """Obtiene instancia singleton."""
    global _color_science_instance
    if _color_science_instance is None:
        _color_science_instance = ColorScience()
    return _color_science_instance
