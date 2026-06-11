#!/usr/bin/env bash
# ============================================================
# 03_deploy_frontend.sh — Build + deploy del frontend a Firebase Hosting
# ============================================================
# Uso:
#   bash deploy/03_deploy_frontend.sh
#
# Requiere:
#   - deploy/02_deploy_backend.sh ya corrido (genera deploy/backend_url.txt)
#   - Node.js / npm instalados
#   - Firebase CLI: npm install -g firebase-tools
#   - firebase login   (una sola vez, abre el navegador)
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"
PROJECT_ID="quimera-ai-prod"

BACKEND_URL_FILE="${SCRIPT_DIR}/backend_url.txt"
if [[ ! -f "${BACKEND_URL_FILE}" ]]; then
  echo "ERROR: no existe ${BACKEND_URL_FILE}. Corre primero deploy/02_deploy_backend.sh" >&2
  exit 1
fi
BACKEND_URL=$(cat "${BACKEND_URL_FILE}")
echo "Backend URL: ${BACKEND_URL}"

# --- Verificar Firebase CLI ---
if ! command -v firebase >/dev/null 2>&1; then
  echo "Firebase CLI no encontrado. Instalando (npm install -g firebase-tools)..."
  npm install -g firebase-tools
fi

# --- Verificar que el proyecto GCP tenga Firebase habilitado ---
echo ""
echo "Verificando proyecto Firebase..."
if ! firebase projects:list 2>/dev/null | grep -q "${PROJECT_ID}"; then
  echo "Habilitando Firebase en el proyecto ${PROJECT_ID}..."
  firebase projects:addfirebase "${PROJECT_ID}" || true
fi

# --- Configurar variable de entorno del frontend ---
echo ""
echo "Configurando NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL}"
cat > "${FRONTEND_DIR}/.env.production" <<EOF
NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL}
EOF

# --- Build del frontend (export estático) ---
echo ""
echo "================================================"
echo "  Build del frontend (next build → out/)"
echo "================================================"
cd "${FRONTEND_DIR}"
if [[ ! -d node_modules ]]; then
  npm install
fi
npm run build

# --- Deploy a Firebase Hosting ---
echo ""
echo "================================================"
echo "  Deploy a Firebase Hosting"
echo "================================================"
firebase deploy --only hosting --project "${PROJECT_ID}"

echo ""
echo "================================================"
echo "  ✅ Frontend desplegado."
echo "  Anota la URL de Hosting (https://${PROJECT_ID}.web.app)"
echo "  Siguiente paso: bash deploy/04_update_cors.sh <URL_DEL_FRONTEND>"
echo "================================================"
