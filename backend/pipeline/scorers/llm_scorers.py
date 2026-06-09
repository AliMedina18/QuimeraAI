"""
llm_scorers.py — ARCHIVO MOVIDO A ARCHIVE
==========================================

Este módulo pertenecía al pipeline de evaluación estética v1.
Contenía 6 scorers via Gemini (temperatura=0) que evaluaban:
- Criterio 3: Balance compositivo
- Criterio 4: Jerarquía visual
- Criterio 5: Cumplimiento Gestalt
- Criterio 6: Calidad del espacio negativo
- Criterio 7: Consistencia de marca
- Criterio 8: Accesibilidad general

El pipeline activo (v3) ya no llama a estos scorers.
Además, usaban campos de DesignContext que ya no existen
(primary_color, neutral_palette, brand_personality, industry, etc.)

El código original se conserva en:
    backend/pipeline/archive/llm_scorers_v1.py

Para reactivar, ver las instrucciones en step2_evaluate.py.
"""

# Placeholder — ver backend/pipeline/archive/llm_scorers_v1.py
