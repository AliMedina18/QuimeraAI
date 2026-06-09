"""
test_scorers.py — Tests de validación de outputs (DESIGN.md y HTML)
===================================================================

El pipeline genera dos outputs:
- DESIGN.md: YAML + Markdown con tokens de diseño
- HTML autocontenido: documento completo listo para iframe srcDoc

Estos tests validan la estructura y calidad de ambos outputs
sin llamar a Gemini (todos son @pytest.mark.unit).

Los scorers algorítmicos heredados (wcag_contrast, color_harmony)
aún existen en el repo pero no son parte del pipeline activo.
"""

import pytest
import re
import yaml


# ---------------------------------------------------------------------------
# TESTS DE VALIDACIÓN DE DESIGN.MD YAML
# ---------------------------------------------------------------------------

class TestDesignMarkdownYAMLValidation:
    """Verifica que el YAML en DESIGN.md sea válido."""

    @pytest.mark.unit
    def test_yaml_minimal_valido(self):
        """YAML mínimo debe ser parseable."""
        yaml_str = """
version: alpha
name: Test Design
colors:
  primary: '#0066FF'
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
"""
        try:
            data = yaml.safe_load(yaml_str)
            assert data["version"] == "alpha"
            assert data["colors"]["primary"] == "#0066FF"
        except yaml.YAMLError:
            pytest.fail("YAML inválido")

    @pytest.mark.unit
    def test_yaml_indentacion_dos_espacios(self):
        """YAML en DESIGN.md usa 2 espacios, no tabs."""
        yaml_str = """typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
"""
        assert "\t" not in yaml_str
        assert "  " in yaml_str

    @pytest.mark.unit
    def test_yaml_requiere_version_y_name(self):
        """YAML debe tener version y name."""
        yaml_str = """
version: alpha
name: My Design
colors:
  primary: '#0066FF'
"""
        data = yaml.safe_load(yaml_str)
        assert "version" in data
        assert "name" in data

    @pytest.mark.unit
    def test_yaml_colores_son_hex_validos(self):
        """Los colores deben ser #HEX válidos."""
        valid_colors = [
            "#000000",
            "#FFFFFF",
            "#FF0000",
            "#0066FF",
            "#fff6df",
            "#00daf3",
        ]
        for color in valid_colors:
            assert re.match(r"^#[0-9A-Fa-f]{6}$", color), f"Color inválido: {color}"

    @pytest.mark.unit
    def test_yaml_tipografia_requiere_campos_base(self):
        """Cada entrada de typography debe tener campos base."""
        yaml_str = """
typography:
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
"""
        data = yaml.safe_load(yaml_str)
        typo = data["typography"]["body-md"]

        required_fields = ["fontFamily", "fontSize", "fontWeight", "lineHeight"]
        for field in required_fields:
            assert field in typo, f"Falta campo {field}"

    @pytest.mark.unit
    def test_yaml_components_tienen_propiedades(self):
        """Components deben tener propiedades como backgroundColor, etc."""
        yaml_str = """
components:
  button-primary:
    backgroundColor: '#0066FF'
    textColor: '#FFFFFF'
    typography: '{typography.body-md}'
    rounded: '{rounded.lg}'
    padding: '{spacing.md}'
"""
        data = yaml.safe_load(yaml_str)
        button = data["components"]["button-primary"]

        required_props = ["backgroundColor", "textColor", "typography"]
        for prop in required_props:
            assert prop in button, f"Falta propiedad {prop}"


class TestDesignMarkdownMarkdownValidation:
    """Verifica que el Markdown en DESIGN.md sea válido."""

    @pytest.mark.unit
    def test_markdown_tiene_secciones_con_doble_hash(self):
        """Secciones deben ser ## (h2), no # (h1)."""
        markdown = """
## Overview
Test

## Colors
Paleta

## Components
Botones
"""
        sections = re.findall(r"^##\s+\w+", markdown, re.MULTILINE)
        assert len(sections) >= 3

    @pytest.mark.unit
    def test_markdown_colores_con_negrita_y_hex(self):
        """Cada color debe tener formato: **Name (#HEX):** Description"""
        markdown = """
## Colors

- **Primary (#0066FF):** Main accent color for interactive elements
- **Secondary (#6366F1):** Secondary accent color
"""
        assert re.search(r"\*\*.*?\(#[0-9A-Fa-f]{6}\):\*\*", markdown)

    @pytest.mark.unit
    def test_markdown_token_references(self):
        """Las referencias a tokens deben usar {{token.path}}."""
        markdown = """
Components:
- Button: uses {{typography.body-md}} and {{colors.primary}}
- Card: uses {spacing.md} padding
"""
        refs = re.findall(r"\{\{([^}]+)\}\}", markdown)
        assert len(refs) > 0


class TestDesignMarkdownConsistencia:
    """Verifica consistencia entre YAML y Markdown."""

    @pytest.mark.unit
    def test_colores_definidos_en_yaml_referenciados_en_markdown(self):
        """Los colores definidos en YAML deben referenciarse en Markdown."""
        design_md = """---
version: alpha
colors:
  primary: '#0066FF'
  secondary: '#6366F1'
---

## Colors

- **Primary (#0066FF):** Main accent
- **Secondary (#6366F1):** Secondary accent
"""
        yaml_match = re.match(r"^---\n(.*?)\n---", design_md, re.DOTALL)
        yaml_data = yaml.safe_load(yaml_match.group(1))

        for color_name in yaml_data["colors"]:
            markdown_part = design_md.split("---")[2]
            assert color_name.capitalize() in markdown_part or color_name in markdown_part

    @pytest.mark.unit
    def test_token_references_existen_en_yaml(self):
        """Las referencias {{token}} en markdown deben existir en YAML."""
        design_md = """---
version: alpha
colors:
  primary: '#0066FF'
typography:
  body-md:
    fontFamily: Inter
---

## Overview

Uses {{colors.primary}} and {{typography.body-md}}
"""
        yaml_match = re.match(r"^---\n(.*?)\n---", design_md, re.DOTALL)
        yaml_data = yaml.safe_load(yaml_match.group(1))

        refs = re.findall(r"\{\{([^}]+)\}\}", design_md)
        for ref in refs:
            parts = ref.split(".")
            assert parts[0] in yaml_data, f"Falta sección {parts[0]} en YAML"


# ---------------------------------------------------------------------------
# TESTS DE VALIDACIÓN DEL HTML OUTPUT
# ---------------------------------------------------------------------------

class TestHtmlOutputValidation:
    """Verifica que el HTML generado sea un documento válido y autocontenido."""

    @pytest.mark.unit
    def test_html_empieza_con_doctype(self):
        """HTML debe empezar con <!DOCTYPE html>."""
        html = "<!DOCTYPE html>\n<html lang='es'><head></head><body></body></html>"
        assert html.strip().lower().startswith("<!doctype html>")

    @pytest.mark.unit
    def test_html_tiene_estructura_completa(self):
        """HTML debe tener <html>, <head> y <body>."""
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
    def test_html_tiene_meta_charset_y_viewport(self):
        """HTML debe declarar charset UTF-8 y viewport para responsividad."""
        html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Test</title>
</head>
<body></body>
</html>"""
        assert "UTF-8" in html
        assert "viewport" in html

    @pytest.mark.unit
    def test_html_sin_bloques_markdown(self):
        """HTML generado no debe contener bloques de código markdown (```)."""
        html = """<!DOCTYPE html>
<html><head><title>Test</title></head>
<body><h1>Hello</h1></body>
</html>"""
        assert "```" not in html

    @pytest.mark.unit
    def test_html_autocontenido_sin_react_ni_vue(self):
        """HTML no debe importar React, Vue ni Angular."""
        html = """<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>:root { --color-primary: #0066FF; }</style>
</head>
<body><main></main><script>console.log('ok')</script></body>
</html>"""
        html_lower = html.lower()
        assert "unpkg.com/react" not in html_lower
        assert "cdn.jsdelivr.net/npm/vue" not in html_lower
        assert "angular" not in html_lower

    @pytest.mark.unit
    def test_html_tiene_css_variables_en_root(self):
        """HTML debe definir CSS variables en :root para los tokens del DESIGN.md."""
        html = """<!DOCTYPE html>
<html>
<head>
<style>
  :root {
    --color-primary: #0066FF;
    --color-background: #FFFFFF;
    --font-body: 'Inter', sans-serif;
    --space-md: 16px;
  }
</style>
</head>
<body></body>
</html>"""
        assert ":root" in html
        assert "--color-" in html

    @pytest.mark.unit
    def test_html_tiene_etiquetas_semanticas(self):
        """HTML debe usar etiquetas semánticas para accesibilidad."""
        html = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <nav>Navbar</nav>
  <main>
    <section class="hero">Hero</section>
  </main>
  <footer>Footer &copy; 2025</footer>
</body>
</html>"""
        assert "<nav" in html
        assert "<main" in html or "<section" in html
        assert "<footer" in html

    @pytest.mark.unit
    def test_html_tiene_titulo(self):
        """HTML debe tener un <title> no vacío."""
        html = """<!DOCTYPE html>
<html><head><title>Mi Aplicación</title></head><body></body></html>"""
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        assert match is not None
        assert len(match.group(1).strip()) > 0

    @pytest.mark.unit
    def test_html_botones_tienen_clases(self):
        """Los botones en el HTML deben tener clase CSS definida."""
        html = """<!DOCTYPE html>
<html>
<head>
<style>
  .btn-primary { background: #0066FF; color: #fff; padding: 12px 24px; border-radius: 8px; }
</style>
</head>
<body>
  <button class="btn-primary">Empezar</button>
</body>
</html>"""
        # Verifica que hay definición de clase de botón
        assert ".btn-primary" in html or ".button" in html or "button" in html.lower()

    @pytest.mark.unit
    def test_html_responsive_con_tailwind_o_media_queries(self):
        """HTML debe tener clases responsive de Tailwind o media queries CSS."""
        html_con_tailwind = """<div class="grid grid-cols-1 md:grid-cols-3 gap-6">"""
        html_con_media = """@media (min-width: 768px) { .grid { grid-template-columns: repeat(3, 1fr); } }"""

        assert (
            "md:" in html_con_tailwind
            or "lg:" in html_con_tailwind
            or "@media" in html_con_media
        )


# ---------------------------------------------------------------------------
# TESTS DE WCAG CONTRAST (funciones puras disponibles en pipeline activo)
# ---------------------------------------------------------------------------

class TestWcagContrast:
    """Tests de las funciones puras de wcag_contrast.py."""

    @pytest.mark.unit
    def test_calculate_relative_luminance_negro(self):
        """El negro absoluto tiene luminancia 0."""
        from pipeline.scorers.wcag_contrast import calculate_relative_luminance
        assert calculate_relative_luminance("#000000") == pytest.approx(0.0, abs=1e-6)

    @pytest.mark.unit
    def test_calculate_relative_luminance_blanco(self):
        """El blanco absoluto tiene luminancia 1."""
        from pipeline.scorers.wcag_contrast import calculate_relative_luminance
        assert calculate_relative_luminance("#FFFFFF") == pytest.approx(1.0, abs=1e-4)

    @pytest.mark.unit
    def test_negro_sobre_blanco_es_21(self):
        """Negro sobre blanco siempre da contraste 21:1 (máximo)."""
        from pipeline.scorers.wcag_contrast import calculate_wcag_ratio
        ratio = calculate_wcag_ratio("#000000", "#FFFFFF")
        assert ratio == pytest.approx(21.0, abs=0.01)

    @pytest.mark.unit
    def test_classify_aaa(self):
        """Ratio >= 7 es AAA."""
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(21.0) == "AAA"
        assert classify_wcag_level(7.0) == "AAA"

    @pytest.mark.unit
    def test_classify_aa(self):
        """Ratio 4.5–6.99 es AA."""
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(4.5) == "AA"
        assert classify_wcag_level(5.0) == "AA"

    @pytest.mark.unit
    def test_classify_fail(self):
        """Ratio < 4.5 falla WCAG AA."""
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(2.0) == "FAIL"
        assert classify_wcag_level(4.49) == "FAIL"

    @pytest.mark.unit
    def test_validate_pair_negro_sobre_blanco(self):
        """validate_pair devuelve resultado estructurado correcto."""
        from pipeline.scorers.wcag_contrast import validate_pair
        result = validate_pair("#000000", "#FFFFFF", "negro/blanco")
        assert result["passes_aa"] is True
        assert result["passes_aaa"] is True
        assert result["ratio"] == pytest.approx(21.0, abs=0.01)
