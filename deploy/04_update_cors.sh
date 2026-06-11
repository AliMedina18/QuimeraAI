#!/usr/bin/env bash
# ============================================================
# 04_update_cors.sh — Actualiza ALLOWED_ORIGINS del backend
# ============================================================
# Uso:
#   bash deploy/04_update_cors.sh https://quimera-ai-prod.web.app
#
# Restringe el CORS del backend a la(s) URL(s) reales del frontend
# y redespliega el servicio (sin rebuild de imagen).
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ID="quimera-ai-prod"
REGION="us-central1"
SERVICE_NAME="quimera-backend"

if [[ $# -lt 1 ]]; then
  echo "Uso: bash deploy/04_update_cors.sh <URL_FRONTEND_1> [URL_FRONTEND_2 ...]" >&2
  echo "Ejemplo: bash deploy/04_update_cors.sh https://quimera-ai-prod.web.app https://quimera-ai-prod.firebaseapp.com" >&2
  exit 1
fi

# Unir las URLs con comas
ORIGINS=$(IFS=,; echo "$*")

gcloud config set project "${PROJECT_ID}" >/dev/null

echo "Actualizando ALLOWED_ORIGINS=${ORIGINS} en ${SERVICE_NAME}..."

gcloud run services update "${SERVICE_NAME}" \
  --region="${REGION}" \
  --update-env-vars="^##^ALLOWED_ORIGINS=${ORIGINS}"

echo ""
echo "✅ CORS actualizado. Verifica con:"
echo "  curl -I -H \"Origin: ${1}\" \$(cat ${SCRIPT_DIR}/backend_url.txt)/health"
