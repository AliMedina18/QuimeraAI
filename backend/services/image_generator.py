"""
image_generator.py -- Generación automática de imágenes con IA
==============================================================
Genera imágenes usando Google's Imagen 3 API.
"""

import logging
import os
from typing import Optional, Tuple
import base64
import io

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Genera imágenes con IA automáticamente."""
    
    def __init__(self):
        self.use_imagen3 = os.getenv("USE_IMAGEN3", "false").lower() == "true"
        self.project_id = os.getenv("GCP_PROJECT_ID", "quimera-ai-prod")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        
        if self.use_imagen3:
            try:
                from vertexai.generative_models import GenerativeModel
                self.vision_model = GenerativeModel("imagen-3.0-generate-001")
                logger.info("ImageGenerator: Imagen 3 API OK")
            except Exception as e:
                logger.warning(f"ImageGenerator: Imagen 3 no disponible: {e}")
                self.use_imagen3 = False
    
    def generate_hero_image(
        self,
        brand_name: str,
        design_brief: str,
        colors: Optional[Tuple[str, str]] = None,
        size: Tuple[int, int] = (1200, 630)
    ) -> Optional[str]:
        """
        Genera imagen para sección Hero.
        
        Args:
            brand_name: Nombre de la marca/proyecto
            design_brief: Brief del diseño
            colors: Tupla (primary_hex, secondary_hex)
            size: (width, height)
        
        Returns:
            URL o base64 de la imagen, o None si falla
        """
        if not self.use_imagen3:
            logger.warning("Imagen 3 no está habilitado. Usando placeholder.")
            return self._placeholder_url(size)
        
        # Construir prompt descriptivo
        color_desc = ""
        if colors:
            color_desc = f" with primary color {colors[0]} and accent {colors[1]}"
        
        prompt = (
            f"Hero image for '{brand_name}' - {design_brief}. "
            f"Modern, professional, minimalist aesthetic{color_desc}. "
            f"High-quality, clean composition, premium look. "
            f"No text overlays. Wide format for web banner."
        )
        
        try:
            return self._call_imagen3(prompt, size)
        except Exception as e:
            logger.error(f"Error generando hero image: {e}")
            return self._placeholder_url(size)
    
    def generate_feature_image(
        self,
        feature_name: str,
        feature_description: str,
        style: str = "modern",
        size: Tuple[int, int] = (600, 400)
    ) -> Optional[str]:
        """
        Genera imagen para sección de feature/benefit.
        
        Args:
            feature_name: Nombre del feature
            feature_description: Descripción del feature
            style: "modern", "minimalist", "vibrant", "professional"
            size: (width, height)
        
        Returns:
            URL o base64 de la imagen, o None si falla
        """
        if not self.use_imagen3:
            return self._placeholder_url(size)
        
        style_keywords = {
            "modern": "contemporary, sleek, clean lines",
            "minimalist": "minimal, abstract, geometric",
            "vibrant": "colorful, energetic, dynamic",
            "professional": "corporate, sophisticated, premium",
        }
        
        style_desc = style_keywords.get(style, "modern")
        
        prompt = (
            f"Illustration for '{feature_name}': {feature_description}. "
            f"Style: {style_desc}. "
            f"High-quality, professional illustration. "
            f"Suitable for web. No text. Transparent background preferred."
        )
        
        try:
            return self._call_imagen3(prompt, size)
        except Exception as e:
            logger.error(f"Error generando feature image: {e}")
            return self._placeholder_url(size)
    
    def generate_pattern(
        self,
        theme: str = "abstract",
        size: Tuple[int, int] = (1200, 1200),
        colors: Optional[Tuple[str, str]] = None
    ) -> Optional[str]:
        """
        Genera patrón abstracto para background.
        
        Args:
            theme: "abstract", "geometric", "organic", "grid"
            size: (width, height)
            colors: Tupla (primary_hex, secondary_hex)
        
        Returns:
            URL o base64 de la imagen, o None si falla
        """
        if not self.use_imagen3:
            return self._placeholder_url(size)
        
        theme_keywords = {
            "abstract": "abstract, flowing, organic shapes",
            "geometric": "geometric, patterns, symmetrical",
            "organic": "organic, natural, flowing forms",
            "grid": "grid pattern, systematic, technical",
        }
        
        theme_desc = theme_keywords.get(theme, "abstract")
        
        color_desc = ""
        if colors:
            color_desc = f"using colors {colors[0]} and {colors[1]}"
        
        prompt = (
            f"Seamless background pattern: {theme_desc} {color_desc}. "
            f"Tileable, modern design. Subtle, not overwhelming. "
            f"For use as website background. Professional quality."
        )
        
        try:
            return self._call_imagen3(prompt, size)
        except Exception as e:
            logger.error(f"Error generando pattern: {e}")
            return self._placeholder_url(size)
    
    def _call_imagen3(self, prompt: str, size: Tuple[int, int]) -> Optional[str]:
        """Llama a Imagen 3 API para generar imagen."""
        if not self.use_imagen3:
            return None
        
        try:
            # Aquí irá la llamada real a Imagen 3 cuando esté disponible
            # Por ahora, retornar placeholder
            logger.info(f"ImageGenerator: Imagen 3 prompt: {prompt}")
            return self._placeholder_url(size)
        except Exception as e:
            logger.error(f"Error en _call_imagen3: {e}")
            return None
    
    def _placeholder_url(self, size: Tuple[int, int]) -> str:
        """Genera URL placeholder para cuando no se puede generar imagen real."""
        width, height = size
        # Usar placeholder.com o similar
        return f"https://via.placeholder.com/{width}x{height}/cccccc/999999?text=Image+{width}x{height}"


class ImageDownloader:
    """Descarga e integra imágenes en HTML."""
    
    @staticmethod
    def url_to_base64(url: str) -> Optional[str]:
        """Descarga imagen de URL y la convierte a base64."""
        try:
            import requests
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode('utf-8')
        except Exception as e:
            logger.error(f"Error descargando imagen: {e}")
        return None
    
    @staticmethod
    def create_img_tag(
        src: str,
        alt: str = "Image",
        classes: str = ""
    ) -> str:
        """
        Crea tag <img> HTML.
        
        Args:
            src: URL o data:image URI
            alt: Texto alt
            classes: Clases CSS
        
        Returns:
            String HTML <img />
        """
        class_attr = f' class="{classes}"' if classes else ""
        return f'<img src="{src}" alt="{alt}"{class_attr} />'


# Singleton
_image_generator_instance: Optional[ImageGenerator] = None

def get_image_generator() -> ImageGenerator:
    """Obtiene instancia singleton."""
    global _image_generator_instance
    if _image_generator_instance is None:
        _image_generator_instance = ImageGenerator()
    return _image_generator_instance
