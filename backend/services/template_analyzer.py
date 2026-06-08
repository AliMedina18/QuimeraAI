"""
template_analyzer.py -- Análisis inteligente de templates de diseño
===================================================================
Extrae patrones de composición, tipografía, colores y responsive
de templates reales para mejorar la generación de nuevos diseños.
"""

import logging
import random
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re

from backend.models import TemplatePattern, TemplateAnalysisContext
from backend.services.design_templates import get_templates_manager

logger = logging.getLogger(__name__)


class TemplateAnalyzer:
    """Analiza templates para extraer patrones inteligentes."""
    
    def __init__(self):
        self.templates_manager = get_templates_manager()
        self._cache: Dict[str, TemplatePattern] = {}
    
    def find_relevant_templates(
        self, 
        industry: Optional[str] = None,
        project_type: Optional[str] = None,
        design_reference: Optional[str] = None
    ) -> List[str]:
        """
        Encuentra templates relevantes según industria o tipo de proyecto.
        
        Args:
            industry: "fintech", "saas", "marketplace", "design", etc.
            project_type: "landing_page", "dashboard", "app"
            design_reference: Template específico si el usuario lo sugiere
        
        Returns:
            Lista de nombres de templates recomendados
        """
        # Si el usuario proporciona un template específico, incluirlo primero
        recommended = []
        if design_reference:
            if design_reference.lower() in self.templates_manager.list_available():
                recommended.append(design_reference.lower())
        
        # Mapeo de industrias a templates sugeridos
        industry_map = {
            "fintech": ["stripe", "revolut", "kraken", "coinbase"],
            "saas": ["figma", "linear", "posthog", "slack", "notion"],
            "marketplace": ["airbnb", "uber"],
            "design": ["figma", "adobe"],
            "commerce": ["shopify", "stripe"],
            "productivity": ["notion", "linear", "slack"],
            "developer": ["github", "stripe", "vercel"],
            "media": ["youtube", "spotify", "theverge"],
            "social": ["facebook", "twitter"],
            "wellness": ["apple", "elevenlabs"],
        }
        
        # Agregar templates sugeridos por industria
        if industry:
            suggested = industry_map.get(industry.lower(), [])
            for template_name in suggested:
                if template_name not in recommended:
                    if template_name in self.templates_manager.list_available():
                        recommended.append(template_name)
        
        # Si no hay recomendaciones, agregar algunos templates destacados
        if not recommended:
            featured = ["stripe", "figma", "airbnb", "slack", "apple"]
            for template_name in featured:
                if template_name in self.templates_manager.list_available():
                    recommended.append(template_name)
        
        # Limitar a 5 templates para análisis
        return recommended[:5]
    
    def extract_pattern(self, template_name: str) -> Optional[TemplatePattern]:
        """
        Extrae el patrón de un template analizando su DESIGN.md.
        
        Args:
            template_name: Nombre del template (ej: "airbnb", "stripe")
        
        Returns:
            TemplatePattern con los datos extraídos
        """
        # Verificar cache
        if template_name in self._cache:
            return self._cache[template_name]
        
        # Obtener el DESIGN.md del template
        design_md = self.templates_manager.get_template(template_name)
        if not design_md:
            logger.warning(f"Template {template_name} no encontrado")
            return None
        
        # Parsear YAML para extraer tokens
        import yaml
        parts = design_md.split('---', 2)
        if len(parts) < 3:
            return None
        
        try:
            tokens = yaml.safe_load(parts[1])
        except Exception as e:
            logger.warning(f"Error parseando YAML de {template_name}: {e}")
            return None
        
        # Extraer de markdown body
        body = parts[2] if len(parts) > 2 else ""
        
        # Crear pattern
        pattern = TemplatePattern(
            name=template_name,
            composition=self._extract_composition(body),
            typography=self._extract_typography(tokens),
            colors_strategy=self._extract_colors_strategy(body),
            colors_sample=self._extract_colors_sample(tokens),
            responsive_strategy=self._extract_responsive(body),
            elevation_strategy=self._extract_elevation(body),
            spacing_base=self._extract_spacing_base(tokens),
            corner_radius_philosophy=self._extract_corner_radius(tokens),
        )
        
        self._cache[template_name] = pattern
        return pattern
    
    def _extract_composition(self, body: str) -> str:
        """Extrae descripción de composición/layout del markdown."""
        # Buscar sección "Layout & Spacing"
        match = re.search(r'## Layout.*?\n(.+?)(?=##|$)', body, re.DOTALL)
        if match:
            text = match.group(1)[:200]  # Primeras 200 caracteres
            # Limpiar líneas vacías
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return ' '.join(lines[:3])
        return "Grid layout, responsive mobile-first"
    
    def _extract_typography(self, tokens: dict) -> Dict[str, str]:
        """Extrae tipografía de los tokens YAML."""
        result = {}
        if not tokens or 'typography' not in tokens:
            return result
        
        for name, props in tokens['typography'].items():
            if isinstance(props, dict):
                family = props.get('fontFamily', 'sans-serif')
                size = props.get('fontSize', '16px')
                weight = props.get('fontWeight', '400')
                result[name] = f"{family}, {size} {weight}"
            else:
                result[name] = str(props)
        
        return result
    
    def _extract_colors_strategy(self, body: str) -> str:
        """Extrae estrategia de colores del markdown."""
        match = re.search(r'## Colors.*?\n(.+?)(?=##|$)', body, re.DOTALL)
        if match:
            text = match.group(1)[:150]
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return ' '.join(lines[:2])
        return "Primary + secondary + neutral palette"
    
    def _extract_colors_sample(self, tokens: dict) -> Dict[str, str]:
        """Extrae paleta de colores de los tokens YAML."""
        result = {}
        if not tokens or 'colors' not in tokens:
            return result
        
        colors = tokens['colors']
        # Tomar primeros 5 colores
        for key, value in list(colors.items())[:5]:
            if isinstance(value, str):
                result[key] = value
        
        return result
    
    def _extract_responsive(self, body: str) -> str:
        """Extrae estrategia responsive del markdown."""
        match = re.search(r'## Layout.*?\n(.+?)(?=##|$)', body, re.DOTALL)
        if match:
            text = match.group(1)
            if 'mobile-first' in text.lower():
                return "mobile-first"
            elif 'desktop-first' in text.lower():
                return "desktop-first"
        return "mobile-first"
    
    def _extract_elevation(self, body: str) -> str:
        """Extrae estrategia de elevación (sombras, glassmorphism, etc)."""
        match = re.search(r'## Elevation.*?\n(.+?)(?=##|$)', body, re.DOTALL)
        if match:
            text = match.group(1).lower()
            if 'glassmorphism' in text or 'glass' in text or 'blur' in text:
                return "glassmorphism"
            elif 'neumorphism' in text:
                return "neumorphism"
            elif 'flat' in text:
                return "flat"
            else:
                return "shadows"
        return "shadows"
    
    def _extract_spacing_base(self, tokens: dict) -> str:
        """Extrae unidad base de espaciado."""
        if not tokens or 'spacing' not in tokens:
            return "8px"
        
        spacing = tokens['spacing']
        if 'base' in spacing:
            return str(spacing['base'])
        elif 'xs' in spacing:
            return str(spacing['xs'])
        
        return "8px"
    
    def _extract_corner_radius(self, tokens: dict) -> str:
        """Extrae filosofía de border radius."""
        if not tokens or 'rounded' not in tokens:
            return "12px rounded, friendly aesthetic"
        
        rounded = tokens['rounded']
        default_radius = rounded.get('DEFAULT', '8px')
        
        if isinstance(default_radius, str):
            if 'full' in str(rounded.get('full', '')):
                return f"Rounded {default_radius} with full pill buttons"
            else:
                return f"{default_radius} border radius, balanced style"
        
        return "Moderate border radius"
    
    async def analyze_all_relevant(
        self,
        industry: Optional[str] = None,
        project_type: Optional[str] = None,
        design_reference: Optional[str] = None
    ) -> TemplateAnalysisContext:
        """
        Análisis completo: encuentra templates relevantes y extrae sus patrones.
        
        Returns:
            TemplateAnalysisContext con análisis completo
        """
        relevant = self.find_relevant_templates(industry, project_type, design_reference)
        
        patterns = {}
        for template_name in relevant:
            pattern = self.extract_pattern(template_name)
            if pattern:
                patterns[template_name] = pattern
        
        # Resumen de estrategia
        primary = relevant[0] if relevant else None
        summary = f"Using {len(patterns)} reference templates"
        if primary and primary in patterns:
            p = patterns[primary]
            summary = f"Primary reference: {primary}. Composition: {p.composition}. Colors: {p.colors_strategy}"
        
        return TemplateAnalysisContext(
            relevant_templates=relevant,
            primary_template=primary,
            industry=industry,
            patterns=patterns,
            design_strategy_summary=summary
        )


# Singleton
_analyzer_instance: Optional[TemplateAnalyzer] = None

def get_template_analyzer() -> TemplateAnalyzer:
    """Obtiene instancia singleton del analizador."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = TemplateAnalyzer()
    return _analyzer_instance
