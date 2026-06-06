#!/bin/bash
# ============================================================
# setup_gcp.sh — Configuración inicial de GCP para Quimera
# ============================================================
# Ejecutar PASO A PASO, no todo de corrido.
# Cada sección tiene un número. Corre una, verifica, luego la siguiente.
#
# Prerequisitos:
#   - gcloud CLI instalado: https://cloud.google.com/sdk/docs/install
#   - Cuenta de Google con créditos GCP
#   - git configurado
#
# Para ejecutar en Windows PowerShell:
#   bash setup_gcp.sh
# O copiar cada comando manualmente.
# ============================================================

set -e  # Detener el script si algún comando falla

PROJECT_ID="quimera-ai-prod"
REGION="us-central1"
SERVICE_NAME="quimera-backend"
REPO_NAME="quimera-repo"  # Nombre del repo en Artifact Registry
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

echo "================================================"
echo "  Quimera GCP Setup"
echo "  Project: ${PROJECT_ID}"
echo "  Region:  ${REGION}"
echo "================================================"


# ============================================================
# PASO 1 — Autenticación
# ============================================================
echo ""
echo "PASO 1: Autenticación en GCP"
echo "--------------------------------------------"

# Login interactivo (abre el navegador)
gcloud auth login

# Configurar el proyecto activo
gcloud config set project ${PROJECT_ID}

# Application Default Credentials: el SDK de Python las usa automáticamente
# en Cloud Run (no necesitas hacer esto en producción, solo en local)
gcloud auth application-default login

echo "✅ Autenticación completada"


# ============================================================
# PASO 2 — Crear el proyecto GCP
# ============================================================
# Nota: Si ya tienes el proyecto creado, salta este paso.
# Si el ID quimera-ai-prod ya está tomado, usa quimera-ai-prod-[tus-iniciales]
echo ""
echo "PASO 2: Crear proyecto GCP"
echo "--------------------------------------------"

gcloud projects create ${PROJECT_ID} \
    --name="Quimera AI" \
    --set-as-default

# Verificar que el proyecto se creó
gcloud projects describe ${PROJECT_ID}

echo "✅ Proyecto ${PROJECT_ID} creado"


# ============================================================
# PASO 3 — Vincular la cuenta de facturación
# ============================================================
# Necesitas vincular una cuenta de billing ANTES de habilitar APIs.
# Cloud Run, Vertex AI, etc. requieren billing habilitado.
echo ""
echo "PASO 3: Vincular cuenta de facturación"
echo "--------------------------------------------"
echo "👉 Listar cuentas de billing disponibles:"
gcloud billing accounts list

echo ""
echo "👉 Copiar el ACCOUNT_ID de arriba y pegarlo aquí:"
echo "   Formato: XXXXXX-XXXXXX-XXXXXX"
echo ""
# Descomentar y reemplazar BILLING_ACCOUNT_ID con tu ID real:
# BILLING_ACCOUNT_ID="XXXXXX-XXXXXX-XXXXXX"
# gcloud billing projects link ${PROJECT_ID} --billing-account=${BILLING_ACCOUNT_ID}

echo "⚠️  Recuerda: vincula la cuenta de billing antes de continuar con el PASO 4"


# ============================================================
# PASO 4 — Habilitar las APIs necesarias
# ============================================================
echo ""
echo "PASO 4: Habilitando APIs de GCP"
echo "--------------------------------------------"
# Por qué cada API:
#   aiplatform    → Vertex AI y Gemini (el motor de IA)
#   run           → Cloud Run (donde vive el backend)
#   firestore     → Base de datos NoSQL
#   storage       → Archivos generados (React, CSS, Markdown)
#   secretmanager → Guardar GOOGLE_API_KEY de forma segura
#   cloudbuild    → CI/CD automático desde GitHub
#   artifactregistry → Guardar imágenes Docker
#   iam           → Permisos entre servicios

gcloud services enable \
    aiplatform.googleapis.com \
    run.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    iam.googleapis.com

echo "✅ APIs habilitadas"


# ============================================================
# PASO 5 — Guardar GOOGLE_API_KEY en Secret Manager
# ============================================================
# Por qué Secret Manager en vez de variables de entorno directas:
#   - Las variables de entorno de Cloud Run son visibles en la consola
#   - Secret Manager cifra el valor y controla quién puede leerlo
#   - El log de auditoría registra cada acceso a la clave
echo ""
echo "PASO 5: Configurar Secret Manager"
echo "--------------------------------------------"
echo "👉 Obtén tu API Key de: https://aistudio.google.com/app/apikey"
echo ""

# Crear el secret (el valor se pide interactivamente para no dejarlo en el historial)
echo "Ingresa tu GOOGLE_API_KEY cuando se solicite:"
echo -n "" | gcloud secrets create GOOGLE_API_KEY \
    --replication-policy="automatic" \
    --data-file=-

# Alternativa: leer desde variable de entorno (más seguro que escribirlo directamente)
# echo -n "${GOOGLE_API_KEY_VALUE}" | gcloud secrets create GOOGLE_API_KEY --data-file=-

# Verificar que se creó
gcloud secrets describe GOOGLE_API_KEY

echo "✅ Secret GOOGLE_API_KEY creado"


# ============================================================
# PASO 6 — Crear repositorio en Artifact Registry
# ============================================================
# Artifact Registry es el registro de imágenes Docker de GCP.
# Es como Docker Hub pero privado y dentro de tu proyecto.
echo ""
echo "PASO 6: Crear Artifact Registry"
echo "--------------------------------------------"

gcloud artifacts repositories create ${REPO_NAME} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Imágenes Docker de Quimera AI"

# Configurar Docker para autenticarse con Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

echo "✅ Artifact Registry creado en ${REGION}"


# ============================================================
# PASO 7 — Primer build y push de la imagen Docker
# ============================================================
# Esto construye la imagen en tu máquina y la sube a Artifact Registry.
# El primer build tarda ~5 minutos (descarga dependencias Python).
# Los siguientes son más rápidos por el caché de Docker.
echo ""
echo "PASO 7: Build y push de imagen Docker"
echo "--------------------------------------------"

# Ir al directorio del backend
cd backend

# Construir la imagen
docker build -t ${IMAGE_NAME}:latest .

# Subir al Artifact Registry
docker push ${IMAGE_NAME}:latest

cd ..

echo "✅ Imagen ${IMAGE_NAME}:latest subida"


# ============================================================
# PASO 8 — Crear base de datos Firestore
# ============================================================
echo ""
echo "PASO 8: Inicializar Firestore"
echo "--------------------------------------------"

gcloud firestore databases create \
    --location=${REGION} \
    --type=firestore-native

echo "✅ Firestore creado en ${REGION}"


# ============================================================
# PASO 9 — Primer deploy a Cloud Run
# ============================================================
# Cloud Run es serverless: solo corre cuando hay requests.
# Se escala a 0 cuando no hay tráfico (sin costo).
# Se escala automáticamente cuando hay carga.
echo ""
echo "PASO 9: Deploy a Cloud Run"
echo "--------------------------------------------"

# Dar permisos al Cloud Run Service Account para leer el secret
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')
CLOUD_RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
    --member="serviceAccount:${CLOUD_RUN_SA}" \
    --role="roles/secretmanager.secretAccessor"

# Deploy
# --set-secrets: inyecta el secret como variable de entorno en el contenedor
# --allow-unauthenticated: el API es pública (ajustar en producción con IAM)
# --memory 512Mi: suficiente para FastAPI + Gemini SDK
# --timeout 300: los requests del pipeline pueden tardar hasta 45s
gcloud run deploy ${SERVICE_NAME} \
    --image=${IMAGE_NAME}:latest \
    --region=${REGION} \
    --platform=managed \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
    --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},ENVIRONMENT=production"

# Obtener la URL del servicio
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

echo "✅ Servicio desplegado en: ${SERVICE_URL}"
echo ""
echo "Verificar health check:"
echo "  curl ${SERVICE_URL}/health"
echo ""
echo "Verificar integración con Gemini:"
echo "  curl ${SERVICE_URL}/gemini-test"


# ============================================================
# PASO 10 — Configurar Cloud Build (CI/CD)
# ============================================================
# Cloud Build conecta GitHub con Cloud Run:
# cada push a main → build → push imagen → deploy automático.
echo ""
echo "PASO 10: Configurar Cloud Build"
echo "--------------------------------------------"
echo ""
echo "Este paso se configura en la consola web de GCP:"
echo ""
echo "1. Ir a: https://console.cloud.google.com/cloud-build/triggers"
echo "2. Click en 'Connect Repository'"
echo "3. Seleccionar GitHub y autorizar"
echo "4. Seleccionar: github.com/AliMedina18/QuimeraAI"
echo "5. Click en 'Create Trigger' con estas configuraciones:"
echo "   - Name: deploy-on-push-main"
echo "   - Event: Push to branch"
echo "   - Branch: ^main$"
echo "   - Configuration: cloudbuild.yaml (se crea abajo)"
echo ""

# Crear el archivo cloudbuild.yaml
cat > cloudbuild.yaml << 'EOF'
# cloudbuild.yaml — Pipeline de CI/CD de Quimera
# Cada push a main ejecuta estos pasos en orden:
steps:
  # Paso 1: Build de la imagen Docker
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/${_SERVICE_NAME}:${COMMIT_SHA}'
      - '-t'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/${_SERVICE_NAME}:latest'
      - './backend'
    id: 'build'

  # Paso 2: Push al Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/${_SERVICE_NAME}'
    id: 'push'
    waitFor: ['build']

  # Paso 3: Deploy a Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image=${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/${_SERVICE_NAME}:${COMMIT_SHA}'
      - '--region=${_REGION}'
      - '--platform=managed'
    id: 'deploy'
    waitFor: ['push']

# Variables con defaults (se pueden sobreescribir en el trigger de Cloud Build)
substitutions:
  _REGION: us-central1
  _SERVICE_NAME: quimera-backend
  _REPO_NAME: quimera-repo

# Imágenes que quedan registradas en Artifact Registry después del build
images:
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/${_SERVICE_NAME}:${COMMIT_SHA}'
  - '${_REGION}-docker.pkg.dev/${PROJECT_ID}/${_REPO_NAME}/${_SERVICE_NAME}:latest'

# Timeout del build completo (5 minutos es suficiente para este proyecto)
timeout: '600s'
EOF

echo "✅ cloudbuild.yaml creado"
echo ""
echo "=============================================="
echo "  SETUP COMPLETO"
echo "  Verificar endpoints:"
echo "  curl ${SERVICE_URL}/health"
echo "  curl ${SERVICE_URL}/gemini-test"
echo "=============================================="
