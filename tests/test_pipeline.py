"""
test_pipeline.py — Tests de integración del pipeline completo
=============================================================
Estos tests verifican que los 3 pasos del pipeline se encadenan correctamente.
A diferencia de los tests unitarios (test_scorers.py), aquí probamos el flujo
completo: brief → análisis → evaluación → generación.

Requisitos para correr estos tests:
  - GOOGLE_API_KEY configurada (llaman a Gemini)
  - Correr: pytest tests/test_pipeline.py -v -m "not slow"

Markers:
  @pytest.mark.slow     → Tests que llaman a Gemini (cuentan contra la cuota)
  @pytest.mark.unit     → Tests que no necesitan credenciales

Estado por días:
  Día 1: Tests definidos, todos SKIPPED o con mocks mínimos
  Día 4: Tests completos de integración
  Día 6: Tests con matriz de confusión
"""

import pytest
import sys
import os
import asyncio

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_briefs():
    """
    10 briefs de prueba predefinidos con ground truth de diseñador humano.
    Ver Sección 9.3 del plan maestro.
    """
    return [
        {
            "id": "fintech_001",
            "brief": "App de inversiones para jóvenes de 25-35 años. Colores: azul y verde. Tono moderno y confiable.",
            "expected_project_type": "landing_page",
            "expected_industry": "fintech",
            "human_verdict": "good",  # Un diseñador diría que es un buen brief
        },
        {
            "id": "health_001",
            "brief": "Dashboard de seguimiento de salud mental. Estética minimalista, colores suaves.",
            "expected_project_type": "dashboard",
            "expected_industry": "healthtech",
            "human_verdict": "good",
        },
        {
            "id": "ecommerce_001",
            "brief": "Tienda de moda sostenible. Paleta: colores tierra, beis y verde oliva.",
            "expected_project_type": "landing_page",
            "expected_industry": "e-commerce",
            "human_verdict": "good",
        },
        {
            "id": "saas_001",
            "brief": "Plataforma de gestión de proyectos para agencias creativas. B2B. Profesional.",
            "expected_project_type": "dashboard",
            "expected_industry": "saas",
            "human_verdict": "good",
        },
        {
            "id": "education_001",
            "brief": "App de aprendizaje de idiomas para niños. Colorida, energética, divertida.",
            "expected_project_type": "app",
            "expected_industry": "educación",
            "human_verdict": "good",
        },
    ]


@pytest.fixture
def minimal_context():
    """DesignContext mínimo para tests que no necesitan Gemini."""
    from models import DesignContext
    return DesignContext(
        design_brief="Landing page para startup de fintech. Colores azul y blanco.",
        project_type="landing_page",
        industry="fintech",
        target_audience="Jóvenes de 25-35 años",
        brand_personality=["moderno", "confiable"],
        primary_color="#1E40AF",
        secondary_color="#3B82F6",
        accent_color="#F59E0B",
        neutral_palette=["#FFFFFF", "#F8FAFC", "#64748B", "#1E293B"],
        heading_font="Inter Bold",
        body_font="Inter",
        layout_type="landing_page",
        composition_rule="rule_of_thirds",
        color_harmony_type="complementario",
    )


# ---------------------------------------------------------------------------
# TESTS UNITARIOS DEL PIPELINE (sin Gemini)
# ---------------------------------------------------------------------------

class TestDesignContextModel:
    """Verifica que el modelo DesignContext funciona correctamente."""

    @pytest.mark.unit
    def test_design_context_crea_con_brief_minimo(self):
        """DesignContext solo requiere design_brief."""
        from models import DesignContext
        ctx = DesignContext(design_brief="Una landing page simple.")
        assert ctx.design_brief == "Una landing page simple."
        assert ctx.approved is False
        assert ctx.iteration == 0
        assert ctx.overall_score is None

    @pytest.mark.unit
    def test_design_context_iteration_incrementa(self):
        """El campo iteration se puede incrementar para el loop de corrección."""
        from models import DesignContext
        ctx = DesignContext(design_brief="test")
        ctx.iteration += 1
        assert ctx.iteration == 1

    @pytest.mark.unit
    def test_design_context_serializa_a_dict(self):
        """DesignContext se puede serializar para guardar en Firestore."""
        from models import DesignContext
        ctx = DesignContext(design_brief="test", primary_color="#FF0000")
        data = ctx.model_dump()
        assert data["design_brief"] == "test"
        assert data["primary_color"] == "#FF0000"
        assert data["approved"] is False


class TestLoopCorreccion:
    """Verifica la logica del loop de correccion sin llamar a Gemini."""

    @pytest.mark.unit
    def test_context_no_aprobado_cuando_score_bajo(self):
        """Si overall_score < 85, approved debe ser False."""
        from models import AestheticScores
        scores = AestheticScores(
            color_harmony=50, wcag_contrast=50, composition_balance=50,
            visual_hierarchy=50, gestalt_compliance=50, whitespace_quality=50,
            brand_consistency=50, accessibility=50,
        )
        assert scores.passed is False
        assert scores.overall_score < 85

    @pytest.mark.unit
    def test_critique_contiene_criterios_fallidos(self):
        """_generate_critique debe mencionar los criterios que fallaron."""
        from pipeline.step2_evaluate import _generate_critique
        from models import AestheticScores
        scores = AestheticScores(
            color_harmony=40, wcag_contrast=90, composition_balance=90,
            visual_hierarchy=90, gestalt_compliance=90, whitespace_quality=90,
            brand_consistency=90, accessibility=90,
        )
        critique = _generate_critique(scores, {"color_harmony": "Paleta sin armonia reconocible."})
        assert "color_harmony" in critique
        assert "40" in critique

    @pytest.mark.unit
    def test_iteration_incrementa_en_cada_ciclo(self):
        """El campo iteration debe incrementarse en cada evaluacion."""
        from models import DesignContext
        ctx = DesignContext(design_brief="test")
        assert ctx.iteration == 0
        ctx.iteration += 1
        assert ctx.iteration == 1
        ctx.iteration += 1
        assert ctx.iteration == 2

    @pytest.mark.unit
    def test_aprobado_cuando_overall_es_exactamente_85(self):
        """El umbral de aprobacion es >= 85, no > 85."""
        from models import AestheticScores
        scores = AestheticScores(
            color_harmony=85, wcag_contrast=85, composition_balance=85,
            visual_hierarchy=85, gestalt_compliance=85, whitespace_quality=85,
            brand_consistency=85, accessibility=85,
        )
        assert scores.passed is True
        assert scores.overall_score == 85.0


class TestAestheticScoresModel:
    """Verifica el modelo AestheticScores y sus propiedades calculadas."""

    @pytest.mark.unit
    def test_overall_score_es_promedio_de_8(self):
        """overall_score debe ser el promedio exacto de los 8 criterios."""
        from models import AestheticScores
        scores = AestheticScores(
            color_harmony=80,
            wcag_contrast=90,
            composition_balance=85,
            visual_hierarchy=75,
            gestalt_compliance=88,
            whitespace_quality=92,
            brand_consistency=70,
            accessibility=85,
        )
        expected = (80 + 90 + 85 + 75 + 88 + 92 + 70 + 85) / 8
        assert scores.overall_score == pytest.approx(expected, abs=0.01)

    @pytest.mark.unit
    def test_passed_cuando_overall_es_85_o_mas(self):
        """El diseño pasa cuando overall_score >= 85."""
        from models import AestheticScores
        scores = AestheticScores(
            color_harmony=85, wcag_contrast=85, composition_balance=85,
            visual_hierarchy=85, gestalt_compliance=85, whitespace_quality=85,
            brand_consistency=85, accessibility=85,
        )
        assert scores.passed is True

    @pytest.mark.unit
    def test_falla_cuando_overall_es_menos_de_85(self):
        """El diseño falla cuando overall_score < 85."""
        from models import AestheticScores
        scores = AestheticScores(
            color_harmony=60, wcag_contrast=60, composition_balance=60,
            visual_hierarchy=60, gestalt_compliance=60, whitespace_quality=60,
            brand_consistency=60, accessibility=60,
        )
        assert scores.passed is False

    @pytest.mark.unit
    def test_failing_criteria_retorna_los_que_estan_bajo_85(self):
        """failing_criteria() retorna solo los criterios por debajo de 85."""
        from models import AestheticScores
        scores = AestheticScores(
            color_harmony=90, wcag_contrast=40,  # wcag falla
            composition_balance=85, visual_hierarchy=88,
            gestalt_compliance=85, whitespace_quality=85,
            brand_consistency=85, accessibility=85,
        )
        failing = scores.failing_criteria()
        assert "wcag_contrast" in failing
        assert "color_harmony" not in failing


# ---------------------------------------------------------------------------
# TESTS DE INTEGRACIÓN (requieren Gemini — marcar como slow)
# ---------------------------------------------------------------------------

class TestPipelineIntegration:
    """Tests del pipeline completo. Requieren GOOGLE_API_KEY."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """
        El endpoint /health debe responder 200.
        TODO Día 1: este test debe pasar.
        """
        try:
            import fastapi
        except ImportError:
            pytest.skip("fastapi no instalado en sandbox")
        from httpx import AsyncClient
        from main import app
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_gemini_test_endpoint(self):
        """
        El endpoint /gemini-test debe llamar a Gemini y devolver una respuesta.
        TODO Día 1: este test debe pasar si GOOGLE_API_KEY está configurada.
        """
        pytest.skip("Requiere GOOGLE_API_KEY — correr manualmente")
        try:
            import fastapi
        except ImportError:
            pytest.skip("fastapi no instalado en sandbox")
        from httpx import AsyncClient
        from main import app
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/gemini-test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert len(data["gemini_response"]) > 0

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_loop_de_correccion_activa_con_score_bajo(self):
        """Pipeline completo: /evaluate ejecuta Paso1+Paso2 y retorna scores."""
        try:
            from httpx import AsyncClient
            from main import app
        except ImportError:
            pytest.skip("fastapi o httpx no instalado")
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/evaluate", json={
                "design_brief": "App de meditacion. Colores suaves. Minimalista.",
                "project_type": "app",
            })
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "approved" in data
        assert data["iterations_used"] >= 1

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_pipeline_completo_fintech(self):
        """Pipeline end-to-end con brief fintech via /evaluate."""
        try:
            from httpx import AsyncClient
            from main import app
        except ImportError:
            pytest.skip("fastapi o httpx no instalado")
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/evaluate", json={
                "design_brief": "Landing page para app de inversiones. Jovenes 25-35. Azul corporativo.",
                "project_type": "landing_page",
            })
        assert response.status_code == 200
        data = response.json()
        proposal = data.get("design_proposal", {})
        assert proposal.get("primary_color"), "Debe tener primary_color"
        assert proposal.get("heading_font"), "Debe tener heading_font"
        assert proposal.get("layout_type"), "Debe tener layout_type"
        assert data.get("overall_score") is not None


# ---------------------------------------------------------------------------
# TESTS UNITARIOS DEL PASO 3 (sin Gemini)
# ---------------------------------------------------------------------------

class TestStep3Generate:
    """Tests unitarios de step3_generate.py — no requieren Gemini."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_code_raises_si_no_aprobado(self):
        """generate_code debe lanzar ValueError si context.approved == False."""
        from models import DesignContext
        from pipeline.step3_generate import generate_code

        ctx = DesignContext(design_brief="test")
        assert ctx.approved is False
        with pytest.raises(ValueError, match="aprobados"):
            await generate_code(ctx)

    @pytest.mark.unit
    def test_parse_code_output_extrae_tres_secciones(self):
        """_parse_code_output debe extraer react_component, css y rationale."""
        from pipeline.step3_generate import _parse_code_output

        texto = (
            "===REACT_COMPONENT===\nimport React from 'react';\nexport default App;\n"
            "===DESIGN_TOKENS_CSS===\n:root { --color-primary: #000; }\n"
            "===RATIONALE===\n# Rationale\nDecision aqui.\n"
            "===END==="
        )
        result = _parse_code_output(texto)

        assert "import React" in result["react_component"]
        assert "--color-primary" in result["design_tokens_css"]
        assert "Rationale" in result["rationale_document"]

    @pytest.mark.unit
    def test_parse_code_output_secciones_vacias_si_no_hay_delimitadores(self):
        """Sin delimitadores, todas las secciones deben ser string vacio."""
        from pipeline.step3_generate import _parse_code_output

        result = _parse_code_output("texto sin delimitadores")
        assert result["react_component"] == ""
        assert result["design_tokens_css"] == ""
        assert result["rationale_document"] == ""

    @pytest.mark.unit
    def test_fallback_component_incluye_colores_del_context(self):
        """_get_fallback_component debe usar los colores del DesignContext."""
        from models import DesignContext
        from pipeline.step3_generate import _get_fallback_component

        ctx = DesignContext(
            design_brief="test",
            primary_color="#AA1122",
            accent_color="#BBCCDD",
            neutral_palette=["#FFFFFF", "#F0F0F0", "#888888", "#111111"],
            heading_font="Poppins Bold",
            body_font="Poppins",
        )
        component = _get_fallback_component(ctx)

        assert "#AA1122" in component
        assert "#BBCCDD" in component
        assert "Poppins" in component
        assert "export default" in component

    @pytest.mark.unit
    def test_fallback_tokens_incluye_todas_las_variables(self):
        """_get_fallback_tokens debe incluir todas las variables CSS requeridas."""
        from models import DesignContext
        from pipeline.step3_generate import _get_fallback_tokens

        ctx = DesignContext(
            design_brief="test",
            primary_color="#1E40AF",
            secondary_color="#3B82F6",
            accent_color="#F59E0B",
            neutral_palette=["#FFFFFF", "#F8FAFC", "#64748B", "#1E293B"],
            heading_font="Inter Bold",
            body_font="Inter",
        )
        tokens = _get_fallback_tokens(ctx)

        required = [
            "--color-primary", "--color-secondary", "--color-accent",
            "--font-heading", "--font-body",
            "--spacing-md", "--radius-md",
        ]
        for var in required:
            assert var in tokens, f"Falta variable: {var}"

    @pytest.mark.unit
    def test_basic_python_validation_acepta_componente_valido(self):
        """_basic_python_validation debe aceptar un componente con estructura valida."""
        from pipeline.step3_generate import _basic_python_validation

        valid_code = """
import React from 'react';
const App: React.FC = () => {
  return <div>Hello</div>;
};
export default App;
"""
        assert _basic_python_validation(valid_code) is True

    def test_basic_python_validation_rechaza_codigo_invalido(self):
        """_basic_python_validation rechaza codigo sin estructura React valida."""
        from pipeline.step3_generate import _basic_python_validation

        invalid_code = "console.log('hello')"
        assert _basic_python_validation(invalid_code) is False
