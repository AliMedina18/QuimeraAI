"""
step2_analyze_images.py -- PASO 2: Análisis para Generación de Imágenes
========================================================================
Analiza DESIGN.md y decide dónde generar imágenes automáticamente.

Input:  DesignContext (con design_markdown)
Output: DesignContext (con image_generation_plan)
"""

import logging
import re
from backend.models import DesignContext, ImageSpec, ImageGenerationPlan
from backend.services.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


async def analyze_for_images(context: DesignContext) -> DesignContext:
    """
    Step 2: Analiza qué imágenes generar para el diseño.
    
    Identifica secciones que necesitan imágenes:
    - Hero banner
    - Feature/benefit images
    - Background patterns
    - Icons/illustrations
    
    Args:
        context: DesignContext con design_markdown
    
    Returns:
        DesignContext actualizado con image_generation_plan
    """
    if not context.design_markdown:
        logger.warning("Step 2: design_markdown vacío, saltando análisis de imágenes")
        context.image_generation_plan = ImageGenerationPlan(images=[], total_count=0)
        return context
    
    logger.info("Step 2: Analizando para generación de imágenes...")
    
    # Extraer información de secciones del DESIGN.md
    brief_excerpt = context.design_brief[:300]
    
    # Crear plan de imágenes
    image_plan = ImageGenerationPlan(images=[])
    
    # Hero image (siempre)
    hero_spec = ImageSpec(
        section="hero",
        description=f"Hero banner for {brief_excerpt}",
        style="modern",
        size=(1200, 630),
        prompt=_generate_hero_prompt(context)
    )
    image_plan.images.append(hero_spec)
    
    # Feature images (si hay características)
    feature_specs = _extract_feature_images(context)
    image_plan.images.extend(feature_specs)
    
    # Background pattern (opcional)
    if len(image_plan.images) < 3:  # Si hay poco contenido, agregar patrón
        pattern_spec = ImageSpec(
            section="background-pattern",
            description="Subtle background pattern",
            style="geometric",
            size=(1200, 1200),
            prompt="Subtle geometric pattern, modern, tileable"
        )
        image_plan.images.append(pattern_spec)
    
    image_plan.total_count = len(image_plan.images)
    image_plan.estimated_cost = image_plan.total_count * 0.04  # ~$0.04 per image
    
    context.image_generation_plan = image_plan
    
    logger.info(f"Step 2: OK. Plan: {image_plan.total_count} imágenes a generar")
    
    return context


def _generate_hero_prompt(context: DesignContext) -> str:
    """Genera prompt descriptivo para Hero image."""
    brief = context.design_brief[:100]
    
    # Detectar tema/color del brief
    colors = _extract_colors_from_brief(context.design_brief)
    color_str = f"using colors {colors}" if colors else ""
    
    prompt = (
        f"Professional hero banner for: {brief}. "
        f"Modern, clean, premium aesthetic {color_str}. "
        f"High-quality image, suitable for web. "
        f"Wide format (1200x630). No text overlays."
    )
    
    return prompt


def _extract_feature_images(context: DesignContext) -> list:
    """Extrae especificaciones de feature images del design_markdown."""
    specs = []
    
    # Buscar secciones de features/benefits en el markdown
    markdown = context.design_markdown or ""
    
    # Patrón simple: buscar listas o secciones después de "Features" o "Benefits"
    feature_pattern = r'(?:## Features|## Benefits)(.*?)(?=##|$)'
    match = re.search(feature_pattern, markdown, re.IGNORECASE | re.DOTALL)
    
    if match:
        features_text = match.group(1)
        # Buscar items (líneas que empiezan con -)
        items = re.findall(r'-\s+([^\n]+)', features_text)
        
        for i, item in enumerate(items[:3]):  # Máximo 3 feature images
            spec = ImageSpec(
                section=f"feature-{i+1}",
                description=item[:80],  # Primeros 80 caracteres
                style="modern",
                size=(600, 400),
                prompt=f"Illustration for: {item}. Professional, minimalist style."
            )
            specs.append(spec)
    
    return specs


def _extract_colors_from_brief(brief: str) -> str:
    """Extrae colores mencionados en el brief."""
    color_keywords = {
        "blue": "#0066cc",
        "red": "#ff0000",
        "green": "#00cc00",
        "purple": "#9933cc",
        "orange": "#ff9900",
        "pink": "#ff1493",
        "yellow": "#ffcc00",
        "gray": "#666666",
        "white": "#ffffff",
        "black": "#000000",
    }
    
    colors = []
    for color_name, color_hex in color_keywords.items():
        if color_name in brief.lower():
            colors.append(color_name)
    
    return ", ".join(colors[:2]) if colors else ""
