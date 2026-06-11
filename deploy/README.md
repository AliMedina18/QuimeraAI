# Despliegue de Quimera AI a Google Cloud

Scripts listos para desplegar el stack completo (backend FastAPI en Cloud Run +
frontend Next.js en Firebase Hosting) en el proyecto `quimera-ai-prod`.

Ejecutar todo desde **Git Bash / Google Cloud SDK Shell** (con bash), parados en
la raíz del repo (`QuimeraAI/`).

## 0. Prerrequisitos (una sola vez)

```bash
# Autenticarte (si no lo has hecho ya)
gcloud auth login
gcloud config set project quimera-ai-prod

# Verificar que el billing esté activo en el proyecto
gcloud billing projects describe quimera-ai-prod
```

`backend/.env` debe existir con `GOOGLE_API_KEY`, `UNSPLASH_ACCESS_KEY`,
`SENDGRID_API_KEY`, etc. (ya lo tienes).

## 1. Infraestructura base (una sola vez)

```bash
bash deploy/01_setup_infra.sh
```

Hace, de forma idempotente (se puede re-correr sin romper nada):

- Habilita las APIs necesarias (Cloud Run, Artifact Registry, Firestore, Storage,
  Secret Manager, Cloud Build, Vertex AI, IAM).
- Crea el repo `quimera-repo` en Artifact Registry.
- Crea/actualiza los secrets `GOOGLE_API_KEY`, `UNSPLASH_ACCESS_KEY`,
  `SENDGRID_API_KEY` en Secret Manager (lee los valores de `backend/.env`).
- Crea la base de datos Firestore (modo nativo) si no existe.
- Crea el bucket `quimera-ai-prod-outputs` si no existe.
- Da permisos a la service account de Cloud Run (Secret Manager, Vertex AI,
  Firestore, el bucket).
- Genera `deploy/env.prod.yaml` con las variables de entorno de producción.

## 2. Backend → Cloud Run

```bash
bash deploy/02_deploy_backend.sh
```

Construye la imagen Docker con Cloud Build, la sube a Artifact Registry y
despliega `quimera-backend` en Cloud Run (región `us-central1`,
`--allow-unauthenticated`). Guarda la URL resultante en
`deploy/backend_url.txt`.

Verificar:

```bash
curl $(cat deploy/backend_url.txt)/health
curl $(cat deploy/backend_url.txt)/gemini-test
```

Vuelve a correr este script cada vez que quieras desplegar una nueva versión
del backend.

## 3. Frontend → Firebase Hosting

Requiere Firebase CLI (el script lo instala solo si falta) y una sesión de
Firebase:

```bash
firebase login   # una sola vez, abre el navegador
bash deploy/03_deploy_frontend.sh
```

Hace:

- Lee `deploy/backend_url.txt` y escribe `frontend/.env.production` con
  `NEXT_PUBLIC_BACKEND_URL`.
- `npm install` (si falta `node_modules`) + `npm run build` (export estático
  a `frontend/out/`, ya configurado con `output: "export"`).
- `firebase deploy --only hosting` al proyecto `quimera-ai-prod`.

La URL final será algo como `https://quimera-ai-prod.web.app`.

## 4. Restringir CORS del backend

Una vez tengas la URL del frontend:

```bash
bash deploy/04_update_cors.sh https://quimera-ai-prod.web.app https://quimera-ai-prod.firebaseapp.com
```

Esto actualiza `ALLOWED_ORIGINS` en Cloud Run (sin rebuild de imagen) para que
el backend solo acepte requests desde el frontend desplegado.

## Notas

- `backend/.gcloudignore` excluye `.env` y archivos locales del build, para que
  las claves no terminen dentro de la imagen Docker.
- Re-desplegar = volver a correr `02_deploy_backend.sh` y/o
  `03_deploy_frontend.sh`. `01_setup_infra.sh` solo hace falta una vez (o si
  cambian los secrets).
- Costos: Cloud Run escala a 0 (sin tráfico = sin costo de cómputo). Firestore,
  Storage y Firebase Hosting tienen capas gratuitas generosas. Vertex AI
  (Gemini) cobra por uso — revisa la consola de billing.
