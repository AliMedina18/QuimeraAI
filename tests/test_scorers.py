"""
test_scorers.py — Tests unitarios de los scorers algorítmicos
=============================================================
Los scorers algorítmicos (WCAG, color harmony) son deterministas:
dado el mismo input, siempre dan el mismo output.
Eso los hace perfectos para tests unitarios clásicos.

Cuándo correr estos tests:
  pytest tests/test_scorers.py -v

Estado por días:
  Día 1: Tests definidos, todos SKIPPED (scorers son stubs)
  Día 3: Tests completos con asserts reales
"""

import pytest
import sys
import os

# Añadir el directorio backend al path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ---------------------------------------------------------------------------
# TESTS DE WCAG CONTRAST (wcag_contrast.py)
# ---------------------------------------------------------------------------

class TestCalculateRelativeLuminance:
    """Luminancia relativa: el componente base de todos los cálculos WCAG."""

    def test_negro_es_cero(self):
        """El negro absoluto tiene luminancia 0."""
        from pipeline.scorers.wcag_contrast import calculate_relative_luminance
        assert calculate_relative_luminance("#000000") == pytest.approx(0.0, abs=1e-6)

    def test_blanco_es_uno(self):
        """El blanco absoluto tiene luminancia 1."""
        from pipeline.scorers.wcag_contrast import calculate_relative_luminance
        assert calculate_relative_luminance("#FFFFFF") == pytest.approx(1.0, abs=1e-4)

    def test_rojo_puro(self):
        """Rojo puro tiene luminancia ~0.2126 (solo contribuye el canal R)."""
        from pipeline.scorers.wcag_contrast import calculate_relative_luminance
        luminance = calculate_relative_luminance("#FF0000")
        assert luminance == pytest.approx(0.2126, abs=0.001)

    def test_hex_sin_hash(self):
        """Debe funcionar con o sin el # inicial."""
        from pipeline.scorers.wcag_contrast import calculate_relative_luminance
        assert calculate_relative_luminance("FFFFFF") == pytest.approx(1.0, abs=1e-4)

    def test_hex_invalido_lanza_error(self):
        """Un hex inválido debe lanzar ValueError."""
        from pipeline.scorers.wcag_contrast import calculate_relative_luminance
        with pytest.raises(ValueError):
            calculate_relative_luminance("#GGGGGG")


class TestCalculateWcagRatio:
    """Ratio de contraste WCAG: el número que determina la accesibilidad."""

    def test_negro_sobre_blanco_es_21(self):
        """
        El caso canónico: negro sobre blanco = 21:1.
        WCAG lo define como el máximo posible.
        """
        from pipeline.scorers.wcag_contrast import calculate_wcag_ratio
        ratio = calculate_wcag_ratio("#000000", "#FFFFFF")
        assert ratio == pytest.approx(21.0, abs=0.01)

    def test_mismo_color_es_uno(self):
        """Mismo color sobre sí mismo = 1:1 (sin contraste)."""
        from pipeline.scorers.wcag_contrast import calculate_wcag_ratio
        ratio = calculate_wcag_ratio("#3D7AB5", "#3D7AB5")
        assert ratio == pytest.approx(1.0, abs=0.01)

    def test_es_simetrico(self):
        """El ratio es el mismo sin importar el orden de los colores."""
        from pipeline.scorers.wcag_contrast import calculate_wcag_ratio
        r1 = calculate_wcag_ratio("#1E40AF", "#FFFFFF")
        r2 = calculate_wcag_ratio("#FFFFFF", "#1E40AF")
        assert r1 == pytest.approx(r2, abs=0.001)

    def test_gris_767676_bordea_wcag_aa(self):
        """
        #767676 sobre blanco = ~4.48:1.
        Este es el caso de referencia del WCAG: bordea el mínimo de 4.5:1.
        Una diferencia de 1 en cualquier canal puede hacer que falle o pase.
        """
        from pipeline.scorers.wcag_contrast import calculate_wcag_ratio
        ratio = calculate_wcag_ratio("#767676", "#FFFFFF")
        # 4.54 es mayor que 4.5, este par PASA WCAG AA (por muy poco)
        assert ratio > 4.5  # Pasa AA
        assert ratio == pytest.approx(4.54, abs=0.1)

    def test_azul_oscuro_sobre_blanco_pasa_aaa(self):
        """Azul oscuro corporativo debe pasar WCAG AAA (≥7:1)."""
        from pipeline.scorers.wcag_contrast import calculate_wcag_ratio
        ratio = calculate_wcag_ratio("#1E3A8A", "#FFFFFF")
        assert ratio >= 7.0


class TestClassifyWcagLevel:
    """Clasificación del nivel WCAG según el ratio."""

    def test_ratio_21_es_aaa(self):
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(21.0) == "AAA"

    def test_ratio_7_es_aaa(self):
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(7.0) == "AAA"

    def test_ratio_4_5_es_aa(self):
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(4.5) == "AA"

    def test_ratio_3_texto_grande_es_aa_large(self):
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(3.0, is_large_text=True) == "AA_large"

    def test_ratio_2_es_fail(self):
        from pipeline.scorers.wcag_contrast import classify_wcag_level
        assert classify_wcag_level(2.0) == "FAIL"


# ---------------------------------------------------------------------------
# TESTS DE COLOR HARMONY (color_harmony.py)
# ---------------------------------------------------------------------------

class TestAngularDifference:
    """La diferencia angular en el círculo cromático debe ser siempre ≤ 180°."""

    def test_diferencia_simple(self):
        from pipeline.scorers.color_harmony import angular_difference
        assert angular_difference(60.0, 120.0) == pytest.approx(60.0)

    def test_cruza_el_cero(self):
        """10° y 350° están separados por 20°, no por 340°."""
        from pipeline.scorers.color_harmony import angular_difference
        assert angular_difference(10.0, 350.0) == pytest.approx(20.0)

    def test_opuestos_son_180(self):
        """Los colores complementarios están a 180°."""
        from pipeline.scorers.color_harmony import angular_difference
        assert angular_difference(0.0, 180.0) == pytest.approx(180.0)

    def test_simetria(self):
        """El orden no importa."""
        from pipeline.scorers.color_harmony import angular_difference
        assert angular_difference(30.0, 90.0) == angular_difference(90.0, 30.0)


class TestScoreColorHarmony:
    """Tests del scorer de armonía cromática."""

    def test_paleta_vacia_da_cero(self):
        from pipeline.scorers.color_harmony import score_color_harmony
        assert score_color_harmony([]) == 0.0

    def test_un_solo_color_da_neutral(self):
        from pipeline.scorers.color_harmony import score_color_harmony
        score = score_color_harmony(["#1E40AF"])
        assert 40.0 <= score <= 60.0

    def test_complementario_azul_naranja_score_alto(self):
        """Azul y naranja son complementarios en OKLCH -> score >= 85."""
        from pipeline.scorers.color_harmony import score_color_harmony
        palette = ["#0000FF", "#FF8C00"]
        score = score_color_harmony(palette)
        assert score >= 85

    def test_colores_sin_relacion_score_bajo(self):
        """Colores sin relacion cromatica deben dar score < 50."""
        from pipeline.scorers.color_harmony import score_color_harmony
        palette = ["#FF0000", "#FFFF00"]  # rojo y amarillo: sin armonia reconocible
        score = score_color_harmony(palette)
        assert score < 50


# ---------------------------------------------------------------------------
# TESTS DE INTEGRACIÓN (requieren DesignContext completo)
# ---------------------------------------------------------------------------

class TestScoreWcagContrastIntegration:
    """Tests del scorer completo con un DesignContext."""

    def _make_context(self, primary, neutral_palette, secondary=None, accent=None):
        """Helper para crear un DesignContext mínimo para los tests."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
        from models import DesignContext
        return DesignContext(
            design_brief="test",
            primary_color=primary,
            secondary_color=secondary,
            accent_color=accent,
            neutral_palette=neutral_palette,
        )

    def test_paleta_sin_colores_da_neutral(self):
        from pipeline.scorers.wcag_contrast import score_wcag_contrast
        from models import DesignContext
        ctx = DesignContext(design_brief="test")
        score = score_wcag_contrast(ctx)
        assert score == 50.0  # Score neutral cuando no hay datos

    def test_paleta_excelente_da_score_alto(self):
        """Negro sobre blanco siempre debe dar el score máximo."""
        from pipeline.scorers.wcag_contrast import score_wcag_contrast
        ctx = self._make_context(
            primary="#000000",
            neutral_palette=["#FFFFFF", "#F0F0F0", "#333333"],
        )
        score = score_wcag_contrast(ctx)
        assert score >= 90.0

    def test_paleta_ilegible_da_score_bajo(self):
        """Colores casi iguales entre sí deben dar score bajo."""
        from pipeline.scorers.wcag_contrast import score_wcag_contrast
        ctx = self._make_context(
            primary="#CCCCCC",  # gris claro
            neutral_palette=["#DDDDDD", "#EEEEEE", "#BBBBBB"],  # todos grises similares
        )
        score = score_wcag_contrast(ctx)
        assert score < 80.0  # 2 pares fallan: 100 - 2x15 = 70
