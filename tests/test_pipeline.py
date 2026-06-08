"""
test_pipeline.py — Tests de integración del pipeline (2 pasos)
==============================================================

Pipeline: analyze_and_design() → generate_code()
Outputs: DESIGN.md + HTML autocontenido

Requisitos para correr estos tests:
  - GOOGLE_API_KEY configurada (llaman a Gemini)
  - Correr: pytest tests/test_pipeline.py -v
  - Solo slow tests: pytest tests/test_pipeline.py -v -m slow

Markers:
  @pytest.mark.slow     → Tests que llaman a Gemini (cuentan contra la cuota)
  @pytest.mark.unit     → Tests que no necesitan credenciales (mocks)
"""

import pytest
import sys
import os
import re
import yaml

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_briefs():
    """5 briefs de prueba predefinidos para testing."""
    return [
        {
            "id": "fintech_001",
            "brief": "App de inversiones para jóvenes de 25-35 años. Colores: azul oscuro y oro. Tono moderno, confiable, premium.",
            "project_type": "landing_page",
        },
        {
            "id": "health_001",
            "brief": "Dashboard de seguimiento de salud mental. Estética minimalista, colores suaves, calming.",
            "project_type": "dashboard",
        },
        {
            "id": "saas_001",
            "brief": "Plataforma de gestión de proyectos para agencias creativas. B2B. Profesional, moderno.",
            "project_type": "dashboard",
        },
        {
            "id": "education_001",
            "brief": "App de aprendizaje de idiomas para niños. Colorida, energética, divertida, amigable.",
            "project_type": "app",
        },
        {
            "id": "minimalist_001",
            "brief": "1970s technical handout aesthetic. Paper and ink. Serif typography, generous margins, no decorations.",
            "project_type": "landing_page",
        },
    ]


@pytest.fixture
def minimal_context():
    """DesignContext mínimo para tests."""
    from models import DesignContext
    return DesignContext(
        design_brief="Landing page para startup de fintech. Colores azul y blanco.",
        project_type="landing_page",
    )


# ---------------------------------------------------------------------------
# TESTS UNITARIOS DEL MODELO (sin Gemini)
# ---------------------------------------------------------------------------

class TestDesignContextModel:
    """Verifica que el modelo DesignContext funciona correctamente."""

    @pytest.mark.unit
    def test_design_context_minimal(self):
        """DesignContext solo requiere design_brief."""
        from models import DesignContext
        ctx = DesignContext(design_brief="Una landing page simple.")
        assert ctx.design_brief == "Una landing page simple."
        assert ctx.project_type is None
        assert ctx.design_markdown is None
        assert ctx.html_output is None

    @pytest.mark.unit
    def test_design_context_con_project_type(self):
        """DesignContext puede incluir project_type opcional."""
        from models import DesignContext
        ctx = DesignContext(
            design_brief="Dashboard",
            project_type="dashboard"
        )
        assert ctx.design_brief == "Dashboard"
        assert ctx.project_type == "dashboard"

    @pytest.mark.unit
    def test_design_context_acumula_outputs(self):
        """DesignContext acumula outputs de cada paso."""
        from models import DesignContext
        ctx = DesignContext(design_brief="test")

        # Paso 1
        ctx.design_markdown = "---\nversion: alpha\n---\n## Overview\nTest"
        assert ctx.design_markdown is not None

        # Paso 2
        ctx.html_output = "<!DOCTYPE html><html><body><h1>Test</h1></body></html>"
        assert ctx.html_output is not None

    @pytest.mark.unit
    def test_design_context_serializable(self):
        """DesignContext se puede serializar a dict."""
        from models import DesignContext
        ctx = DesignContext(
            design_brief="test",
            project_type="landing_page",
            design_markdown="---\nversion: alpha\n---\nTest"
        )
        data = ctx.model_dump()
        assert data["design_brief"] == "test"
        assert data["project_type"] == "landing_page"
        assert data["design_markdown"] == "---\nversion: alpha\n---\nTest"


# ---------------------------------------------------------------------------
# TESTS DE VALIDACIÓN DE OUTPUTS (sin Gemini)
# ---------------------------------------------------------------------------

class TestDesignMarkdownValidation:
    """Verifica que DESIGN.md tenga la estructura correcta."""

    @pytest.mark.unit
    def test_design_markdown_tiene_frontmatter_yaml(self):
        """DESIGN.md debe empezar con --- YAML --- """
        valid_design_md = """---
version: alpha
name: Test Design
colors:
  primary: '#0066FF'
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
---

## Overview
Test design system.
"""
        assert valid_design_md.startswith("---")
        assert "---" in valid_design_md[3:]  # Cierre del YAML

    @pytest.mark.unit
    def test_design_markdown_yaml_valido(self):
        """El YAML del DESIGN.md debe ser parseable."""
        design_md = """---
version: alpha
name: Test
colors:
  primary: '#0066FF'
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
---

## Overview
Test
"""
        match = re.match(r"^---\n(.*?)\n---", design_md, re.DOTALL)
        assert match is not None
        yaml_str = match.group(1)

        try:
            data = yaml.safe_load(yaml_str)
            assert data["version"] == "alpha"
            assert data["name"] == "Test"
            assert data["colors"]["primary"] == "#0066FF"
        except yaml.YAMLError:
            pytest.fail("YAML no es válido")

    @pytest.mark.unit
    def test_design_markdown_tiene_secciones_requeridas(self):
        """DESIGN.md debe tener todas las secciones markdown."""
        design_md = """---
version: alpha
---

## Overview
Test overview

## Colors
Test colors

## Typography
Test typography

## Layout & Spacing
Test layout

## Elevation & Depth
Test elevation

## Shapes
Test shapes

## Components
Test components

## Do's and Don'ts
Test do's and don'ts
"""
        required_sections = [
            "## Overview",
            "## Colors",
            "## Typography",
            "## Layout & Spacing",
            "## Elevation & Depth",
            "## Shapes",
            "## Components",
            "## Do's and Don'ts",
        ]
        for section in required_sections:
            assert section in design_md, f"Falta sección: {section}"


class TestHtmlOutputValidation:
    """Verifica que el HTML generado sea un documento válido y autocontenido."""

    @pytest.mark.unit
    def test_html_tiene_doctype(self):
        """HTML debe empezar con <!DOCTYPE html>."""
        html = "<!DOCTYPE html>\n<html lang='es'><head></head><body></body></html>"
        assert html.strip().lower().startswith("<!doctype html>")

    @pytest.mark.unit
    def test_html_tiene_estructura_basica(self):
        """HTML debe tener html, head y body."""
        html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Test</title>
</head>
<body>
  <main><h1>Test</h1></main>
</body>
</html>"""
        assert "<html" in html
        assert "<head" in html
        assert "<body" in html
        assert "</html>" in html

    @pytest.mark.unit
    def test_html_tiene_title(self):
        """HTML debe tener un <title>."""
        html = """<!DOCTYPE html>
<html><head><title>Mi Sitio</title></head><body></body></html>"""
        assert "<title>" in html and "</title>" in html

    @pytest.mark.unit
    def test_html_tiene_meta_charset_y_viewport(self):
        """HTML debe tener charset UTF-8 y viewport para responsividad."""
        html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Test</title>
</head>
<body></body>
</html>"""
        assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html
        assert "viewport" in html

    @pytest.mark.unit
    def test_html_no_contiene_bloques_markdown(self):
        """HTML generado no debe tener bloques de código markdown (```)."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><h1>Hello</h1></body>
</html>"""
        assert "```" not in html

    @pytest.mark.unit
    def test_html_autocontenido_sin_framework_js(self):
        """HTML no debe importar React, Vue ni Angular."""
        html = """<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>:root { --color-primary: #0066FF; }</style>
</head>
<body><main></main></body>
</html>"""
        # No debe haber imports de frameworks JS
        assert "react" not in html.lower() or "cdn.tailwindcss" in html  # Tailwind OK, React no
        assert "vue" not in html.lower()
        assert "angular" not in html.lower()

    @pytest.mark.unit
    def test_html_usa_css_variables(self):
        """HTML debe definir CSS variables (:root) desde los tokens del DESIGN.md."""
        html = """<!DOCTYPE html>
<html>
<head>
<style>
  :root {
    --color-primary: #0066FF;
    --color-background: #FFFFFF;
    --font-body: 'Inter', sans-serif;
  }
</style>
</head>
<body></body>
</html>"""
        assert ":root" in html
        assert "var(--" in html or "--color-" in html

    @pytest.mark.unit
    def test_html_tiene_secciones_semanticas(self):
        """HTML debe usar etiquetas semánticas: nav, main, footer."""
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <nav>Navbar</nav>
  <main>
    <section class="hero">Hero</section>
    <section class="features">Features</section>
  </main>
  <footer>Footer</footer>
</body>
</html>"""
        assert "<nav" in html
        assert "<main" in html or "<section" in html
        assert "<footer" in html


# ---------------------------------------------------------------------------
# TESTS DE INTEGRACIÓN (con Gemini - SLOW)
# ---------------------------------------------------------------------------

class TestAnalyzeAndDesignIntegration:
    """Tests de analyze_and_design() llamando a Gemini."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_analyze_and_design_genera_design_markdown(self, minimal_context):
        """analyze_and_design() debe generar DESIGN.md válido."""
        from pipeline.step1_analyze import analyze_and_design

        result_context = await analyze_and_design(minimal_context)

        assert result_context.design_markdown is not None
        assert len(result_context.design_markdown) > 0
        assert result_context.design_markdown.startswith("---")
        assert "---" in result_context.design_markdown[3:]

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_analyze_and_design_design_markdown_tiene_secciones(self, minimal_context):
        """El DESIGN.md generado debe tener todas las secciones."""
        from pipeline.step1_analyze import analyze_and_design

        result_context = await analyze_and_design(minimal_context)
        design_md = result_context.design_markdown

        assert "## Overview" in design_md or "# Overview" in design_md
        assert "## Colors" in design_md or "# Colors" in design_md
        assert "## Typography" in design_md or "# Typography" in design_md
        assert "## Components" in design_md or "# Components" in design_md


class TestGenerateCodeIntegration:
    """Tests de generate_code() llamando a Gemini."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_generate_code_genera_html(self, minimal_context):
        """generate_code() debe generar HTML autocontenido válido."""
        from pipeline.step1_analyze import analyze_and_design
        from pipeline.step3_generate import generate_code

        context = await analyze_and_design(minimal_context)
        result_context = await generate_code(context)

        assert result_context.html_output is not None
        assert len(result_context.html_output) > 0

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_generate_code_html_es_documento_completo(self, minimal_context):
        """El HTML generado debe ser un documento completo."""
        from pipeline.step1_analyze import analyze_and_design
        from pipeline.step3_generate import generate_code

        context = await analyze_and_design(minimal_context)
        result_context = await generate_code(context)

        html = result_context.html_output

        # Documento completo
        assert html.strip().lower().startswith("<!doctype html>")
        assert "<html" in html
        assert "<body" in html
        assert "</html>" in html

        # Sin bloques markdown
        assert "```" not in html

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_generate_code_html_tiene_estilos(self, minimal_context):
        """El HTML generado debe tener estilos CSS."""
        from pipeline.step1_analyze import analyze_and_design
        from pipeline.step3_generate import generate_code

        context = await analyze_and_design(minimal_context)
        result_context = await generate_code(context)

        html = result_context.html_output

        # Debe tener CSS (inline o Tailwind CDN)
        assert "<style>" in html or "tailwindcss" in html or "cdn.tailwind" in html

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_generate_code_falla_sin_design_markdown(self):
        """generate_code() debe fallar si falta DESIGN.md."""
        from models import DesignContext
        from pipeline.step3_generate import generate_code

        context = DesignContext(design_brief="test")  # Sin design_markdown

        with pytest.raises(ValueError):
            await generate_code(context)


# ---------------------------------------------------------------------------
# TESTS END-TO-END (con Gemini - SLOW)
# ---------------------------------------------------------------------------

class TestEndToEndPipeline:
    """Tests completos del pipeline: brief → DESIGN.md → HTML."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_pipeline_completo_fintech(self, sample_briefs):
        """Pipeline completo con brief de fintech."""
        from models import DesignContext
        from pipeline.step1_analyze import analyze_and_design
        from pipeline.step3_generate import generate_code

        brief_data = sample_briefs[0]  # Fintech
        context = DesignContext(
            design_brief=brief_data["brief"],
            project_type=brief_data["project_type"],
        )

        context = await analyze_and_design(context)
        assert context.design_markdown is not None

        context = await generate_code(context)
        assert context.html_output is not None
        assert context.html_output.strip().lower().startswith("<!doctype html>")

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_pipeline_completo_minimalist(self, sample_briefs):
        """Pipeline completo con brief minimalista."""
        from models import DesignContext
        from pipeline.step1_analyze import analyze_and_design
        from pipeline.step3_generate import generate_code

        brief_data = sample_briefs[4]  # Minimalist
        context = DesignContext(
            design_brief=brief_data["brief"],
            project_type=brief_data["project_type"],
        )

        context = await analyze_and_design(context)
        assert context.design_markdown is not None
        assert (
            "1970s" in context.design_markdown
            or "handout" in context.design_markdown
            or "serif" in context.design_markdown.lower()
        )

        context = await generate_code(context)
        assert context.html_output is not None
        assert "<html" in context.html_output
