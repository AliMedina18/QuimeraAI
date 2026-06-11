"""
test_suggestion_engine.py — Tests unitarios del motor de sugerencias
=====================================================================
Todos marcados @pytest.mark.unit — sin Gemini, sin red, sin credenciales.
Correr con: pytest tests/test_suggestion_engine.py -v
"""

import pytest
from services.suggestion_engine import (
    detect_missing,
    get_styles_for_industry,
    get_templates_for_industry,
    get_palettes_for_industry,
    analyze_brief,
)


# ============================================================================
# detect_missing — qué falta en el brief
# ============================================================================

class TestDetectMissing:

    @pytest.mark.unit
    def test_brief_vacio_detecta_todo(self):
        """Un brief mínimo debe detectar todos los elementos faltantes."""
        missing = detect_missing("tienda online")
        keys = [m["key"] for m in missing]
        assert "audience" in keys
        assert "colors" in keys
        assert "tone" in keys
        assert "sections" in keys
        assert "cta" in keys

    @pytest.mark.unit
    def test_audience_detectado_con_jovenes(self):
        missing = detect_missing("app para jóvenes de 25-35 años")
        keys = [m["key"] for m in missing]
        assert "audience" not in keys

    @pytest.mark.unit
    def test_audience_detectado_con_profesionales(self):
        missing = detect_missing("plataforma para profesionales B2B")
        keys = [m["key"] for m in missing]
        assert "audience" not in keys

    @pytest.mark.unit
    def test_colores_detectados_con_hex(self):
        missing = detect_missing("sitio web con color #1A56DB y fondo blanco")
        keys = [m["key"] for m in missing]
        assert "colors" not in keys

    @pytest.mark.unit
    def test_colores_detectados_con_nombre(self):
        missing = detect_missing("diseño en azul y negro, elegante")
        keys = [m["key"] for m in missing]
        assert "colors" not in keys

    @pytest.mark.unit
    def test_tono_detectado_minimalista(self):
        missing = detect_missing("landing page minimalista y moderna")
        keys = [m["key"] for m in missing]
        assert "tone" not in keys

    @pytest.mark.unit
    def test_tono_detectado_premium(self):
        missing = detect_missing("diseño premium y lujoso para spa")
        keys = [m["key"] for m in missing]
        assert "tone" not in keys

    @pytest.mark.unit
    def test_secciones_detectadas(self):
        missing = detect_missing("necesito hero, servicios y contacto")
        keys = [m["key"] for m in missing]
        assert "sections" not in keys

    @pytest.mark.unit
    def test_cta_detectado_reservar(self):
        missing = detect_missing("quiero que los usuarios puedan reservar cita")
        keys = [m["key"] for m in missing]
        assert "cta" not in keys

    @pytest.mark.unit
    def test_cta_detectado_registrarse(self):
        missing = detect_missing("botón de registrarse gratis en el hero")
        keys = [m["key"] for m in missing]
        assert "cta" not in keys

    @pytest.mark.unit
    def test_brief_completo_no_missing(self):
        """Brief con todo incluido no debe tener elementos faltantes."""
        brief = (
            "App fintech para jóvenes 25-35. "
            "Colores azul #1A56DB y blanco. "
            "Estilo minimalista y elegante. "
            "Secciones: hero, precios, testimonios, contacto. "
            "CTA: registrarse gratis."
        )
        missing = detect_missing(brief)
        assert missing == [], f"Se esperaba [] pero hay: {[m['key'] for m in missing]}"

    @pytest.mark.unit
    def test_chip_text_no_vacio(self):
        """Cada elemento faltante debe tener chip_text no vacío."""
        missing = detect_missing("tienda")
        for m in missing:
            assert m["chip_text"].strip(), f"chip_text vacío en {m['key']}"
            assert m["label"].strip()
            assert m["hint"].strip()

    @pytest.mark.unit
    def test_missing_es_lista_de_dicts(self):
        missing = detect_missing("restaurante de sushi")
        assert isinstance(missing, list)
        for m in missing:
            assert isinstance(m, dict)
            assert {"key", "label", "hint", "chip_text"} <= m.keys()


# ============================================================================
# get_styles_for_industry — estilos por industria
# ============================================================================

class TestGetStyles:

    @pytest.mark.unit
    def test_retorna_lista_no_vacia(self):
        styles = get_styles_for_industry("fintech")
        assert len(styles) > 0

    @pytest.mark.unit
    def test_retorna_entre_3_y_6_estilos(self):
        for industry in ["restaurant", "saas", "fitness", "healthcare", "unknown"]:
            styles = get_styles_for_industry(industry)
            assert 3 <= len(styles) <= 6, f"Estilos para {industry}: {len(styles)}"

    @pytest.mark.unit
    def test_cada_estilo_tiene_campos_requeridos(self):
        styles = get_styles_for_industry("saas")
        for s in styles:
            assert "id" in s
            assert "label" in s
            assert "emoji" in s
            assert "description" in s
            assert "chip_text" in s

    @pytest.mark.unit
    def test_campo_industries_no_expuesto(self):
        """El campo 'industries' es interno y no debe llegar al cliente."""
        styles = get_styles_for_industry("fitness")
        for s in styles:
            assert "industries" not in s

    @pytest.mark.unit
    def test_chip_text_no_vacio(self):
        styles = get_styles_for_industry("restaurant")
        for s in styles:
            assert s["chip_text"].strip()

    @pytest.mark.unit
    def test_industria_desconocida_igual_retorna_estilos(self):
        styles = get_styles_for_industry("industria_inexistente_xyz")
        assert len(styles) >= 3

    @pytest.mark.unit
    def test_fitness_incluye_dark_o_bold(self):
        """Fitness debe tener estilos de alta energía como primeros resultados."""
        styles = get_styles_for_industry("fitness")
        ids = [s["id"] for s in styles]
        assert "bold" in ids or "dark" in ids, f"Se esperaba bold o dark en fitness, got: {ids}"


# ============================================================================
# get_templates_for_industry — templates por industria
# ============================================================================

class TestGetTemplates:

    @pytest.mark.unit
    def test_retorna_lista_no_vacia(self):
        templates = get_templates_for_industry("fintech")
        assert len(templates) > 0

    @pytest.mark.unit
    def test_maximo_4_templates(self):
        for industry in ["fintech", "saas", "restaurant", "automotive", "unknown"]:
            templates = get_templates_for_industry(industry)
            assert len(templates) <= 4, f"{industry} tiene {len(templates)} templates (máx 4)"

    @pytest.mark.unit
    def test_cada_template_tiene_campos_requeridos(self):
        templates = get_templates_for_industry("saas")
        for t in templates:
            assert "slug" in t
            assert "label" in t
            assert "mood" in t
            assert "chip_text" in t

    @pytest.mark.unit
    def test_chip_text_menciona_label(self):
        """El chip_text debe mencionar el nombre del template."""
        templates = get_templates_for_industry("fintech")
        for t in templates:
            assert t["label"] in t["chip_text"], (
                f"chip_text de {t['slug']} no menciona el label '{t['label']}'"
            )

    @pytest.mark.unit
    def test_fintech_incluye_stripe_o_revolut(self):
        templates = get_templates_for_industry("fintech")
        slugs = [t["slug"] for t in templates]
        assert "stripe" in slugs or "revolut" in slugs, f"fintech slugs: {slugs}"

    @pytest.mark.unit
    def test_saas_incluye_notion_o_figma(self):
        templates = get_templates_for_industry("saas")
        slugs = [t["slug"] for t in templates]
        assert "notion" in slugs or "figma" in slugs

    @pytest.mark.unit
    def test_automotive_incluye_tesla_o_bmw(self):
        templates = get_templates_for_industry("automotive")
        slugs = [t["slug"] for t in templates]
        assert "tesla" in slugs or "bmw" in slugs

    @pytest.mark.unit
    def test_industria_desconocida_usa_fallback(self):
        """Industrias no mapeadas deben usar los templates genéricos."""
        templates = get_templates_for_industry("industria_desconocida_xyz")
        assert len(templates) > 0
        slugs = [t["slug"] for t in templates]
        # Debe incluir algún template del fallback genérico
        assert any(s in slugs for s in ["stripe", "notion", "airbnb", "figma", "apple"])


# ============================================================================
# get_palettes_for_industry — paletas por industria
# ============================================================================

class TestGetPalettes:

    @pytest.mark.unit
    def test_retorna_entre_1_y_3_paletas(self):
        for industry in ["fintech", "restaurant", "wellness", "unknown"]:
            palettes = get_palettes_for_industry(industry)
            assert 1 <= len(palettes) <= 3, f"{industry}: {len(palettes)} paletas"

    @pytest.mark.unit
    def test_cada_paleta_tiene_campos_requeridos(self):
        palettes = get_palettes_for_industry("fintech")
        for p in palettes:
            assert "name" in p
            assert "primary" in p
            assert "secondary" in p
            assert "accent" in p
            assert "surface" in p
            assert "text" in p
            assert "chip_text" in p

    @pytest.mark.unit
    def test_colores_son_hex_validos(self):
        """Todos los campos de color deben ser hex válidos (#RGB o #RRGGBB)."""
        import re
        hex_pattern = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")
        palettes = get_palettes_for_industry("saas")
        for p in palettes:
            for field in ["primary", "secondary", "accent", "surface", "text"]:
                assert hex_pattern.match(p[field]), (
                    f"Color inválido en paleta '{p['name']}' campo '{field}': {p[field]}"
                )

    @pytest.mark.unit
    def test_chip_text_menciona_colores(self):
        """El chip_text de cada paleta debe mencionar al menos un valor hex."""
        palettes = get_palettes_for_industry("restaurant")
        for p in palettes:
            assert "#" in p["chip_text"], f"chip_text sin hex en paleta '{p['name']}'"

    @pytest.mark.unit
    def test_industria_desconocida_usa_fallback(self):
        palettes = get_palettes_for_industry("xyz_desconocido")
        assert len(palettes) > 0


# ============================================================================
# analyze_brief — función principal
# ============================================================================

class TestAnalyzeBrief:

    @pytest.mark.unit
    def test_retorna_dict_con_claves_requeridas(self):
        result = analyze_brief("restaurante de comida italiana")
        assert "industry" in result
        assert "confidence" in result
        assert "missing" in result
        assert "styles" in result
        assert "templates" in result
        assert "palettes" in result

    @pytest.mark.unit
    def test_confidence_entre_0_y_1(self):
        result = analyze_brief("gym y entrenamiento personal")
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.unit
    def test_detecta_restaurante(self):
        result = analyze_brief("Restaurante de sushi premium en Madrid")
        assert result["industry"] == "restaurant"

    @pytest.mark.unit
    def test_detecta_fitness(self):
        result = analyze_brief("Gimnasio y centro de entrenamiento personal")
        assert result["industry"] == "fitness"

    @pytest.mark.unit
    def test_detecta_healthcare(self):
        result = analyze_brief("Clínica médica de salud integral y bienestar")
        assert result["industry"] == "healthcare"

    @pytest.mark.unit
    def test_detecta_hotel(self):
        result = analyze_brief("Hotel boutique de lujo en Cartagena")
        assert result["industry"] == "hotel"

    @pytest.mark.unit
    def test_brief_completo_no_missing(self):
        brief = (
            "App fintech para profesionales 30-45. "
            "Colores azul marino y blanco. "
            "Estilo formal y elegante. "
            "Secciones hero, características, precios, testimonios. "
            "CTA: crear cuenta gratis."
        )
        result = analyze_brief(brief)
        assert result["missing"] == [], f"Missing inesperado: {[m['key'] for m in result['missing']]}"

    @pytest.mark.unit
    def test_listas_no_vacias(self):
        result = analyze_brief("tienda de ropa y moda")
        assert len(result["styles"]) > 0
        assert len(result["templates"]) > 0
        assert len(result["palettes"]) > 0

    @pytest.mark.unit
    def test_brief_muy_corto_no_rompe(self):
        """Un brief de pocas palabras no debe lanzar excepción."""
        result = analyze_brief("café")
        assert "industry" in result

    @pytest.mark.unit
    def test_brief_en_ingles(self):
        result = analyze_brief("luxury hotel resort with spa and pool")
        assert result["industry"] == "hotel"
        assert len(result["templates"]) > 0
