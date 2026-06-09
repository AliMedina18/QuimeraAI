"""
typography_analyzer.py -- Análisis y recomendación de tipografía sistemática
=============================================================================
Recomienda pairings, jerarquías y escalas responsive de tipografía.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class TypographyAnalyzer:
    """Análisis y recomendación de tipografía sistemática."""
    
    # Pairings de tipografía probados (Serif + Sans-Serif, o Sans + Sans)
    PROVEN_PAIRINGS = {
        # Moderna & Profesional
        "inter-plus-jakarta": {
            "headline": {"font": "Plus Jakarta Sans", "weight": 700, "size": 32},
            "display": {"font": "Plus Jakarta Sans", "weight": 600, "size": 24},
            "body": {"font": "Inter", "weight": 400, "size": 16},
            "caption": {"font": "Inter", "weight": 400, "size": 12},
            "description": "Friendly + reliable (Airbnb, Paw & Paths style)"
        },
        
        # Premium & Editorial
        "crimson-plus-inter": {
            "headline": {"font": "Crimson Text", "weight": 600, "size": 36},
            "display": {"font": "Crimson Text", "weight": 400, "size": 24},
            "body": {"font": "Inter", "weight": 400, "size": 16},
            "caption": {"font": "Inter", "weight": 400, "size": 12},
            "description": "Editorial + clarity (Premium, sophisticated)"
        },
        
        # Tech & Modern
        "mono-plus-inter": {
            "headline": {"font": "Space Grotesk", "weight": 700, "size": 32},
            "display": {"font": "Space Grotesk", "weight": 600, "size": 24},
            "body": {"font": "Inter", "weight": 400, "size": 16},
            "caption": {"font": "JetBrains Mono", "weight": 400, "size": 11},
            "description": "Geometric + technical (Developer-friendly)"
        },
        
        # Minimal & Clean
        "system-ui": {
            "headline": {"font": "system-ui", "weight": 700, "size": 28},
            "display": {"font": "system-ui", "weight": 600, "size": 20},
            "body": {"font": "system-ui", "weight": 400, "size": 15},
            "caption": {"font": "system-ui", "weight": 400, "size": 12},
            "description": "Minimalist system fonts (Fast, accessible)"
        },
        
        # Bold & Creative
        "poppins-plus-lato": {
            "headline": {"font": "Poppins", "weight": 800, "size": 36},
            "display": {"font": "Poppins", "weight": 700, "size": 28},
            "body": {"font": "Lato", "weight": 400, "size": 16},
            "caption": {"font": "Lato", "weight": 400, "size": 12},
            "description": "Bold + friendly (Creative, energetic)"
        },
        
        # Corporate & Formal
        "roboto-slab-plus-roboto": {
            "headline": {"font": "Roboto Slab", "weight": 700, "size": 32},
            "display": {"font": "Roboto Slab", "weight": 600, "size": 24},
            "body": {"font": "Roboto", "weight": 400, "size": 16},
            "caption": {"font": "Roboto", "weight": 400, "size": 12},
            "description": "Formal + readable (Enterprise, corporate)"
        },
    }
    
    # Escalas responsive (móvil -> tablet -> desktop)
    RESPONSIVE_SCALES = {
        "headline": {
            "mobile": 28,
            "tablet": 32,
            "desktop": 36
        },
        "display": {
            "mobile": 20,
            "tablet": 24,
            "desktop": 28
        },
        "body": {
            "mobile": 14,
            "tablet": 15,
            "desktop": 16
        },
        "caption": {
            "mobile": 11,
            "tablet": 11,
            "desktop": 12
        }
    }
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def recommend_pairing(self, industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Recomienda un pairing de tipografía basado en industria.
        
        Args:
            industry: "fintech", "saas", "marketplace", "design", etc.
        
        Returns:
            Diccionario con recomendación completa
        """
        industry_to_pairing = {
            "fintech": "inter-plus-jakarta",      # Profesional + amigable
            "saas": "mono-plus-inter",            # Tech + clara
            "marketplace": "inter-plus-jakarta",  # Amigable + confiable
            "design": "crimson-plus-inter",       # Editorial + sofisticada
            "commerce": "poppins-plus-lato",      # Bold + atractivo
            "corporate": "roboto-slab-plus-roboto",  # Formal
            "creative": "poppins-plus-lato",      # Bold
            "tech": "mono-plus-inter",            # Geométrica
            "startup": "inter-plus-jakarta",      # Moderna
        }
        
        # Seleccionar pairing
        pairing_key = industry_to_pairing.get(industry.lower() if industry else "fintech", "inter-plus-jakarta")
        
        if pairing_key not in self.PROVEN_PAIRINGS:
            pairing_key = "inter-plus-jakarta"  # Default
        
        pairing = self.PROVEN_PAIRINGS[pairing_key]
        
        return {
            "pairing": pairing_key,
            "description": pairing.get("description"),
            "headline": pairing.get("headline"),
            "display": pairing.get("display"),
            "body": pairing.get("body"),
            "caption": pairing.get("caption"),
        }
    
    def generate_hierarchy(self, pairing_key: str) -> Dict[str, Dict]:
        """
        Genera jerarquía tipográfica completa basada en pairing.
        
        Returns:
            Diccionario con niveles: headline-xl, headline-lg, body-md, etc.
        """
        if pairing_key not in self.PROVEN_PAIRINGS:
            pairing_key = "inter-plus-jakarta"
        
        base = self.PROVEN_PAIRINGS[pairing_key]
        hierarchy = {}
        
        # Headline sizes: XL, LG, MD
        for level, factor in [("xl", 1.5), ("lg", 1.25), ("md", 1.0)]:
            props = base["headline"].copy()
            props["size"] = int(props["size"] * factor)
            hierarchy[f"headline-{level}"] = props
        
        # Display
        hierarchy["display"] = base["display"]
        
        # Body variants
        for weight in [400, 500, 600]:
            props = base["body"].copy()
            props["weight"] = weight
            hierarchy[f"body-md-w{weight}"] = props
        
        # Caption
        hierarchy["caption"] = base["caption"]
        
        # Label
        label_props = base["body"].copy()
        label_props["size"] = 12
        label_props["weight"] = 600
        hierarchy["label"] = label_props
        
        return hierarchy
    
    def responsive_scale(self, level: str) -> Dict[str, int]:
        """
        Retorna escala responsive de sizes para un nivel.
        
        Args:
            level: "headline", "display", "body", "caption"
        
        Returns:
            Dict con mobile, tablet, desktop sizes
        """
        return self.RESPONSIVE_SCALES.get(level, self.RESPONSIVE_SCALES["body"])
    
    def extract_from_yaml(self, typography_yaml: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae información de tipografía desde YAML de DESIGN.md.
        
        Args:
            typography_yaml: Sección 'typography' del YAML
        
        Returns:
            Diccionario estructurado de tipografía
        """
        result = {
            "extracted_fonts": [],
            "extracted_levels": {},
            "default_size": 16,
            "default_weight": 400,
        }
        
        if not typography_yaml:
            return result
        
        fonts_seen = set()
        
        for level_name, props in typography_yaml.items():
            if isinstance(props, dict):
                level_info = {}
                
                if "fontFamily" in props:
                    font = props["fontFamily"]
                    level_info["font"] = font
                    fonts_seen.add(font)
                
                if "fontSize" in props:
                    size = props["fontSize"]
                    # Parsear size (ej: "16px" -> 16)
                    if isinstance(size, str):
                        import re
                        match = re.search(r'(\d+)', size)
                        if match:
                            level_info["size"] = int(match.group(1))
                    else:
                        level_info["size"] = int(size)
                
                if "fontWeight" in props:
                    level_info["weight"] = int(props["fontWeight"])
                
                if "lineHeight" in props:
                    level_info["lineHeight"] = props["lineHeight"]
                
                if "letterSpacing" in props:
                    level_info["letterSpacing"] = props["letterSpacing"]
                
                result["extracted_levels"][level_name] = level_info
        
        result["extracted_fonts"] = list(fonts_seen)
        
        # Detectar default size
        for level_info in result["extracted_levels"].values():
            if "size" in level_info:
                result["default_size"] = level_info["size"]
                break
        
        return result
    
    def generate_google_fonts_links(self, fonts: List[str]) -> str:
        """
        Genera HTML <link> tags para Google Fonts.
        
        Args:
            fonts: Lista de nombres de fuentes
        
        Returns:
            String HTML con <link> tags
        """
        # Limitar a fuentes comunes que existen en Google Fonts
        google_fonts_map = {
            "Inter": "family=Inter:wght@400;500;600;700&display=swap",
            "Plus Jakarta Sans": "family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
            "Poppins": "family=Poppins:wght@400;600;700;800&display=swap",
            "Space Grotesk": "family=Space+Grotesk:wght@400;500;600;700&display=swap",
            "Crimson Text": "family=Crimson+Text:wght@400;600&display=swap",
            "Roboto": "family=Roboto:wght@400;500;700&display=swap",
            "Roboto Slab": "family=Roboto+Slab:wght@400;600;700&display=swap",
            "JetBrains Mono": "family=JetBrains+Mono:wght@400;600&display=swap",
            "Lato": "family=Lato:wght@400;700&display=swap",
        }
        
        links = []
        added = set()
        
        for font in fonts:
            if font in google_fonts_map and font not in added:
                link = f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                link += f'<link href="https://fonts.googleapis.com/css2?{google_fonts_map[font]}" rel="stylesheet">'
                links.append(link)
                added.add(font)
        
        # Agregar algunas fuentes por defecto si no hay
        if not links:
            links.append(
                '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
            )
        
        return '\n'.join(links)
    
    def css_variables_from_hierarchy(self, hierarchy: Dict[str, Dict]) -> str:
        """
        Genera CSS custom properties (variables) a partir de jerarquía.
        
        Returns:
            String con CSS :root { ... }
        """
        lines = [":root {"]
        
        for level_name, props in hierarchy.items():
            if isinstance(props, dict):
                var_name = f"--font-{level_name}"
                font_family = props.get("font", "system-ui")
                font_size = props.get("size", 16)
                font_weight = props.get("weight", 400)
                line_height = props.get("lineHeight", 1.5)
                
                lines.append(f"  {var_name}: {font_size}px {font_weight} {font_family};")
                lines.append(f"  {var_name}-size: {font_size}px;")
                lines.append(f"  {var_name}-weight: {font_weight};")
                lines.append(f"  {var_name}-family: {font_family};")
                lines.append(f"  {var_name}-height: {line_height};")
        
        lines.append("}")
        return "\n".join(lines)


# Singleton
_typography_analyzer_instance: Optional[TypographyAnalyzer] = None

def get_typography_analyzer() -> TypographyAnalyzer:
    """Obtiene instancia singleton."""
    global _typography_analyzer_instance
    if _typography_analyzer_instance is None:
        _typography_analyzer_instance = TypographyAnalyzer()
    return _typography_analyzer_instance
