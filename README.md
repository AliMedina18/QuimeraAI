# Quimera AI

> Agente de diseño visual que convierte un brief en lenguaje natural en un sitio web completo, listo para usar.

Proyecto para el **Google AI Agents Challenge** — deadline 11 jul 2026.

Stack: **GCP · Gemini 2.5 Pro/Flash · FastAPI · Next.js · Cloud Run · Firestore · Cloud Storage**

---

## ¿Qué es Quimera?

Quimera es un agente AI que toma una descripción en lenguaje natural ("Restaurante de sushi premium, colores oscuros con dorado, menú interactivo y reservas") y genera automáticamente:

- Un sistema de diseño completo en `DESIGN.md` (tokens de color, tipografía, espaciado, filosofía de marca)
- Un sitio HTML autocontenido con CSS variables, listo para desplegar
- Vista Studio para editar el resultado: colores, texto inline, redimensionar elementos, edición asistida por IA

---

## Arquitectura del pipeline

```
Brief del usuario
      │
      ▼
Paso 0: analyze_templates()      → Analiza 80+ templates de marca reales (Stripe, Airbnb, Figma, Apple…)
      │                             extrae patrones de color, tipografía y layout de referencia
      ▼
Paso 1: analyze_and_design()     → Genera DESIGN.md completo con tokens YAML + filosofía de diseño
      │                             usa Gemini 2.5 Pro con los patrones de referencia como contexto
      ▼
Paso 2: analyze_for_images()     → Planifica las imágenes a generar y dónde colocarlas en el layout
      │
      ▼
Paso 3: generate_code()          → Genera HTML autocontenido con CSS custom properties
                                    usa Gemini 2.5 Flash optimizado para code generation
```

`DesignContext` (en `backend/models.py`) es el único estado compartido entre pasos — modelo Pydantic que se enriquece en cada etapa.

---

## Features

### Generación
- Pipeline de 4 pasos con Gemini 2.5 Pro (análisis) y Flash (código)
- 80+ templates de diseño reales como referencia (marcas tech, moda, automoción, fintech…)
- Análisis WCAG 2.1 de contraste en colores generados
- Sugerencias de brief basadas en industria y estilo

### Studio (editor visual)
- Selección de elementos con click en el preview
- Edición de color de texto y fondo con color picker
- Edición inline de texto (doble click)
- Redimensionado con handles de drag
- Edición asistida por IA con contexto del elemento seleccionado
- Reemplazo global de colores en todo el sitio
- Historial de versiones con undo/redo
- Paleta de colores del sitio detectada automáticamente

### Biblioteca personal
- Guardar diseños en biblioteca con nombre personalizado
- HTML y DESIGN.md almacenados en Cloud Storage (sin límite de tamaño)
- Rutas de GCS persistidas en Firestore
- Recuperar y editar diseños guardados desde la biblioteca

### Usuarios
- Registro con nombre y email
- Email de bienvenida via SendGrid
- Persistencia en localStorage (sin autenticación compleja)
- Modal de valoración tras guardar el primer diseño

---

## Estructura del proyecto

```
QuimeraAI/
├── backend/
│   ├── main.py                          # FastAPI — todos los endpoints
│   ├── models.py                        # DesignContext + modelos Pydantic
│   ├── requirements.txt
│   ├── Dockerfile                       # python:3.12-slim → Cloud Run
│   ├── .env.example                     # Variables de entorno (copiar a .env)
│   ├── pipeline/
│   │   ├── step0_template_analysis.py   # Analiza templates de referencia
│   │   ├── step1_analyze.py             # Genera DESIGN.md con Gemini Pro
│   │   ├── step2_analyze_images.py      # Plan de imágenes
│   │   ├── step3_generate.py            # Genera HTML con Gemini Flash
│   │   ├── scorers/
│   │   │   └── wcag_contrast.py         # Validación WCAG 2.1 (funciones puras)
│   │   └── archive/                     # Pipeline v1 archivado (referencia)
│   ├── services/
│   │   ├── gemini_client.py             # Wrapper google-genai SDK
│   │   ├── design_templates.py          # Carga 80+ DESIGN.md de referencia
│   │   ├── template_analyzer.py         # Extrae patrones de templates
│   │   ├── typography_analyzer.py       # Pairings tipográficos por industria
│   │   ├── color_science.py             # WCAG, paletas tonales OKLCH, hex/rgb
│   │   ├── firestore_client.py          # Persistencia en Cloud Firestore
│   │   ├── storage_client.py            # HTML/Markdown en Cloud Storage
│   │   ├── image_generator.py           # Imagen 3 (stub — pendiente)
│   │   └── email_client.py              # SendGrid — email de bienvenida
│   └── design_templates/                # 80+ archivos DESIGN.md de referencia
│       ├── stripe/, airbnb/, figma/, apple/, nike/, tesla/ …
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Pantalla principal — brief + preview
│   │   ├── studio/page.tsx              # Studio — editor visual completo
│   │   ├── biblioteca/page.tsx          # Biblioteca — diseños guardados
│   │   └── welcome/page.tsx             # Onboarding — registro de usuario
│   ├── components/
│   │   ├── ChatUI.tsx                   # Input del brief con sugerencias
│   │   ├── BriefSuggestions.tsx         # Chips de contexto para el brief
│   │   ├── PreviewWindow.tsx            # Iframe del HTML + scripts de Studio
│   │   ├── ColorPicker.tsx              # Selector de color con hex input
│   │   ├── RatingModal.tsx              # Modal de valoración de experiencia
│   │   ├── QuimeraLoader.tsx            # Animación de carga
│   │   └── Icons.tsx                    # SVG icons inline
│   ├── hooks/
│   │   ├── usePipeline.ts               # Llama a /generar-diseno
│   │   ├── useStudio.ts                 # Estado completo del Studio
│   │   ├── useLibrary.ts                # Operaciones de biblioteca
│   │   └── useUser.ts                   # Registro y estado del usuario
│   └── types/
│       └── pipeline.ts                  # Tipos TypeScript compartidos
│
├── tests/
│   ├── conftest.py                      # Setup pytest (sys.path, .env, markers)
│   ├── test_scorers.py                  # Tests unitarios WCAG + colores
│   ├── test_pipeline.py                 # Tests integración del pipeline
│   └── test_color_utils.py              # Tests de colorUtils frontend (via Node)
│
├── pytest.ini                           # pythonpath = backend
├── CLAUDE.md                            # Documentación técnica detallada
└── setup_gcp.sh                         # Setup completo de GCP
```

---

## Endpoints del backend

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/gemini-test` | Verifica conexión con Gemini |
| `GET` | `/templates` | Lista los 80+ templates disponibles |
| `GET` | `/docs` | Swagger UI interactivo |
| `POST` | `/sugerir` | Sugerencias de brief por industria |
| `POST` | `/generar-diseno` | Ejecuta el pipeline completo (4 pasos) |
| `POST` | `/editar-diseno` | Edición de HTML asistida por IA (Studio) |
| `POST` | `/usuarios/registrar` | Registra usuario + envía email de bienvenida |
| `POST` | `/biblioteca/guardar` | Guarda diseño en GCS + Firestore |
| `GET` | `/biblioteca` | Lista diseños de un usuario |
| `GET` | `/biblioteca/{id}` | Recupera un diseño (HTML + DESIGN.md desde GCS) |
| `DELETE` | `/biblioteca/{id}` | Elimina diseño de Firestore + GCS |

---

## Setup local (Windows)

### Requisitos

- Python 3.12 — [python.org](https://www.python.org/downloads/)
- Node.js 20+ — [nodejs.org](https://nodejs.org/)
- Cuenta en [Google AI Studio](https://aistudio.google.com/) para la API key de Gemini
- (Opcional para biblioteca) Cuenta GCP con Firestore + Cloud Storage

### 1. Clonar el repo

```bash
git clone https://github.com/AliMedina18/QuimeraAI
cd QuimeraAI
```

### 2. Entorno virtual Python

```powershell
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### 3. Variables de entorno del backend

```powershell
Copy-Item backend\.env.example backend\.env
```

Edita `backend/.env`:

```env
# Requerido — Gemini API
GOOGLE_API_KEY=tu_clave_de_google_ai_studio

# Opcional — para la biblioteca (Cloud Firestore + Storage)
GOOGLE_CLOUD_PROJECT=tu_proyecto_gcp

# Opcional — para emails de bienvenida
SENDGRID_API_KEY=tu_clave_sendgrid
SENDGRID_FROM_EMAIL=noreply@tudominio.com
```

### 4. Correr el backend

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

Swagger UI disponible en [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Correr el frontend

```powershell
cd frontend
npm install        # solo la primera vez
npm run dev        # → http://localhost:3000
```

`frontend/.env.local` ya apunta a `http://localhost:8000` por defecto. Si el backend corre en otro puerto:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Tests

Con el entorno virtual activo, desde la raíz del repo:

```powershell
# Tests unitarios — sin credenciales, más rápidos
pytest tests/ -m unit -v

# Todos los tests rápidos (sin llamadas a Gemini)
pytest tests/ -m "not slow" -v

# Un test específico
pytest tests/test_scorers.py::TestWcagContrast::test_negro_sobre_blanco_es_21 -v

# Tests de integración con Gemini (requieren GOOGLE_API_KEY)
pytest tests/ -m slow -v
```

### Markers

| Marker | Descripción |
|--------|-------------|
| `@pytest.mark.unit` | Lógica pura, sin credenciales |
| `@pytest.mark.slow` | Llama a Gemini — consume cuota |

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
  services/typography_analyzer.py `
  services/firestore_client.py `
  services/storage_client.py `
  services/email_client.py
```

Sin output = todo bien.

---

## Deployment en Google Cloud

### Prerrequisitos

- `gcloud` CLI instalado y autenticado
- Proyecto GCP con billing activo
- APIs habilitadas: Cloud Run, Artifact Registry, Firestore, Cloud Storage, Secret Manager

### Setup inicial (una vez)

```bash
bash setup_gcp.sh
```

El script configura: proyecto GCP, APIs, Secret Manager con `GOOGLE_API_KEY`, bucket de Cloud Storage `quimera-ai-prod-outputs`, base de datos Firestore, y despliega la imagen Docker en Cloud Run.

### Deploy manual

```bash
# Build y push de la imagen
gcloud builds submit backend/ \
  --tag gcr.io/TU_PROYECTO/quimera-backend

# Deploy a Cloud Run
gcloud run deploy quimera-backend \
  --image gcr.io/TU_PROYECTO/quimera-backend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets GOOGLE_API_KEY=quimera-gemini-key:latest \
  --set-env-vars GOOGLE_CLOUD_PROJECT=TU_PROYECTO
```

Cloud Run inyecta `PORT=8080` automáticamente. El `Dockerfile` usa `python:3.12-slim` (~300 MB).

### Infraestructura GCP utilizada

| Servicio | Uso |
|----------|-----|
| **Cloud Run** | Backend FastAPI (escala a 0) |
| **Firestore** | Metadatos de usuarios y diseños |
| **Cloud Storage** | HTML y DESIGN.md generados (`quimera-ai-prod-outputs`) |
| **Secret Manager** | `GOOGLE_API_KEY` y `SENDGRID_API_KEY` |
| **Gemini 2.5 Pro** | Pasos 0 y 1 del pipeline (análisis + diseño) |
| **Gemini 2.5 Flash** | Paso 3 (generación de código HTML) |

---

## Estado de implementación

| Componente | Estado |
|------------|--------|
| Pipeline 4 pasos (Step 0–3) | ✅ Completo |
| 80+ templates de referencia | ✅ Completo |
| Scorers WCAG 2.1 | ✅ Completo |
| Backend FastAPI (todos los endpoints) | ✅ Completo |
| Frontend — brief + preview | ✅ Completo |
| Studio — selección de elementos | ✅ Completo |
| Studio — edición de colores | ✅ Completo |
| Studio — edición de texto inline | ✅ Completo |
| Studio — resize de elementos | ✅ Completo |
| Studio — edición asistida por IA | ✅ Completo |
| Studio — historial de versiones | ✅ Completo |
| Biblioteca personal | ✅ Completo |
| Cloud Storage (HTML + Markdown) | ✅ Completo |
| Firestore (metadatos) | ✅ Completo |
| Registro de usuarios + email | ✅ Completo |
| Generación de imágenes (Imagen 3) | 🔨 Stub — pendiente |

---

## Reconocimientos

Quimera se apoya en el trabajo de estas comunidades y proyectos open source:

### UI / Componentes visuales

**[Flowbite](https://github.com/themesberg/flowbite)** — Themesberg  
Librería de componentes UI sobre Tailwind CSS. Sirvió de referencia de patrones de componentes, accesibilidad y estructura HTML semántica para los templates de diseño generados por Quimera.

**[Phantom UI](https://github.com/Aejkatappaja/phantom-ui)**  
Colección de componentes glassmorphism y dark-mode. Inspiró el sistema de estilos oscuros del Studio y la interfaz de Quimera.

### Ciencia del color

**[colour-science/colour](https://github.com/colour-science/colour)**  
Librería Python de colorimetría científica. Base del servicio `color_science.py` de Quimera: validación WCAG 2.1, paletas tonales OKLCH, conversión de espacios de color y distancias perceptuales ΔE CIEDE2000.

### Optimización de prompts

**[prompt-optimizer](https://github.com/linshenkx/prompt-optimizer)**  
Herramienta de optimización y evaluación de prompts LLM. Referencia metodológica para el diseño de los prompts de los pasos 1 y 3 del pipeline de Quimera.

---

Ver `CLAUDE.md` para documentación técnica detallada (Gemini SDK, arquitectura interna, scorers WCAG, markers de test).
