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
    
    # Detectar industria del brief (simple heuristic)
    industry = _detect_industry(context.design_brief)
    
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


def _detect_industry(brief: str) -> str:
    """
    Detecta industria del brief basándose en keywords.
    
    Returns:
        Nombre de industria detectada
    """
    brief_lower = brief.lower()
    
    industry_keywords = {
        "fintech": ["finance", "bank", "payment", "crypto", "money", "transaction", "wallet"],
        "saas": ["software", "app", "platform", "tool", "service", "dashboard", "analytics"],
        "marketplace": ["marketplace", "seller", "buyer", "product", "shop", "ecommerce"],
        "design": ["design", "ui", "ux", "creative", "portfolio"],
        "commerce": ["store", "shop", "buy", "sell", "product", "ecommerce"],
        "productivity": ["task", "todo", "project", "manage", "calendar", "schedule"],
        "social": ["social", "community", "network", "chat", "message"],
        "media": ["video", "music", "stream", "content", "media"],
    }
    
    for industry, keywords in industry_keywords.items():
        for keyword in keywords:
            if keyword in brief_lower:
                return industry
    
    return "saas"  # Default
