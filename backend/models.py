"""
models.py -- Todos los modelos Pydantic de Quimera
===================================================
DesignContext  : Estado compartido del pipeline (Seccion 7.1)
DesignRequest  : Payload de entrada del usuario
DesignProposal : Output del Paso 1
AestheticScores: Output del Paso 2 (8 criterios)
GeneratedOutput: Output del Paso 3
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class DesignContext(BaseModel):
    """La memoria de trabajo de Quimera. Fluye por los 3 pasos del pipeline."""
    # Paso 1: Analisis
    design_brief: str = Field(..., description="Descripcion original del usuario")
    project_type: str = Field(default="", description="landing_page | dashboard | app")
    industry: str = Field(default="", description="fintech | healthtech | e-commerce...")
    target_audience: str = Field(default="", description="Audiencia objetivo")
    brand_personality: list[str] = Field(default_factory=list)

    # Propuesta de diseno (generada en Paso 1, refinada si hay correccion)
    primary_color: Optional[str] = Field(default=None)
    secondary_color: Optional[str] = Field(default=None)
    accent_color: Optional[str] = Field(default=None)
    neutral_palette: list[str] = Field(default_factory=list)
    heading_font: Optional[str] = Field(default=None)
    body_font: Optional[str] = Field(default=None)
    layout_type: Optional[str] = Field(default=None)
    composition_rule: Optional[str] = Field(default=None, description="rule_of_thirds | golden_ratio")
    color_harmony_type: Optional[str] = Field(default=None, description="complementario | analogo | triadico | monocromatico")
    design_rationale: dict = Field(default_factory=dict, description="{campo: {valor, principio, razon}}")

    # Resultados de evaluacion (llenados por step2_evaluate.py)
    aesthetic_scores: dict = Field(default_factory=dict, description="{criterio: float 0-100}")
    overall_score: Optional[float] = Field(default=None, description="Promedio de los 8 criterios. Umbral: >= 85")
    critique: Optional[str] = Field(default=None, description="Que falla y que valor lo resuelve")
    approved: bool = Field(default=False, description="True cuando overall_score >= 85")
    iteration: int = Field(default=0, description="Numero de iteracion actual. Maximo 3.")

    # Codigo generado (llenados por step3_generate.py)
    react_component: Optional[str] = Field(default=None)
    design_tokens_css: Optional[str] = Field(default=None)
    rationale_document: Optional[str] = Field(default=None)


class DesignRequest(BaseModel):
    """Payload de entrada al endpoint POST /generar-diseno"""
    design_brief: str = Field(..., min_length=10)
    project_type: Optional[str] = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "design_brief": "Landing page para app de finanzas. Publico jovenes 25-35. Colores azul y blanco.",
                "project_type": "landing_page"
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


class DesignProposal(BaseModel):
    """Propuesta de diseno estructurada -- output del Paso 1."""
    primary_color: str
    secondary_color: str
    accent_color: str
    neutral_palette: list[str]
    heading_font: str
    body_font: str
    layout_type: str
    composition_rule: str
    color_harmony_type: str
    design_rationale: dict


class AestheticScores(BaseModel):
    """
    Resultado del Motor de Evaluacion Estetica.
    8 criterios de 0 a 100. overall_score = promedio. Pasa si >= 85.
    Criterios 1-2: algoritmicos. Criterios 3-8: LLM temperatura=0.
    """
    color_harmony: float = Field(..., ge=0, le=100)
    wcag_contrast: float = Field(..., ge=0, le=100)
    composition_balance: float = Field(..., ge=0, le=100)
    visual_hierarchy: float = Field(..., ge=0, le=100)
    gestalt_compliance: float = Field(..., ge=0, le=100)
    whitespace_quality: float = Field(..., ge=0, le=100)
    brand_consistency: float = Field(..., ge=0, le=100)
    accessibility: float = Field(..., ge=0, le=100)
    iteration: int = Field(default=1)
    critique: Optional[str] = Field(default=None)

    @property
    def overall_score(self) -> float:
        scores = [
            self.color_harmony, self.wcag_contrast,
            self.composition_balance, self.visual_hierarchy,
            self.gestalt_compliance, self.whitespace_quality,
            self.brand_consistency, self.accessibility,
        ]
        return round(sum(scores) / len(scores), 2)

    @property
    def passed(self) -> bool:
        return self.overall_score >= 85.0

    def failing_criteria(self) -> list[str]:
        criteria = {
            "color_harmony": self.color_harmony,
            "wcag_contrast": self.wcag_contrast,
            "composition_balance": self.composition_balance,
            "visual_hierarchy": self.visual_hierarchy,
            "gestalt_compliance": self.gestalt_compliance,
            "whitespace_quality": self.whitespace_quality,
            "brand_consistency": self.brand_consistency,
            "accessibility": self.accessibility,
        }
        return [name for name, score in criteria.items() if score < 85.0]

    def to_dict(self) -> dict:
        return {
            "color_harmony": self.color_harmony,
            "wcag_contrast": self.wcag_contrast,
            "composition_balance": self.composition_balance,
            "visual_hierarchy": self.visual_hierarchy,
            "gestalt_compliance": self.gestalt_compliance,
            "whitespace_quality": self.whitespace_quality,
            "brand_consistency": self.brand_consistency,
            "accessibility": self.accessibility,
            "overall_score": self.overall_score,
            "passed": self.passed,
            "iteration": self.iteration,
            "critique": self.critique,
        }


class GeneratedOutput(BaseModel):
    """Output final del pipeline -- se guarda en Firestore y Cloud Storage."""
    model_config = {'protected_namespaces': ()}

    react_component: str
    design_tokens_css: str
    rationale_document: str
    model_used: str = Field(default="gemini-2.5-flash")
    aesthetic_scores: Optional[AestheticScores] = Field(default=None)
    iterations_needed: int = Field(default=1)
    generation_time_ms: Optional[int] = Field(default=None)
