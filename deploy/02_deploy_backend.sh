#!/usr/bin/env bash
# ============================================================
# 02_deploy_backend.sh — Build + deploy del backend a Cloud Run
# ============================================================
# Uso:
#   bash deploy/02_deploy_backend.sh
#
# Requiere haber corrido antes: deploy/01_setup_infra.sh
# (genera deploy/env.prod.yaml con las variables de entorno)
#
# Vuelve a ejecutarse cada vez que quieras desplegar una nueva versión
# del backend (build + push + deploy).
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

PROJECT_ID="quimera-ai-prod"
REGION="us-central1"
REPO_NAME="quimera-repo"
SERVICE_NAME="quimera-backend"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"
ENV_YAML="${SCRIPT_DIR}/env.prod.yaml"

if [[ ! -f "${ENV_YAML}" ]]; then
  echo "ERROR: no existe ${ENV_YAML}. Corre primero deploy/01_setup_infra.sh" >&2
  exit 1
fi

gcloud config set project "${PROJECT_ID}" >/dev/null

echo "================================================"
echo "  Build de imagen del backend (Cloud Build)"
echo "================================================"
gcloud builds submit "${ROOT_DIR}/backend" \
  --tag "${IMAGE}:latest" \
  --timeout=900s

echo ""
echo "================================================"
echo "  Deploy a Cloud Run: ${SERVICE_NAME}"
echo "================================================"

# Secrets disponibles (se omiten silenciosamente si no existen)
SECRETS=""
for s in GOOGLE_API_KEY UNSPLASH_ACCESS_KEY SENDGRID_API_KEY; do
  if gcloud secrets describe "${s}" >/dev/null 2>&1; then
    SECRETS+="${s}=${s}:latest,"
  fi
done
SECRETS="${SECRETS%,}"

DEPLOY_ARGS=(
  run deploy "${SERVICE_NAME}"
  --image="${IMAGE}:latest"
  --region="${REGION}"
  --platform=managed
  --allow-unauthenticated
  --memory=1Gi
  --cpu=1
  --timeout=300
  --min-instances=0
  --max-instances=10
  --env-vars-file="${ENV_YAML}"
)

if [[ -n "${SECRETS}" ]]; then
  DEPLOY_ARGS+=(--set-secrets="${SECRETS}")
fi

gcloud "${DEPLOY_ARGS[@]}"

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" --format='value(status.url)')

echo "${SERVICE_URL}" > "${SCRIPT_DIR}/backend_url.txt"

echo ""
echo "================================================"
echo "  ✅ Backend desplegado en: ${SERVICE_URL}"
echo "================================================"
echo ""
echo "Verificar:"
echo "  curl ${SERVICE_URL}/health"
echo "  curl ${SERVICE_URL}/gemini-test"
echo ""
echo "Siguiente paso: bash deploy/03_deploy_frontend.sh"
