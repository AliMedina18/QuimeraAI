# Quimera AI

Agente de IA para diseño visual. Evalúa estéticamente un diseño antes de generar código React.
Proyecto para el **Google AI Startup Agents Challenge** — deadline 11 jul 2026.

---

## Setup local (Windows)

### Requisitos

- Python 3.12 ([python.org](https://www.python.org/downloads/))
- Git

### 1. Clonar el repo

```bash
git clone https://github.com/tu-usuario/QuimeraAI.git
cd QuimeraAI
```

### 2. Crear y activar el entorno virtual

Desde la raíz del repo, en PowerShell:

```powershell
# Crear el entorno virtual con Python 3.12
py -3.12 -m venv .venv

# Permitir scripts en el terminal actual (solo necesario la primera vez por sesión)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# Activar el entorno — verás (.venv) al inicio del prompt cuando esté activo
.\.venv\Scripts\Activate.ps1
```

> **Nota:** hay que activar el entorno cada vez que abras un terminal nuevo.

### 3. Instalar dependencias

Con el entorno activo (`(.venv)` visible en el prompt):

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

### 5. Correr el backend localmente

```powershell
cd backend
py -3.12 -m uvicorn main:app --reload --port 8000
```

Endpoints disponibles:
- `GET http://localhost:8000/health` — health check
- `GET http://localhost:8000/gemini-test` — verifica conexión con Gemini
- `GET http://localhost:8000/docs` — Swagger UI

---

## Correr los tests

```powershell
# Desde la raíz del repo, con el entorno activo
PYTHONPATH=backend pytest tests/ -m "not slow" -v

# Solo tests unitarios (sin credenciales)
PYTHONPATH=backend pytest tests/ -m unit -v

# Un test específico
PYTHONPATH=backend pytest tests/test_scorers.py::TestCalculateWcagRatio::test_negro_sobre_blanco_es_21 -v
```

---

## Arquitectura

Pipeline de 3 pasos que **evalúa antes de generar**:

```
Brief  →  Paso 1: analyze_and_design()   →  DesignContext (colores, fuentes, layout)
                       ↓
          Paso 2: aesthetic_evaluate()   →  8 scores (umbral >= 85)
                  score < 85? → crítica → volver a Paso 1 (max 3 iteraciones)
                  score >= 85? → approved = True
                       ↓
          Paso 3: generate_code()        →  Componente React + CSS tokens
```

Ver `CLAUDE.md` para documentación técnica detallada.

---

## Deployment (Cloud Run)

```bash
bash setup_gcp.sh
```

Ver comentarios en `setup_gcp.sh` para los 10 pasos de configuración en GCP.
