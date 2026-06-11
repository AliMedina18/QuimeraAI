"""
models.py -- Modelos Pydantic de Quimera v3 (MEJORADO)
======================================================
Pipeline de 4 pasos:
  Step 0: Template Analysis (patrones + composición)
  Step 1: Generate DESIGN.md (basado en templates)
  Step 2: Analyze Images (plan de generación)
  Step 3: Generate HTML + Images (output final)

DesignContext: estado compartido del pipeline
"""
from __future__ import annotations
from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field


# ============================================================================
# STEP 0: TEMPLATE ANALYSIS
# ============================================================================

class TemplatePattern(BaseModel):
    """Patrón extraído de un template de diseño."""
    name: str                          # "airbnb", "stripe", etc.
    composition: str                   # "Fluid Grid, 3-col mobile-first"
    typography: Dict[str, str]         # {"display": "Circular, 28px 700", ...}
    colors_strategy: str               # "Warm + accent + neutral"
    colors_sample: Dict[str, str]      # {"primary": "#ff385c", ...}
    responsive_strategy: str           # "mobile-first", "desktop-first"
    elevation_strategy: str            # "shadows", "flat", "glassmorphism"
    spacing_base: str                  # "8px", "4px", etc.
    corner_radius_philosophy: str      # "12px rounded-friendly", etc.


class TemplateAnalysisContext(BaseModel):
    """Resultado del Step 0: análisis de templates relevantes."""
    relevant_templates: List[str]      # Templates encontrados ["stripe", "figma", ...]
    primary_template: Optional[str]    # Template mejor matcheado
    industry: Optional[str]            # "fintech", "saas", "marketplace", etc.
    patterns: Dict[str, TemplatePattern]  # Patrones extraídos
    design_strategy_summary: str       # Resumen de estrategia a usar


# ============================================================================
# STEP 2: IMAGE GENERATION PLAN
# ============================================================================

class ImageSpec(BaseModel):
    """Especificación de una imagen a generar."""
    section: str                       # "hero", "feature-1", "cta", "background"
    description: str                   # Descripción para generar imagen
    style: str                         # "modern", "minimalist", "vibrant", etc.
    size: Tuple[int, int]              # (width, height) ej: (1200, 630)
    prompt: str                        # Prompt completo para Imagen 3


class ImageGenerationPlan(BaseModel):
    """Plan de generación de imágenes para el diseño."""
    images: List[ImageSpec] = Field(default_factory=list)
    total_count: int = 0
    estimated_cost: float = 0.0        # Estimación de costo en USD


# ============================================================================
# MAIN: DESIGN CONTEXT (ACTUALIZADO)
# ============================================================================

class DesignContext(BaseModel):
    """La memoria de trabajo de Quimera v3. Fluye por los 4 pasos del pipeline."""

    # INPUT: Solicitud del usuario
    design_brief: str = Field(..., description="Descripcion original del usuario")
    project_type: Optional[str] = Field(default=None, description="landing_page | dashboard | app")
    design_reference: Optional[str] = Field(default=None, description="Template de referencia: airbnb, figma, stripe, etc.")

    # STEP 0: Template Analysis
    template_analysis: Optional[TemplateAnalysisContext] = Field(default=None, description="Resultado del análisis de templates")

    # STEP 1: DESIGN.md Generation
    design_markdown: Optional[str] = Field(default=None, description="Archivo DESIGN.md completo (YAML + prose)")
    design_tokens_json: Optional[dict] = Field(default=None, description="Tokens extraidos del DESIGN.md como JSON")

    # STEP 2: Image Analysis
    image_generation_plan: Optional[ImageGenerationPlan] = Field(default=None, description="Plan de generación de imágenes")

    # STEP 3: HTML + Images Generation
    html_output: Optional[str] = Field(default=None, description="Archivo HTML completo con imágenes inyectadas")
    generated_images: Optional[Dict[str, str]] = Field(default=None, description="URLs o base64 de imágenes generadas")


class DesignRequest(BaseModel):
    """Payload de entrada al endpoint POST /generar-diseno"""
    design_brief: str = Field(..., min_length=10, description="Descripción del diseño que se desea generar")
    project_type: Optional[str] = Field(default=None, description="Tipo: landing_page, dashboard, app, etc.")
    design_reference: Optional[str] = Field(default=None, description="Template de referencia: airbnb, figma, stripe, spotify, etc. Si se proporciona, mejora la calidad del diseño generado")

    model_config = {
        "json_schema_extra": {
            "example": {
                "design_brief": "Landing page para app de finanzas. Público jóvenes 25-35. Colores azul y blanco. Minimalista, moderno.",
                "project_type": "landing_page",
                "design_reference": "stripe"
            }
        }
    }


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class GeminiTestResponse(BaseModel):
    model_config = {'protected_namespaces': ()}

    status: str
    model_used: str
    gemini_response: str


# ============================================================================
# SUGERENCIAS DE BRIEF
# ============================================================================

class SuggestRequest(BaseModel):
    """Payload del endpoint POST /sugerir"""
    brief: str = Field(..., min_length=3, description="Texto del brief a analizar")


class MissingElement(BaseModel):
    """Elemento que falta en el brief."""
    key: str
    label: str
    hint: str
    chip_text: str


class StyleSuggestion(BaseModel):
    """Estilo de diseño recomendado."""
    id: str
    label: str
    emoji: str
    description: str
    chip_text: str


class TemplateSuggestion(BaseModel):
    """Template de referencia recomendado."""
    slug: str
    label: str
    mood: str
    chip_text: str


class ColorPalette(BaseModel):
    """Paleta de color recomendada."""
    name: str
    primary: str
    secondary: str
    accent: str
    surface: str
    text: str
    chip_text: str


class SuggestResponse(BaseModel):
    """Respuesta del endpoint POST /sugerir"""
    industry: str
    confidence: float
    missing: List[MissingElement]
    styles: List[StyleSuggestion]
    templates: List[TemplateSuggestion]
    palettes: List[ColorPalette]


# ============================================================================
# OUTPUT PERSISTENCIA (Day 4)
# ============================================================================

class GeneratedOutput(BaseModel):
    """
    Output final del pipeline para persistencia (Firestore + Cloud Storage).
    Usado por services/firestore_client.py y services/storage_client.py (Day 4).
    """
    model_config = {'protected_namespaces': ()}

    design_brief: str
    design_markdown: str
    html_output: str
    model_used: str = Field(default="gemini-2.5-flash")
    generation_time_ms: Optional[int] = Field(default=None)
    template_used: Optional[str] = Field(default=None)
