"""
test_spike1.py — Calidad del DESIGN.md generado por el pipeline
================================================================

Valida que Gemini genera paletas completas (≥3 colores HEX) y
frontmatter YAML con las secciones mínimas requeridas.

Marker: @pytest.mark.slow (llama a Gemini — requiere GOOGLE_API_KEY)
"""
import re

import pytest

from models import DesignContext
from pipeline.step1_analyze import analyze_and_design


@pytest.mark.slow
async def test_design_md_tiene_frontmatter_yaml():
    """DESIGN.md generado contiene frontmatter YAML con secciones mínimas."""
    context = DesignContext(
        design_brief=(
            "SaaS de gestión de proyectos para agencias creativas. "
            "B2B, moderno, profesional."
        ),
        project_type="dashboard",
    )
    context = await analyze_and_design(context)

    assert context.design_markdown, "DESIGN.md no fue generado"
    md = context.design_markdown

    assert "---" in md, "Falta delimitador YAML (---)"
    assert "colors:" in md, "Falta sección colors en YAML"
    assert "typography:" in md, "Falta sección typography en YAML"


@pytest.mark.slow
async def test_design_md_contiene_colores_hex():
    """DESIGN.md generado incluye al menos 3 colores HEX válidos."""
    context = DesignContext(
        design_brief=(
            "Landing page para app de fitness. Público 25-45 años activos. "
            "Transmitir confianza, energía y modernidad."
        ),
        project_type="landing_page",
    )
    context = await analyze_and_design(context)

    assert context.design_markdown, "DESIGN.md no fue generado"

    colors = re.findall(r"#[0-9a-fA-F]{6}", context.design_markdown)
    assert len(colors) >= 3, (
        f"Solo {len(colors)} colores HEX encontrados — se esperan ≥3"
    )


@pytest.mark.slow
async def test_design_md_tiene_secciones_markdown():
    """DESIGN.md generado incluye secciones Markdown (## headings)."""
    context = DesignContext(
        design_brief="Plataforma de e-learning para universitarios. Moderno, accesible.",
        project_type="app",
    )
    context = await analyze_and_design(context)

    assert context.design_markdown
    headings = re.findall(r"^##\s+\w+", context.design_markdown, re.MULTILINE)
    assert len(headings) >= 2, (
        f"Solo {len(headings)} secciones ## — se esperan ≥2"
    )
