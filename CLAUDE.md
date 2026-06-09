# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from the repo root unless noted.

```bash
# Run all fast tests (no Gemini calls)
pytest tests/ -m "not slow" -v

# Run a single test
pytest tests/test_scorers.py::TestWcagContrast::test_negro_sobre_blanco_es_21 -v

# Run only unit tests (no credentials needed)
pytest tests/ -m unit -v

# Run backend locally
cd backend
uvicorn main:app --reload --port 8000

# Verify syntax of all Python files
cd backend && python -m py_compile main.py models.py \
  pipeline/step0_template_analysis.py \
  pipeline/step1_analyze.py \
  pipeline/step2_analyze_images.py \
  pipeline/step3_generate.py \
  pipeline/scorers/wcag_contrast.py \
  services/gemini_client.py \
  services/design_templates.py \
  services/template_analyzer.py \
  services/color_science.py \
  services/typography_analyzer.py
```

The backend requires `backend/.env` with `GOOGLE_API_KEY=...` to run locally. Copy `backend/.env.example`.

`pytest.ini` sets `pythonpath = backend`, so tests import as `from models import ...`,
`from pipeline.step1_analyze import ...`, etc. No `sys.path` hacks needed.

## Architecture

Quimera is a 4-step pipeline: **brief → DESIGN.md → image plan → HTML output**.
Each step enriches a single shared object (`DesignContext`) and passes it to the next.

```
User brief
    │
    ▼
Step 0: analyze_templates()     → DesignContext.template_analysis  (patrones de referencia)
    │
    ▼
Step 1: analyze_and_design()    → DesignContext.design_markdown    (archivo DESIGN.md)
    │
    ▼
Step 2: analyze_for_images()    → DesignContext.image_generation_plan
    │
    ▼
Step 3: generate_code()         → DesignContext.html_output        (sitio HTML completo)
```

### DesignContext es la única fuente de verdad

`backend/models.py` define `DesignContext` — modelo Pydantic que acumula estado a medida
que fluye por el pipeline. Cada función de pipeline recibe, muta y retorna el contexto.

### Servicios de soporte

| Servicio | Responsabilidad |
|----------|-----------------|
| `services/gemini_client.py` | Wrapper del SDK google-genai |
| `services/design_templates.py` | Carga DESIGN.md reales desde `backend/design_templates/` (80+ marcas) |
| `services/template_analyzer.py` | Extrae patrones de templates para el Step 0 |
| `services/typography_analyzer.py` | Recomienda pairings tipográficos por industria |
| `services/color_science.py` | Validación WCAG, paletas tonales, hex/rgb |
| `services/firestore_client.py` | Persistencia en Cloud Firestore (Day 4) |
| `services/storage_client.py` | Cloud Storage para HTML/assets generados (Day 4) |
| `services/image_generator.py` | Generación de imágenes via Imagen 3 (Day 4) |

### Gemini SDK

Usar `google-genai` (NO el deprecado `google-generativeai`). Todas las llamadas van a través
de `backend/services/gemini_client.py`:
- `model="pro"` → `gemini-2.5-pro` (Steps 0 y 1)
- `model="flash"` → `gemini-2.5-flash` (Step 3, generación de código)

El SDK es síncrono; todas las llamadas se envuelven en `asyncio.to_thread()`.

### Scorers WCAG

`backend/pipeline/scorers/wcag_contrast.py` contiene funciones puras reutilizables:
- `calculate_relative_luminance(hex)` — luminancia relativa WCAG 2.1
- `calculate_wcag_ratio(fg, bg)` — ratio de contraste [1.0, 21.0]
- `classify_wcag_level(ratio)` — 'AAA' | 'AA' | 'AA_large' | 'FAIL'
- `validate_pair(text, bg)` — validación completa con dict estructurado

### Código archivado (no activo)

`backend/pipeline/archive/` contiene el pipeline de evaluación estética v1:
- `step2_evaluate_v1.py` — Motor de evaluación en 8 criterios con loop de corrección
- `color_harmony_v1.py` — Scorer algorítmico OKLCH (requiere `colour-science`)
- `llm_scorers_v1.py` — 6 scorers vía Gemini (temperatura=0)

Este código usaba campos de `DesignContext` que ya no existen y fue reemplazado
por el pipeline v3 basado en templates. Se conserva como referencia.

### Test markers

- `@pytest.mark.slow` — llama a Gemini (requiere `GOOGLE_API_KEY`, consume cuota)
- `@pytest.mark.unit` — lógica pura, sin credenciales necesarias

### Deployment

- **Backend:** Docker image → Artifact Registry → Cloud Run (port 8080, `$PORT` env var)
- `backend/Dockerfile` usa `python:3.12-slim`
- `setup_gcp.sh` contiene el setup de GCP (proyecto, APIs, Secret Manager, Cloud Run)
- `GOOGLE_API_KEY` se guarda en Secret Manager y Cloud Run la inyecta como env var

## Estado de implementación

| Archivo | Estado |
|---------|--------|
| `backend/models.py` | ✅ Completo |
| `backend/services/gemini_client.py` | ✅ Completo |
| `backend/pipeline/scorers/wcag_contrast.py` | ✅ Completo (funciones puras) |
| `backend/services/design_templates.py` | ✅ Completo |
| `backend/services/template_analyzer.py` | ✅ Completo |
| `backend/services/typography_analyzer.py` | ✅ Completo |
| `backend/services/color_science.py` | ✅ Completo |
| `backend/main.py` | ✅ Completo — /health, /gemini-test, /templates, /generar-diseno |
| `backend/pipeline/step0_template_analysis.py` | ✅ Completo |
| `backend/pipeline/step1_analyze.py` | ✅ Completo |
| `backend/pipeline/step2_analyze_images.py` | ✅ Completo |
| `backend/pipeline/step3_generate.py` | ✅ Completo |
| `backend/services/image_generator.py` | 🔨 Stub — implementar con Imagen 3 |
| `backend/services/firestore_client.py` | 🔨 Stub — integrar al endpoint /generar-diseno |
| `backend/services/storage_client.py` | 🔨 Stub — implementar |
| `frontend/` | ✅ Funcional — ChatUI + Preview + DESIGN.md view + HTML view |
