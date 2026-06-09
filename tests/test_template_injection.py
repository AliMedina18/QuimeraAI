"""
test_template_injection.py — Tests unitarios del sistema de templates
=====================================================================

Verifica que los templates de diseño se cargan correctamente y tienen
la estructura YAML + Markdown esperada.

Marker: @pytest.mark.unit (sin llamadas a Gemini — no requiere credenciales)
"""
import re

import pytest

from services.design_templates import get_templates_manager


class TestTemplateLoading:
    """Tests de carga y disponibilidad de templates."""

    @pytest.mark.unit
    def test_carga_templates_al_iniciar(self):
        """El manager carga al menos 10 templates al arrancar."""
        manager = get_templates_manager()
        templates = manager.list_available()
        assert len(templates) >= 10, (
            f"Solo {len(templates)} templates cargados — se esperan ≥10"
        )

    @pytest.mark.unit
    def test_templates_conocidos_disponibles(self):
        """Templates populares conocidos deben estar disponibles."""
        manager = get_templates_manager()
        available = set(manager.list_available())
        for name in ("stripe", "airbnb", "figma"):
            assert name in available, f"Template '{name}' no encontrado"

    @pytest.mark.unit
    def test_get_template_retorna_contenido_no_vacio(self):
        """get_template() retorna contenido de texto no vacío."""
        manager = get_templates_manager()
        content = manager.get_template("stripe")
        assert content, "Template 'stripe' retornó vacío"
        assert len(content) > 100, "Template 'stripe' demasiado corto"

    @pytest.mark.unit
    def test_get_template_inexistente_retorna_none(self):
        """get_template() retorna None para un nombre que no existe."""
        manager = get_templates_manager()
        assert manager.get_template("este-template-no-existe") is None

    @pytest.mark.unit
    def test_lista_ordenada_alfabeticamente(self):
        """list_available() retorna lista ordenada."""
        manager = get_templates_manager()
        templates = manager.list_available()
        assert templates == sorted(templates), "Templates no están ordenados"


class TestTemplateStructure:
    """Tests de estructura interna de los templates."""

    @pytest.mark.unit
    def test_template_tiene_yaml_frontmatter(self):
        """El template de Stripe comienza con delimitador YAML ---."""
        manager = get_templates_manager()
        content = manager.get_template("stripe")
        assert content is not None
        lines = content.strip().split("\n")
        assert lines[0] == "---", "El template no comienza con '---'"

    @pytest.mark.unit
    def test_template_tiene_colores_hex(self):
        """El template de Figma contiene colores HEX válidos."""
        manager = get_templates_manager()
        content = manager.get_template("figma")
        assert content is not None
        colors = re.findall(r"#[0-9a-fA-F]{6}", content)
        assert len(colors) >= 3, (
            f"Solo {len(colors)} colores HEX en 'figma' — se esperan ≥3"
        )

    @pytest.mark.unit
    def test_template_tiene_secciones_markdown(self):
        """El template de Airbnb contiene secciones Markdown (##)."""
        manager = get_templates_manager()
        content = manager.get_template("airbnb")
        assert content is not None
        headings = re.findall(r"^##\s+\w+", content, re.MULTILINE)
        assert len(headings) >= 2, (
            f"Solo {len(headings)} secciones ## en 'airbnb' — se esperan ≥2"
        )

    @pytest.mark.unit
    def test_metadata_retorna_campos_esperados(self):
        """get_template_metadata() retorna dict con campos name, colors, file."""
        manager = get_templates_manager()
        meta = manager.get_template_metadata("stripe")
        assert meta is not None
        for campo in ("name", "colors", "file"):
            assert campo in meta, f"Falta campo '{campo}' en metadata"
        assert meta["file"] == "stripe"
