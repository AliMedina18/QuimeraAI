#!/usr/bin/env bash
# ============================================================
# 01_setup_infra.sh — Infraestructura base de GCP para Quimera
# ============================================================
# Ejecutar UNA VEZ desde la raíz del repo (o desde deploy/, detecta solo):
#   bash deploy/01_setup_infra.sh
#
# Requisitos:
#   - gcloud CLI autenticado: gcloud auth login
#   - gcloud config set project quimera-ai-prod
#   - backend/.env con GOOGLE_API_KEY, UNSPLASH_ACCESS_KEY, SENDGRID_API_KEY, etc.
#
# Es idempotente: se puede correr varias veces sin romper nada.
# ============================================================

set -euo pipefail

# --- Resolver rutas ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${ROOT_DIR}/backend/.env"

PROJECT_ID="quimera-ai-prod"
REGION="us-central1"
REPO_NAME="quimera-repo"
SERVICE_NAME="quimera-backend"
BUCKET_NAME="${PROJECT_ID}-outputs"

echo "================================================"
echo "  Quimera — Setup de infraestructura GCP"
echo "  Proyecto: ${PROJECT_ID}"
echo "  Región:   ${REGION}"
echo "================================================"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: no se encontró ${ENV_FILE}" >&2
  exit 1
fi

# Cargar variables del .env (sin imprimirlas)
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

# --- 0. Proyecto activo ---
gcloud config set project "${PROJECT_ID}" >/dev/null
echo "✅ Proyecto activo: ${PROJECT_ID}"

# --- 1. Habilitar APIs ---
echo ""
echo "Habilitando APIs..."
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

# --- 2. Artifact Registry ---
echo ""
echo "Artifact Registry..."
if gcloud artifacts repositories describe "${REPO_NAME}" --location="${REGION}" >/dev/null 2>&1; then
  echo "✅ Repo '${REPO_NAME}' ya existe"
else
  gcloud artifacts repositories create "${REPO_NAME}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Imágenes Docker de Quimera AI"
  echo "✅ Repo '${REPO_NAME}' creado"
fi
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet >/dev/null

# --- 3. Secret Manager ---
echo ""
echo "Secret Manager..."

create_or_update_secret() {
  local name="$1"
  local value="$2"
  if [[ -z "${value}" ]]; then
    echo "  - ${name}: vacío en .env, se omite"
    return
  fi
  if gcloud secrets describe "${name}" >/dev/null 2>&1; then
    printf '%s' "${value}" | gcloud secrets versions add "${name}" --data-file=- >/dev/null
    echo "  - ${name}: nueva versión añadida"
  else
    printf '%s' "${value}" | gcloud secrets create "${name}" \
      --replication-policy="automatic" --data-file=- >/dev/null
    echo "  - ${name}: secret creado"
  fi
}

create_or_update_secret "GOOGLE_API_KEY" "${GOOGLE_API_KEY:-}"
create_or_update_secret "UNSPLASH_ACCESS_KEY" "${UNSPLASH_ACCESS_KEY:-}"
create_or_update_secret "SENDGRID_API_KEY" "${SENDGRID_API_KEY:-}"
echo "✅ Secrets listos"

# --- 4. Firestore ---
echo ""
echo "Firestore..."
if gcloud firestore databases describe --database='(default)' >/dev/null 2>&1; then
  echo "✅ Base de datos Firestore '(default)' ya existe"
else
  gcloud firestore databases create --location="${REGION}" --type=firestore-native
  echo "✅ Firestore creado en ${REGION}"
fi

# --- 5. Cloud Storage bucket ---
echo ""
echo "Cloud Storage..."
if gcloud storage buckets describe "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
  echo "✅ Bucket gs://${BUCKET_NAME} ya existe"
else
  gcloud storage buckets create "gs://${BUCKET_NAME}" --location="${REGION}"
  echo "✅ Bucket gs://${BUCKET_NAME} creado"
fi

# --- 6. Permisos para la service account de Cloud Run ---
echo ""
echo "IAM..."
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')
RUN_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

for ROLE in roles/secretmanager.secretAccessor roles/aiplatform.user roles/datastore.user \
            roles/storage.objectViewer roles/logging.logWriter roles/artifactregistry.writer; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${RUN_SA}" \
    --role="${ROLE}" \
    --condition=None >/dev/null
done
echo "  - roles de proyecto asignados a ${RUN_SA}"
echo "    (incluye permisos para que Cloud Build pueda leer el código fuente y pushear imágenes)"

gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
  --member="serviceAccount:${RUN_SA}" \
  --role="roles/storage.objectAdmin" >/dev/null
echo "  - acceso al bucket ${BUCKET_NAME} concedido"
echo "✅ IAM listo"

# --- 7. Generar archivo de variables de entorno para el deploy ---
ENV_YAML="${SCRIPT_DIR}/env.prod.yaml"
cat > "${ENV_YAML}" <<EOF
GCP_PROJECT_ID: "${PROJECT_ID}"
GCP_LOCATION: "${REGION}"
GCS_BUCKET: "${BUCKET_NAME}"
ENVIRONMENT: "production"
USE_VERTEX_AI: "true"
QUIMERA_FROM_EMAIL: "${QUIMERA_FROM_EMAIL:-hola@quimera.ai}"
QUIMERA_FROM_NAME: "${QUIMERA_FROM_NAME:-Quimera AI}"
QUIMERA_APP_URL: "${QUIMERA_APP_URL:-http://localhost:3000}"
ALLOWED_ORIGINS: "*"
EOF
echo ""
echo "✅ ${ENV_YAML} generado"

echo ""
echo "================================================"
echo "  Infraestructura lista."
echo "  Siguiente paso: bash deploy/02_deploy_backend.sh"
echo "================================================"
