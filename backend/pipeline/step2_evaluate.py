"""
step2_evaluate.py — ARCHIVO MOVIDO A ARCHIVE
=============================================

Este módulo pertenecía al pipeline de evaluación estética v1.
Fue diseñado para evaluar propuestas de diseño en 8 criterios y decidir
si el diseño pasaba (score >= 85) o necesitaba iteración.

El pipeline activo (v3) ya no incluye este paso de evaluación.
La arquitectura actual es:
    Step 0: analyze_templates    → step0_template_analysis.py
    Step 1: analyze_and_design   → step1_analyze.py
    Step 2: analyze_for_images   → step2_analyze_images.py
    Step 3: generate_code        → step3_generate.py

El código original se conserva en:
    backend/pipeline/archive/step2_evaluate_v1.py

Para reactivar la evaluación, se debe:
1. Actualizar DesignContext en models.py con los campos necesarios
2. Adaptar los scorers al nuevo modelo
3. Integrarlo al pipeline en main.py
"""

# Este archivo es un placeholder. El código activo está en el pipeline v3.
# Ver: backend/pipeline/archive/step2_evaluate_v1.py
