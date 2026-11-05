#!/usr/bin/env bash
# ==============================================================================
# Andalusia AI Portfolio Dashboard — One-Click Production Deploy & Health Probe
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"
PORT=8055
WORKERS=4

echo "======================================================================"
echo "🚀 Starting Andalusia AI Portfolio & Analytics Production Deployment"
echo "======================================================================"

# ── 1. Idempotent Database Migration ───────────────────────────────────────────
echo "📦 Step 1: Running Idempotent Excel -> SQLite WAL Migration..."
cd "${PROJECT_ROOT}"
"${PROJECT_ROOT}/.venv/bin/python3" "${PROJECT_ROOT}/data/migration.py"

# ── 2. Build Frontend Production Assets ───────────────────────────────────────
echo "⚡ Step 2: Compiling & Bundling React 19 Frontend with Vite..."
cd "${FRONTEND_DIR}"
npm run build

# ── 3. Zero-Downtime Server Reload / Restart ──────────────────────────────────
echo "🔄 Step 3: Performing Process Supervisor Reload on Port ${PORT}..."
cd "${PROJECT_ROOT}"

# Find existing uvicorn parent process on port 8055
OLD_PID=$(ss -tlpn 2>/dev/null | grep ":${PORT} " | grep -o 'pid=[0-9]*' | head -n1 | cut -d'=' -f2 || true)

if [ -n "${OLD_PID}" ]; then
  echo "    [i] Found running Uvicorn process (PID: ${OLD_PID}). Restarting..."
  kill -TERM "${OLD_PID}" 2>/dev/null || true
  sleep 2
fi

echo "    [+] Launching 4-Worker Production Uvicorn Cluster..."
nohup "${PROJECT_ROOT}/.venv/bin/uvicorn" server:app \
  --app-dir "${PROJECT_ROOT}" \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --workers "${WORKERS}" \
  > "${PROJECT_ROOT}/server.log" 2>&1 &

NEW_SERVER_PID=$!
echo "    [+] Server started with PID: ${NEW_SERVER_PID}"

# ── 4. Health Probe Verification ──────────────────────────────────────────────
echo "🩺 Step 4: Probing Health & Integrity Endpoints..."
MAX_RETRIES=15
COUNTER=0
SUCCESS=0

while [ ${COUNTER} -lt ${MAX_RETRIES} ]; do
  sleep 1
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PORT}/health" || true)
  if [ "${HTTP_STATUS}" = "200" ]; then
    SUCCESS=1
    break
  fi
  COUNTER=$((COUNTER + 1))
  echo "    Waiting for server readiness... (${COUNTER}/${MAX_RETRIES})"
done

if [ ${SUCCESS} -eq 1 ]; then
  HEALTH_RESP=$(curl -s "http://127.0.0.1:${PORT}/health")
  echo "    [✓] Health Check PASSED: ${HEALTH_RESP}"
else
  echo "    [✗] Health Check FAILED. Check server.log:"
  tail -n 25 "${PROJECT_ROOT}/server.log"
  exit 1
fi

# ── 5. Output Access Links ────────────────────────────────────────────────────
LOCAL_IP="10.24.105.220"
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | grep -o 'https://[^"]*ngrok-free.dev' | head -n1 || echo "https://irksome-uncrystallisable-owen.ngrok-free.dev")

echo "======================================================================"
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "======================================================================"
echo "  • Internal Network URL : http://${LOCAL_IP}:${PORT}"
echo "  • Local Machine URL    : http://127.0.0.1:${PORT}"
echo "  • Public HTTPS URL     : ${NGROK_URL}"
echo "  • Health Endpoint      : http://127.0.0.1:${PORT}/health"
echo "  • Live WebSocket Push  : ws://${LOCAL_IP}:${PORT}/ws/live"
echo "======================================================================"

