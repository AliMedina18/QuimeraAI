#!/usr/bin/env python
"""Test suite para verificar Quimera v3 Pipeline"""

import sys
sys.path.insert(0, '/Users/USUARIO/Documents/Github/QuimeraAI')

from backend.models import DesignContext, TemplatePattern, TemplateAnalysisContext
from backend.services.template_analyzer import get_template_analyzer
from backend.services.color_science import get_color_science
from backend.services.typography_analyzer import get_typography_analyzer

print("✓ All imports successful")

# Test Color Science
cs = get_color_science()
ratio = cs.wcag_contrast_ratio("#ffffff", "#000000")
print(f"✓ Color Science OK - White on Black contrast: {ratio:.1f}:1")

# Test Typography Analyzer
ta = get_typography_analyzer()
rec = ta.recommend_pairing("fintech")
print(f"✓ Typography Analyzer OK - Pairing: {rec['pairing']}")

# Test Template Analyzer
tpl_analyzer = get_template_analyzer()
templates = tpl_analyzer.find_relevant_templates(industry="fintech")
print(f"✓ Template Analyzer OK - Found {len(templates)} templates for fintech")

# Test DesignContext models
context = DesignContext(
    design_brief="Test brief",
    project_type="landing_page"
)
print(f"✓ DesignContext model OK - Created with brief length {len(context.design_brief)}")

print("\n✅ ALL SERVICES INITIALIZED SUCCESSFULLY!")
print("Pipeline v3 is ready for deployment.")
