"""
test_demo.py — Test de integración del pipeline completo
=========================================================

Prueba end-to-end: brief → DESIGN.md → HTML.

Marker: @pytest.mark.slow (llama a Gemini — requiere GOOGLE_API_KEY)
"""
import pytest

from models import DesignContext
from pipeline.step1_analyze import analyze_and_design
from pipeline.step3_generate import generate_code


@pytest.mark.slow
async def test_pipeline_restaurante_genera_html_valido():
    """Pipeline completo para un brief de restaurante produce HTML estructuralmente válido."""
    context = DesignContext(
        design_brief=(
            "Sakura Sushi — Restaurante premium de sushi en Madrid. "
            "Sitio web con: presentación, menú de especialidades, galería, "
            "reservas en línea, ubicación y contacto. Ambiente elegante y moderno."
        ),
        project_type="landing_page",
        design_reference="stripe",
    )

    # Paso 1: DESIGN.md
    context = await analyze_and_design(context)
    assert context.design_markdown, "DESIGN.md no fue generado"
    assert len(context.design_markdown) > 200, "DESIGN.md demasiado corto"
    assert "---" in context.design_markdown, "Falta frontmatter YAML"

    # Paso 3: HTML
    context = await generate_code(context)
    assert context.html_output, "HTML no fue generado"

    html = context.html_output
    assert "<!doctype html>" in html.lower(), "Falta DOCTYPE"
    assert "</html>" in html.lower(), "Falta cierre </html>"
    assert "<style" in html or "<link" in html, "Falta CSS"
    assert "<nav" in html or "<header" in html, "Falta navbar/header"
    assert "<footer" in html or "<main" in html, "Falta footer/main"
    assert "```" not in html, "HTML contiene bloques markdown sin parsear"
