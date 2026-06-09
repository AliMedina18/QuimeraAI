# Quimera AI

Generador de interfaces web basado en IA. Toma un brief en lenguaje natural y produce un sistema de diseño completo (DESIGN.md) + sitio HTML autocontenido listo para usar.

Proyecto para el **Google AI Agents Challenge** — deadline 11 jul 2026.

Stack: **GCP · Gemini 2.5 Pro/Flash · FastAPI · Next.js**

---

## Arquitectura

Pipeline de 4 pasos que convierte un brief en un sitio web completo:

```
Brief del usuario
      │
      ▼
Paso 0: analyze_templates()     → Analiza 80+ templates de marca (Stripe, Airbnb, Figma…)
      │
      ▼
Paso 1: analyze_and_design()    → Genera DESIGN.md (tokens YAML + filosofía Markdown)
      │
      ▼
Paso 2: analyze_for_images()    → Planifica qué imágenes generar y dónde
      │
      ▼
Paso 3: generate_code()         → Genera HTML autocontenido con CSS variables
```

`DesignContext` es el único estado compartido entre pasos (modelo Pydantic en `backend/models.py`).

---

## Setup local (Windows)

### Requisitos

- Python 3.12 ([python.org](https://www.python.org/downloads/))
- Node.js 20+ ([nodejs.org](https://nodejs.org/))
- Git

### 1. Clonar el repo

```bash
git clone https://github.com/AliMedina18/QuimeraAI
cd QuimeraAI
```

### 2. Crear y activar el entorno virtual

Desde la raíz del repo, en PowerShell:

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

> Hay que activar el entorno cada vez que abras un terminal nuevo.

### 3. Instalar dependencias Python

```powershell
pip install -r backend/requirements.txt
```

### 4. Configurar la API key de Gemini

```powershell
Copy-Item backend\.env.example backend\.env
```

Edita `backend/.env` y agrega tu clave de [Google AI Studio](https://aistudio.google.com/app/apikey):

```
GOOGLE_API_KEY=tu_clave_aqui
```

### 5. Correr el backend

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

Endpoints disponibles:

| Endpoint | Descripción |
|---|---|
| `GET /health` | Health check |
| `GET /gemini-test` | Verifica conexión con Gemini |
| `GET /templates` | Lista los 80+ templates disponibles |
| `GET /docs` | Swagger UI interactivo |
| `POST /generar-diseno` | Ejecuta el pipeline completo |

### 6. Correr el frontend

```powershell
cd frontend
npm install        # solo la primera vez
npm run dev        # http://localhost:3000
```

Configura la URL del backend en `frontend/.env.local` (por defecto ya apunta a `http://localhost:8000`):

```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Tests

Desde la raíz del repo (con el entorno virtual activo):

```powershell
# Tests unitarios — sin credenciales, los más rápidos
pytest tests/ -m unit -v

# Todos los tests rápidos (sin llamadas a Gemini)
pytest tests/ -m "not slow" -v

# Un test específico
pytest tests/test_scorers.py::TestWcagContrast::test_negro_sobre_blanco_es_21 -v

# Tests que llaman a Gemini (requieren GOOGLE_API_KEY)
pytest tests/ -m slow -v
```

El archivo `pytest.ini` configura `pythonpath = backend`, por lo que no hay que agregar nada a `PYTHONPATH` manualmente.

> Los tests `@pytest.mark.slow` requieren `GOOGLE_API_KEY` en `backend/.env`. Si la API falla por red, el test se convierte en SKIP automáticamente.

---

## Verificar sintaxis Python

```powershell
cd backend
py -3.12 -m py_compile main.py models.py `
  pipeline/step0_template_analysis.py `
  pipeline/step1_analyze.py `
  pipeline/step2_analyze_images.py `
  pipeline/step3_generate.py `
  pipeline/scorers/wcag_contrast.py `
  services/gemini_client.py `
  services/design_templates.py `
  services/template_analyzer.py `
  services/color_science.py `
  services/typography_analyzer.py
```

Sin output = todo bien. Con error = muestra el archivo y la línea.

---

## Deployment (Cloud Run)

```bash
bash setup_gcp.sh
```

El Dockerfile en `backend/Dockerfile` usa `python:3.12-slim` y arranca uvicorn directamente con `uvicorn main:app`. La imagen final es ~300MB.

Cloud Run inyecta `GOOGLE_API_KEY` desde Secret Manager y `PORT=8080` automáticamente.

---

## Estructura del proyecto

```
QuimeraAI/
├── backend/
│   ├── main.py                          # FastAPI app + endpoints
│   ├── models.py                        # DesignContext y modelos Pydantic
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pipeline/
│   │   ├── step0_template_analysis.py   # Paso 0: analiza templates
│   │   ├── step1_analyze.py             # Paso 1: genera DESIGN.md
│   │   ├── step2_analyze_images.py      # Paso 2: planifica imágenes
│   │   ├── step3_generate.py            # Paso 3: genera HTML
│   │   ├── scorers/
│   │   │   └── wcag_contrast.py         # Validación WCAG 2.1 (funciones puras)
│   │   └── archive/                     # Pipeline v1 archivado (no activo)
│   ├── services/
│   │   ├── gemini_client.py             # Wrapper google-genai SDK
│   │   ├── design_templates.py          # Carga 80+ templates DESIGN.md
│   │   ├── template_analyzer.py         # Extrae patrones de templates
│   │   ├── typography_analyzer.py       # Pairings tipográficos por industria
│   │   ├── color_science.py             # WCAG, paletas tonales, hex/rgb
│   │   ├── firestore_client.py          # Stub — Day 4
│   │   ├── storage_client.py            # Stub — Day 4
│   │   └── image_generator.py           # Stub — Day 4 (Imagen 3)
│   └── design_templates/                # 80+ archivos DESIGN.md de referencia
├── frontend/
│   ├── app/                             # Next.js App Router
│   ├── components/
│   │   ├── ChatUI.tsx                   # Input del brief
│   │   ├── DesignPreview.tsx            # Muestra DESIGN.md
│   │   ├── PreviewWindow.tsx            # Iframe con el HTML generado
│   │   └── ReactPreview.tsx             # Vista de código HTML
│   ├── hooks/
│   │   └── usePipeline.ts               # Hook para llamar al backend
│   └── types/
│       └── pipeline.ts                  # Tipos TypeScript del pipeline
├── tests/
│   ├── conftest.py                      # Setup pytest (sys.path, .env, hooks)
│   ├── test_scorers.py                  # Tests unitarios: DESIGN.md + HTML + WCAG
│   ├── test_pipeline.py                 # Tests de integración del pipeline
│   └── ...                             # Tests adicionales
├── pytest.ini                           # pythonpath = backend
├── CLAUDE.md                            # Documentación técnica para Claude
└── setup_gcp.sh                         # Setup de GCP (Cloud Run, Secret Manager)
```

---

Ver `CLAUDE.md` para documentación técnica detallada (Gemini SDK, scorers WCAG, markers de test, deployment).
