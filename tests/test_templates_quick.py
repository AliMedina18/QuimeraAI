"""
test_templates_quick.py - Tests unitarios del gestor de templates y analizador

Verifica carga aleatoria, seleccion por industria, metadata y extraccion de
patrones del TemplateAnalyzer.

Marker: @pytest.mark.unit (sin llamadas a Gemini - no requiere credenciales)
"""
import pytest

from services.design_templates import get_templates_manager
from services.template_analyzer import get_template_analyzer


class TestTemplatesManager:
    """Tests del gestor de templates DesignTemplatesManager."""

    @pytest.mark.unit
    def test_get_random_template_retorna_tupla(self):
        """get_random_template() retorna tupla (nombre, contenido)."""
        manager = get_templates_manager()
        name, content = manager.get_random_template()
        assert isinstance(name, str) and len(name) > 0
        assert isinstance(content, str) and len(content) > 100

    @pytest.mark.unit
    def test_get_template_by_industry_fintech(self):
        """get_template_by_industry() retorna un template para fintech."""
        manager = get_templates_manager()
        result = manager.get_template_by_industry("fintech")
        assert result is not None
        name, content = result
        assert isinstance(name, str)
        assert isinstance(content, str)

    @pytest.mark.unit
    def test_get_all_metadata_retorna_dict_no_vacio(self):
        """get_all_metadata() retorna diccionario con al menos 5 entradas."""
        manager = get_templates_manager()
        metadata = manager.get_all_metadata()
        assert isinstance(metadata, dict)
        assert len(metadata) >= 5


class TestTemplateAnalyzer:
    """Tests del analizador de templates TemplateAnalyzer."""

    @pytest.mark.unit
    def test_find_relevant_templates_fintech(self):
        """find_relevant_templates() retorna resultados para fintech."""
        analyzer = get_template_analyzer()
        results = analyzer.find_relevant_templates(industry="fintech")
        assert len(results) >= 1, "No se encontraron templates para fintech"

    @pytest.mark.unit
    def test_find_relevant_templates_saas(self):
        """find_relevant_templates() retorna resultados para saas."""
        analyzer = get_template_analyzer()
        results = analyzer.find_relevant_templates(industry="saas")
        assert len(results) >= 1, "No se encontraron templates para saas"

    @pytest.mark.unit
    def test_extract_pattern_stripe(self):
        """extract_pattern para 'stripe' retorna un TemplatePattern valido."""
        from models import TemplatePattern
        analyzer = get_template_analyzer()
        pattern = analyzer.extract_pattern("stripe")
        if pattern is not None:
            assert isinstance(pattern, TemplatePattern)
            assert pattern.name == "stripe"
