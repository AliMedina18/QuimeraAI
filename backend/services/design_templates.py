"""
design_templates.py - Gestor de plantillas de diseno

Carga DESIGN.md reales desde backend/design_templates/ y los proporciona
como contexto para mejorar la generacion de nuevos disenos.
"""

import logging
import os
import random
import re
import json
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class DesignTemplatesManager:
    """Gestor de plantillas de diseno profesionales."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self._templates_cache: Dict[str, str] = {}
        self._load_all_templates()

    def _load_all_templates(self):
        """Carga todos los DESIGN.md desde el directorio de templates."""
        if not self.templates_dir.exists():
            logger.warning("Directorio de templates no encontrado: %s", self.templates_dir)
            return

        for brand_dir in self.templates_dir.iterdir():
            if brand_dir.is_dir():
                design_file = brand_dir / "DESIGN.md"
                if design_file.exists():
                    brand_name = brand_dir.name
                    try:
                        with open(design_file, "r", encoding="utf-8") as f:
                            self._templates_cache[brand_name] = f.read()
                    except Exception as e:
                        logger.warning("Error cargando template '%s': %s", brand_name, e)

    def list_available(self) -> List[str]:
        """Retorna lista de templates disponibles ordenada alfabeticamente."""
        return sorted(list(self._templates_cache.keys()))

    def get_template(self, design_reference: str) -> Optional[str]:
        """
        Obtiene un template especifico por nombre.

        Args:
            design_reference: Nombre del template (ej: "airbnb", "figma", "stripe")

        Returns:
            Contenido del DESIGN.md o None si no existe
        """
        return self._templates_cache.get(design_reference.lower())

    def get_random_template(self) -> tuple:
        """
        Retorna un template aleatorio.

        Returns:
            Tupla (nombre, contenido)
        """
        if not self._templates_cache:
            raise ValueError("No templates available")
        name = random.choice(list(self._templates_cache.keys()))
        return name, self._templates_cache[name]

    def get_template_by_industry(self, industry: str) -> Optional[tuple]:
        """
        Sugiere un template basado en la industria.

        Args:
            industry: Tipo de industria (ej: "fintech", "saas", "marketplace")

        Returns:
            Tupla (nombre, contenido) o None
        """
        industry_lower = industry.lower()
        industry_map = {
            "fintech": ["stripe", "payment"],
            "marketplace": ["airbnb", "ebay"],
            "saas": ["figma", "linear", "posthog", "slack"],
            "design": ["figma"],
            "video": ["youtube", "theverge"],
            "music": ["spotify", "soundcloud"],
            "commerce": ["shopify", "stripe"],
            "social": ["facebook", "twitter"],
            "wellness": ["apple", "elevenlabs"],
            "productivity": ["notion", "linear"],
            "developer": ["github", "stripe", "vercel"],
        }
        suggested = industry_map.get(industry_lower, [])
        for template_name in suggested:
            if template_name in self._templates_cache:
                return template_name, self._templates_cache[template_name]
        if self._templates_cache:
            return self.get_random_template()
        return None

    def get_template_metadata(self, design_reference: str) -> Optional[Dict]:
        """
        Extrae metadata del DESIGN.md (name, description, colors count, etc.)

        Args:
            design_reference: Nombre del template

        Returns:
            Dict con metadata o None
        """
        content = self.get_template(design_reference)
        if not content:
            return None

        name_match = re.search(r"name:\s*(.+)", content)
        name = name_match.group(1).strip() if name_match else design_reference

        desc_match = re.search(r'description:\s*["\']?(.+?)["\']?\n', content)
        description = desc_match.group(1).strip() if desc_match else ""

        colors_match = re.findall(r'^\s+\w+:\s*"#[0-9a-f]{6}"', content, re.MULTILINE)
        color_count = len(colors_match)

        typo_section = (
            content.split("typography:")[1].split("rounded:")[0]
            if "typography:" in content
            else ""
        )
        typo_levels = len(re.findall(r"^\s+\w+:\s*$", typo_section, re.MULTILINE))

        return {
            "name": name,
            "description": description[:100] + "..." if len(description) > 100 else description,
            "colors": color_count,
            "typography_levels": typo_levels,
            "file": design_reference,
        }

    def get_all_metadata(self) -> Dict[str, Dict]:
        """Retorna metadata de todos los templates."""
        result = {}
        for template_name in self.list_available():
            metadata = self.get_template_metadata(template_name)
            if metadata:
                result[template_name] = metadata
        return result


# Instancia global (singleton)
_manager: Optional[DesignTemplatesManager] = None


def get_templates_manager() -> DesignTemplatesManager:
    """Retorna la instancia global del gestor de templates."""
    global _manager
    if _manager is None:
        _manager = DesignTemplatesManager()
    return _manager
