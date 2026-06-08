"""
models.py -- Modelos Pydantic de Quimera (SIMPLIFICADO)
=======================================================
Quimera es ahora un generador simple de interfaces.
Pipeline: User Brief → DESIGN.md → HTML completo (2 pasos)

DesignContext  : Estado compartido del pipeline
DesignRequest  : Entrada del usuario
DesignMarkdown : Output del Paso 1 (DESIGN.md)
GeneratedCode  : Output del Paso 2 (HTML autocontenido)
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class DesignContext(BaseModel):
    """La memoria de trabajo de Quimera. Fluye por los 2 pasos del pipeline simplificado."""
    # Entrada del usuario
    design_brief: str = Field(..., description="Descripcion original del usuario")
    project_type: Optional[str] = Field(default=None, description="landing_page | dashboard | app")

    # Output Paso 1: DESIGN.md generado
    design_markdown: Optional[str] = Field(default=None, description="Archivo DESIGN.md completo (YAML + prose)")

    # Output Paso 2: HTML autocontenido generado
    html_output: Optional[str] = Field(default=None, description="Archivo HTML completo que implementa el diseño (Tailwind + CSS inline + JS vanilla)")
    design_tokens_json: Optional[dict] = Field(default=None, description="Tokens extraidos del DESIGN.md como JSON")


class DesignRequest(BaseModel):
    """Payload de entrada al endpoint POST /generar-diseno"""
    design_brief: str = Field(..., min_length=10, description="Descripción del diseño que se desea generar")
    project_type: Optional[str] = Field(default=None, description="Tipo: landing_page, dashboard, app, etc.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "design_brief": "Landing page para app de finanzas. Público jóvenes 25-35. Colores azul y blanco. Minimalista, moderno.",
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



class GeneratedOutput(BaseModel):
    """Output final del pipeline -- se guarda en Firestore y Cloud Storage."""
    model_config = {'protected_namespaces': ()}

    html_output: str
    design_tokens_css: str
    rationale_document: str
    model_used: str = Field(default="gemini-2.5-flash")
    iterations_needed: int = Field(default=1)
    generation_time_ms: Optional[int] = Field(default=None)
