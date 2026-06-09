"""
test_v3_services.py - Tests unitarios de servicios de soporte

Verifica que los servicios de soporte del pipeline v3 se inicializan
correctamente y responden a llamadas basicas.

Marker: @pytest.mark.unit (sin llamadas a Gemini - no requiere credenciales)
"""
import pytest

from models import DesignContext, TemplatePattern, TemplateAnalysisContext
from services.color_science import get_color_science
from services.typography_analyzer import get_typography_analyzer
from services.template_analyzer import get_template_analyzer


class TestColorScience:
    """Tests del servicio ColorScience."""

    @pytest.mark.unit
    def test_wcag_contrast_blanco_negro(self):
        """Contraste blanco sobre negro debe ser ~21:1 (maximo WCAG)."""
        cs = get_color_science()
        ratio = cs.wcag_contrast_ratio("#ffffff", "#000000")
        assert abs(ratio - 21.0) < 0.1, f"Contraste esperado ~21:1, obtenido {ratio}"

    @pytest.mark.unit
    def test_wcag_contrast_es_simetrico(self):
        """El ratio de contraste es simetrico (fg/bg = bg/fg)."""
        cs = get_color_science()
        ratio_ab = cs.wcag_contrast_ratio("#ffffff", "#000000")
        ratio_ba = cs.wcag_contrast_ratio("#000000", "#ffffff")
        assert abs(ratio_ab - ratio_ba) < 0.01

    @pytest.mark.unit
    def test_hex_a_rgb_blanco(self):
        """#FFFFFF convierte a (255, 255, 255)."""
        cs = get_color_science()
        r, g, b = cs.hex_to_rgb("#FFFFFF")
        assert (r, g, b) == (255, 255, 255)

    @pytest.mark.unit
    def test_hex_a_rgb_negro(self):
        """#000000 convierte a (0, 0, 0)."""
        cs = get_color_science()
        r, g, b = cs.hex_to_rgb("#000000")
        assert (r, g, b) == (0, 0, 0)


class TestTypographyAnalyzer:
    """Tests del servicio TypographyAnalyzer."""

    @pytest.mark.unit
    def test_recommend_pairing_retorna_dict(self):
        """recommend_pairing() retorna un diccionario con clave 'pairing'."""
        ta = get_typography_analyzer()
        rec = ta.recommend_pairing("fintech")
        assert isinstance(rec, dict), "recommend_pairing debe retornar dict"
        assert "pairing" in rec, "Falta clave 'pairing' en resultado"

    @pytest.mark.unit
    def test_recommend_pairing_industrias_comunes(self):
        """recommend_pairing() funciona para las industrias principales."""
        ta = get_typography_analyzer()
        for industry in ("saas", "marketplace", "wellness", "fintech"):
            result = ta.recommend_pairing(industry)
            assert result is not None, f"Sin resultado para industria '{industry}'"


class TestDesignContextModel:
    """Tests del modelo DesignContext."""

    @pytest.mark.unit
    def test_crear_contexto_minimo(self):
        """DesignContext se crea correctamente con solo design_brief."""
        context = DesignContext(design_brief="Test brief de al menos 10 caracteres")
        assert context.design_brief == "Test brief de al menos 10 caracteres"
        assert context.project_type is None
        assert context.design_reference is None
        assert context.template_analysis is None
        assert context.design_markdown is None
        assert context.html_output is None

    @pytest.mark.unit
    def test_crear_contexto_con_campos_opcionales(self):
        """DesignContext acepta campos opcionales."""
        context = DesignContext(
            design_brief="Descripcion del proyecto",
            project_type="landing_page",
            design_reference="stripe",
        )
        assert context.project_type == "landing_page"
        assert context.design_reference == "stripe"

    @pytest.mark.unit
    def test_contexto_es_mutable(self):
        """Los campos opcionales de DesignContext se pueden asignar despues de crear."""
        context = DesignContext(design_brief="Proyecto de prueba")
        context.design_markdown = "# Test\nContenido"
        context.html_output = "<!DOCTYPE html><html></html>"
        assert context.design_markdown.startswith("# Test")
        assert "DOCTYPE" in context.html_output
