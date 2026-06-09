"""
step0_template_analysis.py -- PASO 0: Análisis de Templates
===========================================================
Analiza templates relevantes y extrae patrones para mejorar la generación.

Input:  DesignContext (brief, project_type, design_reference)
Output: DesignContext (con template_analysis poblado)
"""

import logging
from models import DesignContext
from services.template_analyzer import get_template_analyzer
from services.keyword_translator import translate_brief_to_keywords

logger = logging.getLogger(__name__)


async def analyze_templates(context: DesignContext) -> DesignContext:
    """
    Step 0: Analiza templates relevantes.
    
    Busca templates por industria/tipo y extrae patrones de:
    - Composición y layout
    - Tipografía
    - Colores
    - Responsive design
    - Elevación/profundidad
    
    Args:
        context: DesignContext con brief, project_type, design_reference
    
    Returns:
        DesignContext actualizado con template_analysis
    """
    analyzer = get_template_analyzer()

    logger.info("Step 0: Analizando templates relevantes...")

    # Detectar industria usando keyword_translator (25+ industrias, ES+EN)
    kw = translate_brief_to_keywords(context.design_brief)
    industry = kw.industry
    logger.info("Step 0: Industria detectada: %s (confianza: %.0f%%)", industry, kw.confidence * 100)
    
    # Realizar análisis completo
    template_analysis = await analyzer.analyze_all_relevant(
        industry=industry,
        project_type=context.project_type,
        design_reference=context.design_reference
    )
    
    context.template_analysis = template_analysis
    
    logger.info(
        f"Step 0: OK. Found {len(template_analysis.relevant_templates)} templates. "
        f"Primary: {template_analysis.primary_template}"
    )
    
    return context


# _detect_industry reemplazada por keyword_translator.translate_brief_to_keywords()
# Se mantiene como fallback legacy por si algo la llama directamente
def _detect_industry(brief: str) -> str:
    kw = translate_brief_to_keywords(brief)
    return kw.industry
